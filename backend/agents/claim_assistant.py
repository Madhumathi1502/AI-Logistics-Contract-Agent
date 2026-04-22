# backend/agents/claim_assistant.py

from backend.database.db_config import db
from datetime import datetime
from .contract_expert import ContractExpertAgent
from .deadline_monitor import DeadlineMonitorAgent
import json

class ClaimAssistantAgent:
    """
    Agent 3: Helps users file claims
    - Guides through claim process
    - Auto-fills forms
    - Tracks claim status
    """
    
    def __init__(self):
        self.name = "Claim Assistant"
        self.contract_expert = ContractExpertAgent()
        self.deadline_monitor = DeadlineMonitorAgent()
    
    async def start_claim(self, shipment_id, user_input=None):
        """Initialize claim filing process"""
        
        # Get shipment details
        shipment = await db.fetch_one("""
            SELECT s.*, c.name as carrier_name 
            FROM shipments s
            JOIN carriers c ON s.carrier_id = c.id
            WHERE s.id = $1
        """, shipment_id)
        
        if not shipment:
            return {"error": "Shipment not found"}
        
        # Check if within deadline
        deadline = await db.fetch_one("""
            SELECT * FROM deadlines 
            WHERE shipment_id = $1 AND deadline_type = 'claim_filing'
        """, shipment_id)
        
        if deadline:
            days_left = (deadline['deadline_date'] - datetime.now().date()).days
            if days_left < 0:
                return {
                    "error": "deadline_missed",
                    "message": f"Claim deadline was {abs(days_left)} days ago. Cannot file.",
                    "shipment": dict(shipment)
                }
        
        # Get required documents from contract
        rules = await self.contract_expert.get_rules_by_carrier(shipment['carrier_name'])
        
        required_docs = ["Proof of value (invoice)"]
        
        # Add carrier-specific requirements
        for rule in rules:
            if rule['rule_type'] == 'fragile_packaging':
                required_docs.append("Packaging photos")
            elif rule['rule_type'] == 'special_handling':
                required_docs.append("Special handling documentation")
        
        # Create draft claim
        claim_id = await db.fetch_one("""
            INSERT INTO claims (shipment_id, amount, status, documents)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """, shipment_id, shipment['value'], 'draft', json.dumps({"required": required_docs}))
        
        # Pre-fill claim form
        claim_form = {
            "claim_id": claim_id['id'],
            "tracking_number": shipment['tracking_number'],
            "carrier": shipment['carrier_name'],
            "ship_date": str(shipment['ship_date']),
            "delivery_date": str(shipment['delivery_date']),
            "value": float(shipment['value']),
            "contents": shipment['contents'],
            "required_documents": required_docs,
            "uploaded_documents": [],
            "days_remaining": days_left if deadline else "Unknown"
        }
        
        return {
            "status": "claim_started",
            "message": f"I've started a claim for {shipment['tracking_number']}",
            "claim_form": claim_form,
            "next_steps": [
                "Tell me what type of damage occurred",
                "Upload required documents",
                "Review and submit"
            ]
        }
    
    async def add_document(self, claim_id, document_type, file_path):
        """Add document to claim"""
        
        # Get current claim
        claim = await db.fetch_one("SELECT * FROM claims WHERE id = $1", claim_id)
        
        if not claim:
            return {"error": "Claim not found"}
        
        # Update documents
        documents = claim['documents'] or {}
        if 'uploaded' not in documents:
            documents['uploaded'] = []
        
        documents['uploaded'].append({
            "type": document_type,
            "path": file_path,
            "uploaded_at": str(datetime.now())
        })
        
        # Check if all required docs uploaded
        required = documents.get('required', [])
        uploaded_types = [d['type'] for d in documents.get('uploaded', [])]
        
        missing = [doc for doc in required if doc not in uploaded_types]
        
        await db.execute("""
            UPDATE claims SET documents = $1 WHERE id = $2
        """, json.dumps(documents), claim_id)
        
        return {
            "status": "document_added",
            "missing_documents": missing,
            "all_documents_uploaded": len(missing) == 0
        }
    
    async def submit_claim(self, claim_id, damage_description):
        """Submit completed claim"""
        
        claim = await db.fetch_one("SELECT * FROM claims WHERE id = $1", claim_id)
        shipment = await db.fetch_one("SELECT * FROM shipments WHERE id = $1", claim['shipment_id'])
        
        # Generate claim number
        claim_number = f"CLM{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update claim status
        await db.execute("""
            UPDATE claims 
            SET status = 'filed', claim_number = $1, filed_date = $2
            WHERE id = $3
        """, claim_number, datetime.now().date(), claim_id)
        
        return {
            "status": "submitted",
            "claim_number": claim_number,
            "message": f"Claim {claim_number} submitted successfully to {shipment['carrier_name']}",
            "next_steps": [
                "Claim is now being processed by carrier",
                "Typical response time: 5-10 business days",
                "I'll notify you when status changes"
            ]
        }
    
    async def get_claim_status(self, claim_id):
        """Get current claim status"""
        
        claim = await db.fetch_one("""
            SELECT c.*, s.tracking_number, s.carrier_id, cr.name as carrier_name
            FROM claims c
            JOIN shipments s ON c.shipment_id = s.id
            JOIN carriers cr ON s.carrier_id = cr.id
            WHERE c.id = $1
        """, claim_id)
        
        return dict(claim)