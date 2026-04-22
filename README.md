AI Agent for Logistics Contract Intelligence
📌 Overview

It is an AI-powered system that reads and understands logistics carrier contracts (SLAs) from PDFs and helps teams track deadlines, obligations, and risks in real time.

Problem Satement

Logistics contracts contain critical rules (deadlines, penalties, claims), but they are buried in long documents. Teams often miss key actions, leading to losses.

💡 Solution

ContractIQ uses AI Agents + RAG to:

📄 Extract rules from contract PDFs
🔍 Answer contract-related queries
⏰ Track deadlines and obligations
⚠️ Alert risks and suggest actions
🧠 Key Features
Contract PDF parsing & information extraction
AI-powered query system (chat interface)
Deadline tracking & alerts
Multi-carrier contract management
Risk detection (missed claims, penalties)


🏗️ Tech Stack
Frontend: Streamlit
Backend: Python (FastAPI)
AI: LLM + RAG
Tools: PDF parsing, vector database
⚙️ How It Works
Upload contract PDF
System extracts and structures data
AI agent answers queries
Alerts for deadlines & risks
📊 Example

Scenario: Damaged shipment
→ Identifies contract
→ Checks claim deadline
→ Alerts user
→ Suggests next action

🚀 Run Locally
# Install dependencies
pip install -r requirements.txt

# Run backend
python -m backend.main

# Run frontend
cd frontend
streamlit run app.py



📁 Structure
backend/
frontend/
data/
demo_files/


🏆 Hackathon
Theme: AI for Logistics
Focus: Contract Intelligence using AI Agents


⭐ Star this repo if you like it!