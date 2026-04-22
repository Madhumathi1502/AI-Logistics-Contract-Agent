# backend/utils/llm_helper.py

from google import genai
from google.genai import types
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Uses GEMINI_API_KEY from environment natively
client = genai.Client()

class LLMHelper:
    @staticmethod
    async def extract_rules_from_contract(contract_text, carrier):
        """Use LLM to extract structured rules from contract text"""
        
        # Clean and prepare the text (limit to avoid token issues)
        clean_text = contract_text[:10000]  # Increased token limit for Gemini
        
        prompt = f"""
        Extract all relevant rules, deadlines, limits, requirements, and penalties from this {carrier} shipping contract.
        Return as VALID JSON ONLY, where keys are descriptive rule names (snake_case) and values are the specific details.
        
        Make sure to include these standard rules if they exist:
        - claim_deadline_days (integer)
        - concealed_damage_days (integer)
        - loss_claim_days (integer)
        - overcharge_dispute_days (integer)
        - liability_limit_usd (integer)
        - declared_value_max_usd (integer)
        - fragile_packaging (string)
        - prohibited_items (array of strings)
        - max_weight_lbs (integer)
        - dim_factor (integer)
        - pickup_window_minutes (integer)
        - late_pickup_penalty_usd (integer)
        - delivery_commitments (string)

        AND crucially, include ANY OTHER carrier-specific rules, penalties, or restrictions you find in the contract as additional key-value pairs.
        
        Contract text:
        {clean_text}
        
        Return ONLY valid JSON format. A single flat dictionary where keys are the rule names and values are the rule values. No markdown blocks, no other text.
        """
        
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            
            # Get the response content
            content = response.text
            
            # Parse JSON
            rules = json.loads(content)
            print(f"✅ Extracted {len(rules)} rules from {carrier} contract")
            return dict(rules)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            try:
                # Fallback fuzzy clean: try to find anything between { and }
                if content and "{" in content and "}" in content:
                    fuzzy_json = "{" + content.split("{", 1)[1].rsplit("}", 1)[0] + "}"
                    rules = json.loads(fuzzy_json)
                    return dict(rules)
            except Exception:
                pass
            print(f"Raw response: {content[:200] if 'content' in locals() else 'None'}...")
            return None # Return None to trigger fallback
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"⚠️ API Rate Limit / Quota Exceeded (429). Triggering fallback extraction.")
            else:
                print(f"❌ Error extracting rules: {e}")
            return None # Return None to trigger fallback
    
    @staticmethod
    async def generate_response(query, context, shipment_context=None):
        """Generate natural language response for chat"""
        
        system_prompt = """You are a logistics contract expert. Answer questions based on the contract context provided.
        Be specific, include deadlines, and offer to help take action when relevant."""
        
        user_prompt = f"""
        Contract Context: {context}
        
        {f"Shipment Context: {shipment_context}" if shipment_context else ""}
        
        Question: {query}
        
        Provide a helpful, accurate response. If this involves a deadline, mention the time remaining.
        """
        
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    system_instruction=system_prompt,
                )
            )
            
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

    @staticmethod
    async def extract_shipment_details(document_text):
        """Extract shipment details from a shipping label or invoice PDF"""
        prompt = f"""
        Extract shipment details from the following shipping document (label, invoice, or receipt).
        Return as VALID JSON ONLY with these exact keys (use null if not found/unsure):
        
        - tracking_number: The shipment tracking number (string)
        - carrier: Company like UPS, FedEx, DHL, USPS, etc. (string)
        - ship_date: Date the item was shipped in YYYY-MM-DD format (string)
        - delivery_date: Date delivered in YYYY-MM-DD format, ONLY if it shows as delivered (string)
        - contents: What is inside the package based on description (string)
        - value: The declared or commercial value as a float number without currency symbols (float)
        - special_handling: Array of strings like ["Fragile", "Hazardous", "Adult Signature Required"] based on labels/marks (array)
        
        Document text:
        {document_text[:8000]}
        
        Return ONLY valid JSON format. A single flat dictionary. No markdown blocks, no other text.
        """
        
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            content = re.sub(r'```json\s*|\s*```', '', response.text)
            return json.loads(content)
        except Exception as e:
            print(f"❌ Error extracting shipment details: {e}")
            return None

    @staticmethod
    async def extract_claim_details(document_text):
        """Extract claim details from a damage report or repair estimate PDF"""
        prompt = f"""
        Extract claim details from the following document (damage report, repair estimate, customer complaint).
        Return as VALID JSON ONLY with these exact keys (use null if not found):
        
        - damage_description: A clear 2-3 sentence summary explaining what was damaged and how (string)
        - estimated_value: The estimated cost of repair or total item value as a float number without currency symbols (float)
        
        Document text:
        {document_text[:8000]}
        
        Return ONLY valid JSON format. A single flat dictionary. No markdown blocks, no other text.
        """
        
        try:
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            content = re.sub(r'```json\s*|\s*```', '', response.text)
            return json.loads(content)
        except Exception as e:
            print(f"❌ Error extracting claim details: {e}")
            return None