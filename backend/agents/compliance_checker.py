# backend/agents/compliance_checker.py

from backend.database.db_config import db
from .contract_expert import ContractExpertAgent

class ComplianceCheckerAgent:
    """
    Agent 4: Checks shipments for compliance before shipping
    - Verifies packaging meets carrier rules
    - Flags potential issues
    - Prevents claim denials
    """
    
    def __init__(self):
        self.name = "Compliance Checker"
        self.contract_expert = ContractExpertAgent()
    
    async def check_shipment_before_shipping(self, shipment_data):
        """Check if shipment meets carrier requirements before shipping"""
        
        carrier = shipment_data.get('carrier')
        contents = shipment_data.get('contents', '')
        special_handling = shipment_data.get('special_handling', [])
        packaging_used = shipment_data.get('packaging_used', [])
        
        # Get relevant rules from contract
        rules = await self.contract_expert.get_rules_by_carrier(carrier)
        
        issues = []
        warnings = []
        
        for rule in rules:
            rule_type = rule['rule_type']
            rule_value = rule['rule_value']
            
            # Check fragile items
            if 'fragile' in contents.lower() or 'fragile' in str(special_handling).lower():
                if rule_type == 'fragile_packaging' and rule_value:
                    required = str(rule_value).lower()
                    # Check if required packaging is used
                    compliant = False
                    for packaging in packaging_used:
                        if required in packaging.lower():
                            compliant = True
                            break
                    
                    if not compliant:
                        issues.append({
                            "type": "packaging",
                            "severity": "critical",
                            "rule": f"Fragile items require: {rule_value}",
                            "current": f"Using: {', '.join(packaging_used) if packaging_used else 'No special packaging'}"
                        })
            
            # Check high value items
            value = shipment_data.get('value', 0)
            if value > 1000 and rule_type == 'liability_limit_usd' and rule_value:
                try:
                    limit = int(float(rule_value))
                    if value > limit:
                        warnings.append({
                            "type": "value",
                            "severity": "warning",
                            "rule": f"Liability limit: ${limit}",
                            "current": f"Item value: ${value}",
                            "suggestion": "Consider declaring higher value or purchasing additional insurance"
                        })
                except (ValueError, TypeError):
                    pass
        
        # Determine overall status
        if issues:
            status = "blocked"
            message = "❌ Shipment cannot proceed - critical compliance issues"
        elif warnings:
            status = "warning"
            message = "⚠️ Shipment can proceed but has warnings"
        else:
            status = "compliant"
            message = "✅ Shipment meets all carrier requirements"
        
        return {
            "status": status,
            "message": message,
            "issues": issues,
            "warnings": warnings,
            "shipment_id": shipment_data.get('id', 'new'),
            "carrier": carrier
        }
    
    async def check_packaging(self, shipment_id, packaging_photos=None):
        """Verify packaging from photos (simplified for hackathon)"""
        
        # In a real system, this would use image recognition
        # For hackathon, we'll simulate based on shipment data
        
        shipment = await db.fetch_one("SELECT * FROM shipments WHERE id = $1", shipment_id)
        
        # Simulate packaging check
        issues = []
        
        # Check if fragile items need special packaging
        if 'fragile' in shipment['contents'].lower():
            issues.append({
                "check": "Fragile item packaging",
                "status": "manual_review_needed",
                "message": "Please ensure foam wrap and FRAGILE labels are applied"
            })
        
        return {
            "shipment_id": shipment_id,
            "packaging_check": "completed",
            "issues": issues,
            "requires_manual_review": len(issues) > 0
        }
    
    async def get_compliance_report(self, shipment_id):
        """Generate compliance report for a shipment"""
        
        shipment = await db.fetch_one("""
            SELECT s.*, c.name as carrier_name 
            FROM shipments s
            JOIN carriers c ON s.carrier_id = c.id
            WHERE s.id = $1
        """, shipment_id)
        
        # Get all rules for this carrier
        rules = await self.contract_expert.get_rules_by_carrier(shipment['carrier_name'])
        
        report = {
            "shipment": dict(shipment),
            "compliance_status": "unknown",
            "rules_check": []
        }
        
        # Check each rule (simplified for demo)
        for rule in rules:
            report["rules_check"].append({
                "rule": rule['rule_type'],
                "requirement": rule['rule_value'],
                "status": "pending_review",
                "compliant": None
            })
        
        return report