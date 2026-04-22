# backend/agents/contract_expert.py

import json
import re  # Add this line to fix the error
from datetime import datetime
from backend.database.db_config import db
from backend.utils.llm_helper import LLMHelper

class ContractExpertAgent:
    """
    Agent 1: Knows everything about contracts
    - Answers questions about rules
    - Provides contract information to other agents
    """
    
    def __init__(self):
        self.name = "Contract Expert"
    
    async def answer_question(self, query, carrier=None):
        """Answer natural language questions about contracts"""
        context = ""
        
        if carrier:
            # Get rules for specific carrier
            rules = await self.get_rules_by_carrier(carrier)
            context = self.format_rules_for_context(rules, carrier)
        else:
            # Get rules for all carriers for comparison
            carriers = await db.fetch("SELECT id, name FROM carriers")
            for c in carriers:
                rules = await self.get_rules_by_carrier(c['name'])
                if rules:
                    context += self.format_rules_for_context(rules, c['name']) + "\n\n"
        
        if not context:
            return {
                "response": "I don't have any contract rules loaded yet. Please upload a contract first.",
                "agent": self.name,
                "context_used": None
            }
            
        # Use LLM to generate response based on context
        response = await LLMHelper.generate_response(query, context)
        
        return {
            "response": response,
            "agent": self.name,
            "context_used": context
        }
    
    async def get_rule(self, carrier, rule_type):
        """Get specific rule for other agents to use"""
        rule = await db.fetch_one("""
            SELECT r.* 
            FROM rules r
            JOIN contracts c ON r.contract_id = c.id
            JOIN carriers cr ON c.carrier_id = cr.id
            WHERE cr.name = $1 AND r.rule_type = $2
            ORDER BY r.created_at DESC LIMIT 1
        """, carrier, rule_type)
        return dict(rule) if rule else None
    
    async def get_rules_by_carrier(self, carrier):
        """Get all rules for a carrier"""
        rules = await db.fetch("""
            SELECT r.* 
            FROM rules r
            JOIN contracts c ON r.contract_id = c.id
            JOIN carriers cr ON c.carrier_id = cr.id
            WHERE cr.name = $1
        """, carrier)
        return [dict(rule) for rule in rules]
    
    def format_rules_for_context(self, rules, carrier):
        """Format rules into readable context for LLM"""
        if not rules:
            return f"No rules found for {carrier}."
            
        context = f"--- {carrier.upper()} CONTRACT RULES ---\n"
        for rule in rules:
            rule_type = rule['rule_type'].replace('_', ' ').title()
            rule_value = rule['rule_value']
            
            # Format nicely
            if 'usd' in rule['rule_type'] or rule['unit'] == 'dollars':
                formatted_value = f"${rule_value}"
            elif 'days' in rule['rule_type'] or rule['unit'] == 'days':
                formatted_value = f"{rule_value} days"
            elif rule['unit']:
                formatted_value = f"{rule_value} {rule['unit']}"
            else:
                formatted_value = rule_value
                
            context += f"- {rule_type}: {formatted_value}\n"
            
        return context
    
    async def extract_and_store_rules(self, contract_text, carrier, contract_id):
        """Extract rules using LLM and store in database"""
        
        print(f"🔍 Extracting rules from {carrier} contract...")
        
        # Use LLM to extract structured rules
        extracted = await LLMHelper.extract_rules_from_contract(contract_text, carrier)
        
        if not extracted:
            print("⚠️ No rules extracted, using fallback extraction")
            # Fallback: Use regex to extract rules manually
            extracted = self.fallback_extract_rules(contract_text, carrier)
            
        if not extracted:
            print("⚠️ Fallback extraction also failed. No rules to store.")
            return {}
        
        # Store each rule in database
        rules_count = 0
        for rule_type, value in extracted.items():
            if value and value != "null" and value != "":
                # Determine unit based on rule type
                unit = None
                if "days" in rule_type:
                    unit = "days"
                elif "usd" in rule_type or "penalty" in rule_type or "limit" in rule_type:
                    unit = "dollars"
                elif "minutes" in rule_type:
                    unit = "minutes"
                elif "lbs" in rule_type or "weight" in rule_type:
                    unit = "pounds"
                elif "dim" in rule_type:
                    unit = "factor"
                
                # Convert value to string for storage
                if isinstance(value, list):
                    rule_value = json.dumps(value)
                else:
                    rule_value = str(value)
                
                # Insert rule
                try:
                    await db.execute("""
                        INSERT INTO rules (contract_id, rule_type, rule_value, unit)
                        VALUES ($1, $2, $3, $4)
                    """, contract_id, rule_type, rule_value, unit)
                    rules_count += 1
                    print(f"  ✓ Stored rule: {rule_type} = {value}")
                except Exception as e:
                    print(f"  ✗ Error storing rule {rule_type}: {e}")
        
        print(f"✅ Successfully stored {rules_count} rules for {carrier}")
        return extracted

    def fallback_extract_rules(self, text, carrier):
        """Manual extraction using regex if LLM fails or hits ratelimits"""
        rules = {}
        
        # --- Standard Claims ---
        claim_match = re.search(r'(?:Standard|Delivery) Claims:?\s*(\d+)\s*(?:calendar|business)?\s*days', text, re.IGNORECASE)
        if claim_match:
            rules['claim_deadline_days'] = int(claim_match.group(1))
        
        # --- Inventory Claims (Amazon FBA) ---
        inv_claim_match = re.search(r'Inventory Claims:?\s*(\d+)\s*days', text, re.IGNORECASE)
        if inv_claim_match:
            rules['inventory_claim_days'] = int(inv_claim_match.group(1))
            
        rate_dispute_match = re.search(r'Rate Disputes:?\s*(\d+)\s*days', text, re.IGNORECASE)
        if rate_dispute_match:
            rules['overcharge_dispute_days'] = int(rate_dispute_match.group(1))
            
        fba_claim_match = re.search(r'FBA Claims:?\s*(\d+)\s*days', text, re.IGNORECASE)
        if fba_claim_match:
            rules['fba_claim_days'] = int(fba_claim_match.group(1))

        # --- Concealed damage ---
        concealed_match = re.search(r'Concealed Damage:?\s*(\d+)\s*days', text, re.IGNORECASE)
        if concealed_match:
            rules['concealed_damage_days'] = int(concealed_match.group(1))
            
        # --- Liability Limits ---
        liability_match = re.search(r'(?:Standard Liability|Standard Coverage):?\s*\$?(\d+)', text, re.IGNORECASE)
        if liability_match:
            rules['liability_limit_usd'] = int(liability_match.group(1))
            
        fba_liability = re.search(r'FBA Inventory:?.*?\$?(\d+)', text, re.IGNORECASE)
        if fba_liability:
            rules['fba_liability_limit_usd'] = int(fba_liability.group(1))

        # --- Operations & Restrictions ---
        pickup_match = re.search(r'Pickup Window:?\s*(\d+)\s*minutes', text, re.IGNORECASE)
        if pickup_match:
            rules['pickup_window_minutes'] = int(pickup_match.group(1))
            
        weight_match = re.search(r'Maximum Weight:?\s*(\d+)\s*lbs', text, re.IGNORECASE)
        if weight_match:
            rules['max_weight_lbs'] = int(weight_match.group(1))
            
        return rules