# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from backend.database.db_config import db
from backend.database.models import Shipment, Claim
from backend.utils.pdf_processor import PDFProcessor
from backend.utils.llm_helper import LLMHelper
from backend.agents.contract_expert import ContractExpertAgent
from backend.agents.deadline_monitor import DeadlineMonitorAgent
from backend.agents.claim_assistant import ClaimAssistantAgent
from backend.agents.compliance_checker import ComplianceCheckerAgent

app = FastAPI(title="ContractIQ API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
contract_expert = ContractExpertAgent()
deadline_monitor = DeadlineMonitorAgent()
claim_assistant = ClaimAssistantAgent()
compliance_checker = ComplianceCheckerAgent()

# Request/Response models
class ChatRequest(BaseModel):
    query: str
    carrier: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: str
    context_used: Optional[str]

class ShipmentCreateRequest(BaseModel):
    tracking_number: str
    carrier: str
    ship_date: str
    delivery_date: Optional[str] = None
    value: float
    contents: str
    special_handling: List[str] = []

class ClaimStartRequest(BaseModel):
    shipment_id: int
    damage_description: Optional[str] = None

# Startup event
@app.on_event("startup")
async def startup():
    await db.connect()
    print("🚀 ContractIQ API started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# Health check
@app.get("/")
async def root():
    return {"message": "ContractIQ API is running", "status": "healthy"}

# === CONTRACT ENDPOINTS ===
@app.post("/api/contracts/upload")
async def upload_contract(
    file: UploadFile = File(...),
    carrier: str = Form(...),
    contract_name: str = Form(...)
):
    """Upload and process a carrier contract PDF"""
    
    # Read PDF
    pdf_content = await file.read()
    
    # Extract text
    text = PDFProcessor.extract_text_from_pdf(pdf_content)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    # Get or create carrier
    carrier_result = await db.fetch_one(
        "SELECT id FROM carriers WHERE name = $1", carrier
    )
    
    if carrier_result:
        carrier_id = carrier_result['id']
    else:
        carrier_id = await db.fetch_one(
            "INSERT INTO carriers (name) VALUES ($1) RETURNING id", carrier
        )
        carrier_id = carrier_id['id']
    
    # Store contract
    contract_id = await db.fetch_one("""
        INSERT INTO contracts (carrier_id, contract_name, document_text, effective_date, expiry_date)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """, carrier_id, contract_name, text, datetime.now().date(), datetime.now().date().replace(year=datetime.now().year+1))
    
    # Extract and store rules using Contract Expert Agent
    rules = await contract_expert.extract_and_store_rules(text, carrier, contract_id['id'])
    
    # NEW FEATURE: Attempt to extract Sample Shipments or Claims directly from the Contract text
    try:
        shipment_data = await LLMHelper.extract_shipment_details(text)
        if shipment_data and shipment_data.get('tracking_number'):
            ship_date_obj = datetime.strptime(shipment_data.get('ship_date', ''), "%Y-%m-%d").date() if shipment_data.get('ship_date') else None
            delivery_date_obj = datetime.strptime(shipment_data.get('delivery_date', ''), "%Y-%m-%d").date() if shipment_data.get('delivery_date') else None
            
            shipment_id_record = await db.fetch_one("""
                INSERT INTO shipments 
                (tracking_number, carrier_id, ship_date, delivery_date, value, contents, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
            """, shipment_data.get('tracking_number'), carrier_id, ship_date_obj, delivery_date_obj,
                float(shipment_data.get('value', 0) or 0), str(shipment_data.get('contents', 'Document Extraction')), 
                "delivered" if delivery_date_obj else "in_transit")
            
            shipment_id = shipment_id_record['id']
            
            # Create deadline if delivered
            if delivery_date_obj:
                await deadline_monitor.process_new_shipment(
                    shipment_id, shipment_data['tracking_number'], carrier, shipment_data['delivery_date']
                )
                
            # Attempt Claim extraction if we found a shipment
            claim_data = await LLMHelper.extract_claim_details(text)
            if claim_data and claim_data.get('damage_description'):
                await db.fetch_one("""
                    INSERT INTO claims
                    (shipment_id, tracking_number, date_filed, status, requested_amount, damage_description)
                    VALUES ($1, $2, CURRENT_DATE, 'draft', $3, $4)
                    RETURNING id
                """, shipment_id, shipment_data.get('tracking_number'), 
                float(claim_data.get('estimated_value', 0) or 0), 
                str(claim_data.get('damage_description')))
                
    except Exception as e:
        print(f"Bonus extraction failed: {e}")

    return {
        "status": "success",
        "contract_id": contract_id['id'],
        "carrier": carrier,
        "rules_extracted": len(rules),
        "rules": rules,
        "bonus_extraction": "Checked for inline shipments/claims."
    }

@app.get("/api/contracts")
async def get_contracts():
    """Get all contracts"""
    contracts = await db.fetch("""
        SELECT c.*, cr.name as carrier_name 
        FROM contracts c
        JOIN carriers cr ON c.carrier_id = cr.id
        ORDER BY c.created_at DESC
    """)
    return [dict(contract) for contract in contracts]

@app.delete("/api/contracts/{contract_id}")
async def delete_contract(contract_id: int):
    """Delete a contract and its associated rules"""
    try:
        # Delete rules first due to foreign key constraint
        await db.execute("DELETE FROM rules WHERE contract_id = $1", contract_id)
        # Delete contract
        result = await db.execute("DELETE FROM contracts WHERE id = $1", contract_id)
        
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Contract not found")
            
        return {"status": "success", "message": "Contract deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting contract: {e}")

@app.delete("/api/contracts")
async def delete_all_contracts():
    """Delete all contracts and clear demo state"""
    try:
        # Delete dependent operational data first
        await db.execute("DELETE FROM claims")
        await db.execute("DELETE FROM deadlines")
        await db.execute("DELETE FROM shipments")
        # Then delete rule and contract data
        await db.execute("DELETE FROM rules")
        await db.execute("DELETE FROM contracts")
        return {"status": "success", "message": "All data cleared successfully for demo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all contracts: {e}")

@app.get("/api/contracts/{contract_id}/rules")
async def get_contract_rules(contract_id: int):
    """Get rules for a specific contract"""
    rules = await db.fetch("SELECT * FROM rules WHERE contract_id = $1 ORDER BY rule_type", contract_id)
    return [dict(rule) for rule in rules]

# === CHAT ENDPOINT ===
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with Contract Expert Agent"""
    
    response = await contract_expert.answer_question(
        query=request.query,
        carrier=request.carrier
    )
    
    return ChatResponse(
        response=response["response"],
        agent=response["agent"],
        context_used=response.get("context_used")
    )

# === SHIPMENTS ENDPOINTS ===
@app.post("/api/shipments/extract")
async def extract_shipment_data(file: UploadFile = File(...)):
    """Extract shipment data from an uploaded PDF (label/invoice)"""
    pdf_content = await file.read()
    text = PDFProcessor.extract_text_from_pdf(pdf_content)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from document")
        
    extracted_data = await LLMHelper.extract_shipment_details(text)
    
    if not extracted_data:
        raise HTTPException(status_code=500, detail="Failed to analyze document")
        
    return extracted_data

@app.post("/api/shipments")
async def create_shipment(shipment: ShipmentCreateRequest):
    """Create a new shipment"""
    
    # Get carrier ID
    carrier = await db.fetch_one(
        "SELECT id FROM carriers WHERE name = $1", shipment.carrier
    )
    
    if not carrier:
        # Auto-create carrier if not exists
        carrier = await db.fetch_one(
            "INSERT INTO carriers (name) VALUES ($1) RETURNING id", shipment.carrier
        )
        
    # Convert string dates to datetime.date for asyncpg
    ship_date_obj = datetime.strptime(shipment.ship_date, "%Y-%m-%d").date() if shipment.ship_date else None
    delivery_date_obj = datetime.strptime(shipment.delivery_date, "%Y-%m-%d").date() if shipment.delivery_date else None
    
    # Insert shipment
    shipment_id = await db.fetch_one("""
        INSERT INTO shipments 
        (tracking_number, carrier_id, ship_date, delivery_date, value, contents, special_handling, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
    """, shipment.tracking_number, carrier['id'], ship_date_obj, 
        delivery_date_obj, shipment.value, shipment.contents,
        shipment.special_handling, "in_transit" if not delivery_date_obj else "delivered")
    
    # If delivered, create deadline
    if delivery_date_obj:
        await deadline_monitor.process_new_shipment(
            shipment_id['id'], 
            shipment.tracking_number,
            shipment.carrier,
            shipment.delivery_date  # Keep string for the deadline monitor agent
        )
    
    return {
        "status": "created",
        "shipment_id": shipment_id['id'],
        "tracking": shipment.tracking_number
    }

@app.get("/api/shipments")
async def get_shipments(status: Optional[str] = None):
    """Get all shipments, optionally filtered by status"""
    
    if status:
        shipments = await db.fetch(
            "SELECT * FROM shipments WHERE status = $1 ORDER BY created_at DESC", status
        )
    else:
        shipments = await db.fetch("SELECT * FROM shipments ORDER BY created_at DESC")
    
    return [dict(s) for s in shipments]

@app.get("/api/shipments/{shipment_id}")
async def get_shipment(shipment_id: int):
    """Get single shipment by ID"""
    
    shipment = await db.fetch_one("SELECT * FROM shipments WHERE id = $1", shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    return dict(shipment)

# === DEADLINE ENDPOINTS ===
@app.get("/api/deadlines")
async def get_deadlines(days: int = 7):
    """Get upcoming deadlines"""
    
    deadlines = await deadline_monitor.get_upcoming_deadlines(days)
    return [dict(d) for d in deadlines]

@app.get("/api/alerts")
async def get_alerts():
    """Get dashboard alerts"""
    
    return await deadline_monitor.get_dashboard_alerts()

@app.post("/api/deadlines/check")
async def check_deadlines():
    """Manually trigger deadline check"""
    
    alerts = await deadline_monitor.check_all_deadlines()
    return {"alerts_sent": len(alerts), "alerts": alerts}

# === CLAIM ENDPOINTS ===
@app.post("/api/claims/extract")
async def extract_claim_data(file: UploadFile = File(...)):
    """Extract claim data from an uploaded PDF (damage report/estimate)"""
    pdf_content = await file.read()
    text = PDFProcessor.extract_text_from_pdf(pdf_content)
    
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from document")
        
    extracted_data = await LLMHelper.extract_claim_details(text)
    
    if not extracted_data:
        raise HTTPException(status_code=500, detail="Failed to analyze document")
        
    return extracted_data

@app.post("/api/claims/start")
async def start_claim(request: ClaimStartRequest):
    """Start a new claim"""
    
    result = await claim_assistant.start_claim(
        shipment_id=request.shipment_id,
        user_input=request.damage_description
    )
    
    return result

@app.post("/api/claims/{claim_id}/documents")
async def add_claim_document(
    claim_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Add document to claim"""
    
    # Save file (simplified - in real app, save to storage)
    file_content = await file.read()
    file_path = f"data/claims/{claim_id}_{file.filename}"
    
    # For hackathon, we'll just simulate saving
    result = await claim_assistant.add_document(
        claim_id=claim_id,
        document_type=document_type,
        file_path=file_path
    )
    
    return result

@app.post("/api/claims/{claim_id}/submit")
async def submit_claim(claim_id: int, damage_description: str = Form(...)):
    """Submit completed claim"""
    
    result = await claim_assistant.submit_claim(claim_id, damage_description)
    return result

@app.get("/api/claims")
async def get_claims():
    """Get all claims"""
    
    claims = await db.fetch("SELECT * FROM claims ORDER BY created_at DESC")
    return [dict(c) for c in claims]

@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: int):
    """Get single claim"""
    
    result = await claim_assistant.get_claim_status(claim_id)
    return result

# === COMPLIANCE ENDPOINTS ===
@app.post("/api/compliance/check")
async def check_compliance(shipment_data: dict):
    """Check shipment compliance before shipping"""
    
    result = await compliance_checker.check_shipment_before_shipping(shipment_data)
    return result

@app.get("/api/compliance/report/{shipment_id}")
async def get_compliance_report(shipment_id: int):
    """Get compliance report for shipment"""
    
    result = await compliance_checker.get_compliance_report(shipment_id)
    return result

# === DASHBOARD ENDPOINT ===
@app.get("/api/dashboard")
async def get_dashboard():
    """Get all data for dashboard"""
    
    # Get counts
    shipments = await db.fetch("SELECT COUNT(*) FROM shipments")
    pending_claims = await db.fetch("SELECT COUNT(*) FROM claims WHERE status = 'pending'")
    active_deadlines = await db.fetch("SELECT COUNT(*) FROM deadlines WHERE status = 'pending'")
    
    # Get alerts
    alerts = await deadline_monitor.get_dashboard_alerts()
    
    # Get recent shipments
    recent = await db.fetch("SELECT * FROM shipments ORDER BY created_at DESC LIMIT 5")
    
    return {
        "stats": {
            "total_shipments": shipments[0]['count'],
            "pending_claims": pending_claims[0]['count'],
            "active_deadlines": active_deadlines[0]['count']
        },
        "alerts": alerts,
        "recent_shipments": [dict(r) for r in recent]
    }