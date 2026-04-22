# backend/agents/deadline_monitor.py

from backend.database.db_config import db
from datetime import datetime, timedelta
from .contract_expert import ContractExpertAgent

class DeadlineMonitorAgent:
    """
    Agent 2: Tracks all deadlines and sends alerts
    - Calculates deadlines for each shipment
    - Sends proactive alerts
    - Escalates missed deadlines
    """
    
    def __init__(self):
        self.name = "Deadline Monitor"
        self.contract_expert = ContractExpertAgent()
    
    async def process_new_shipment(self, shipment_id, tracking_number, carrier, delivery_date):
        """When shipment is delivered, calculate and store deadlines"""
        
        if not delivery_date:
            return {"status": "no_delivery_date", "message": "Shipment not yet delivered"}
        
        # Get claim deadline rule from contract expert
        rule = await self.contract_expert.get_rule(carrier, "claim_deadline_days")
        
        if not rule:
            return {"status": "no_rule", "message": f"No claim deadline rule found for {carrier}"}
        
        # Calculate deadline
        try:
            # Extract only digits in case LLM returns something like '30 days'
            digits = ''.join(filter(str.isdigit, str(rule['rule_value'])))
            claim_days = int(digits) if digits else 30 # fallback to 30
        except Exception:
            claim_days = 30
            
        delivery = datetime.strptime(delivery_date, '%Y-%m-%d')
        deadline = delivery + timedelta(days=claim_days)
        
        # Store deadline in database
        deadline_id = await db.fetch_one("""
            INSERT INTO deadlines (shipment_id, rule_id, deadline_date, deadline_type, days_remaining, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """, shipment_id, rule['id'], deadline.date(), "claim_filing", claim_days, "pending")
        
        return {
            "status": "deadline_created",
            "shipment_id": shipment_id,
            "deadline_date": deadline.date(),
            "days_remaining": claim_days,
            "deadline_id": deadline_id['id']
        }
    
    async def check_all_deadlines(self):
        """Background task: Check all pending deadlines and send alerts"""
        
        # Get all pending deadlines
        deadlines = await db.fetch("""
            SELECT d.*, s.tracking_number, s.value, c.name as carrier_name
            FROM deadlines d
            JOIN shipments s ON d.shipment_id = s.id
            JOIN carriers c ON s.carrier_id = c.id
            WHERE d.status = 'pending' AND d.alert_sent = FALSE
        """)
        
        alerts = []
        today = datetime.now().date()
        
        for deadline in deadlines:
            days_left = (deadline['deadline_date'] - today).days
            
            # Update days remaining
            await db.execute("""
                UPDATE deadlines SET days_remaining = $1 WHERE id = $2
            """, days_left, deadline['id'])
            
            # Determine alert type based on days left
            if days_left <= 1 and days_left >= 0:
                # CRITICAL - send immediately
                alert = {
                    "type": "critical",
                    "title": "🔴 DEADLINE TOMORROW!",
                    "message": f"Claim for {deadline['tracking_number']} due tomorrow! Value: ${deadline['value']}",
                    "shipment_id": deadline['shipment_id'],
                    "deadline_id": deadline['id'],
                    "days_left": days_left
                }
                alerts.append(alert)
                await self.mark_alert_sent(deadline['id'])
                
            elif days_left == 3:
                # WARNING - 3 days left
                alert = {
                    "type": "warning",
                    "title": "🟡 3 Days Remaining",
                    "message": f"Claim for {deadline['tracking_number']} due in 3 days",
                    "shipment_id": deadline['shipment_id'],
                    "deadline_id": deadline['id'],
                    "days_left": days_left
                }
                alerts.append(alert)
                await self.mark_alert_sent(deadline['id'])
            
            elif days_left < 0:
                # MISSED - deadline passed
                await db.execute("""
                    UPDATE deadlines SET status = 'missed' WHERE id = $1
                """, deadline['id'])
                
                alert = {
                    "type": "missed",
                    "title": "❌ DEADLINE MISSED",
                    "message": f"Claim for {deadline['tracking_number']} missed! Potential loss: ${deadline['value']}",
                    "shipment_id": deadline['shipment_id'],
                    "deadline_id": deadline['id'],
                    "days_late": abs(days_left)
                }
                alerts.append(alert)
        
        return alerts
    
    async def mark_alert_sent(self, deadline_id):
        """Mark that alert has been sent for this deadline"""
        await db.execute("UPDATE deadlines SET alert_sent = TRUE WHERE id = $1", deadline_id)
    
    async def get_upcoming_deadlines(self, days=90):
        """Get all deadlines up to X days in the future, including past ones"""
        today = datetime.now().date()
        future = today + timedelta(days=days)
        
        deadlines = await db.fetch("""
            SELECT d.*, s.tracking_number, s.value, c.name as carrier_name
            FROM deadlines d
            JOIN shipments s ON d.shipment_id = s.id
            JOIN carriers c ON s.carrier_id = c.id
            WHERE d.deadline_date <= $1
            ORDER BY d.deadline_date ASC
        """, future)
        
        return deadlines
    
    async def get_dashboard_alerts(self):
        """Get formatted alerts for dashboard"""
        alerts = await self.check_all_deadlines()
        
        # Count by type
        stats = {
            "critical": len([a for a in alerts if a['type'] == 'critical']),
            "warning": len([a for a in alerts if a['type'] == 'warning']),
            "missed": len([a for a in alerts if a['type'] == 'missed'])
        }
        
        return {
            "alerts": alerts,
            "stats": stats
        }