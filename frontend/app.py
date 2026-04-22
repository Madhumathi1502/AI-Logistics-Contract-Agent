# frontend/app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json

# Page config
st.set_page_config(
    page_title="ContractIQ",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL (change if different)
API_URL = "http://localhost:8001"

# Custom CSS
# Custom CSS - REPLACE THIS ENTIRE SECTION
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Typography */
    html, body {
        font-family: 'Inter', sans-serif !important;
    }

    /* Main Header Styling */
    .main-header {
        font-size: 2.8rem;
        color: #0F172A;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Subheaders */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    /* Top Navigation Buttons */
    div.row-widget.stButton > button {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    div.row-widget.stButton > button:hover {
        border-color: rgba(128, 128, 128, 0.4);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transform: translateY(-1px);
    }
    /* Primary Buttons (Submit, etc) */
    div.row-widget.stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: white !important;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    div.row-widget.stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.3);
    }

    /* Metric Cards (Dashboard) */
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricValue"] {
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 500;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }

    /* Input Fields */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 8px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextInput > div > div > input:focus, 
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within,
    .stDateInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Alerts and Callouts */
    .critical-alert {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .warning-alert {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }
    .success-alert {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
    }

    /* Dataframes/Tables */
    .stDataFrame {
        border-radius: 12px;
        padding: 0.5rem;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Chat Messages */
    .chat-message-user {
        border-radius: 16px 16px 16px 4px;
        margin: 1rem 0;
        max-width: 85%;
        align-self: flex-start;
        border: 1px solid rgba(128, 128, 128, 0.2);
        font-weight: 500;
        line-height: 1.5;
        padding: 1rem 1.5rem;
    }
    
    .chat-message-agent {
        border-radius: 16px 16px 4px 16px;
        margin: 1rem 0;
        max-width: 85%;
        align-self: flex-end;
        margin-left: auto;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        font-weight: 400;
        line-height: 1.5;
        padding: 1rem 1.5rem;
    }

    /* Expanders */
    .stExpander {
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    
    /* Uploader Zone */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed rgba(128, 128, 128, 0.4) !important;
        border-radius: 12px !important;
        transition: all 0.2s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #3B82F6 !important;
    }
    
    /* Form Background */
    div[data-testid="stForm"] {
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_claim" not in st.session_state:
    st.session_state.current_claim = None

# Sidebar[[]]
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1E3A8A/FFFFFF?text=ContractIQ", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### 🤖 Active Agents")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📄 Contract\nExpert")
    with col2:
        st.info("⏰ Deadline\nMonitor")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📝 Claim\nAssistant")
    with col2:
        st.info("✅ Compliance\nChecker")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("📄 Upload New Contract", use_container_width=True):
        st.session_state.page = "Contracts"
    if st.button("📦 Add Shipment", use_container_width=True):
        st.session_state.page = "Shipments"
    if st.button("⏰ Check Deadlines", use_container_width=True):
        with st.spinner("Checking deadlines..."):
            requests.post(f"{API_URL}/api/deadlines/check")
            st.success("Deadlines checked!")
    
    st.markdown("---")
    st.markdown(f"**📅 Today:** {datetime.now().strftime('%B %d, %Y')}")

# Main content
st.markdown('<p class="main-header">📦 ContractIQ</p>', unsafe_allow_html=True)
st.markdown("AI-Powered Contract Intelligence for Logistics")

# Top navigation
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
with col2:
    if st.button("📄 Contracts", use_container_width=True):
        st.session_state.page = "Contracts"
with col3:
    if st.button("📦 Shipments", use_container_width=True):
        st.session_state.page = "Shipments"
with col4:
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "Chat"
with col5:
    if st.button("⏰ Deadlines", use_container_width=True):
        st.session_state.page = "Deadlines"
with col6:
    if st.button("📝 Claims", use_container_width=True):
        st.session_state.page = "Claims"
with col7:
    if st.button("✅ Compliance", use_container_width=True):
        st.session_state.page = "Compliance"

st.markdown("---")

# Set default page
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# === DASHBOARD PAGE ===
if st.session_state.page == "Dashboard":
    st.header("📊 Dashboard")
    
    # Fetch dashboard data
    try:
        response = requests.get(f"{API_URL}/api/dashboard")
        if response.status_code == 200:
            data = response.json()
            
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Shipments", data['stats']['total_shipments'], delta=None)
            with col2:
                st.metric("Pending Claims", data['stats']['pending_claims'], delta=None)
            with col3:
                st.metric("Active Deadlines", data['stats']['active_deadlines'], delta=None)
            with col4:
                critical = data['alerts']['stats']['critical']
                st.metric("Critical Alerts", critical, delta=None, delta_color="inverse")
            
            st.markdown("---")
            
            # Alerts section
            st.subheader("🚨 Active Alerts")
            
            alerts = data['alerts']['alerts']
            if alerts:
                for alert in alerts:
                    if alert['type'] == 'critical':
                        st.markdown(f"""
                        <div class="critical-alert">
                            <strong>{alert['title']}</strong><br>
                            {alert['message']}
                        </div>
                        """, unsafe_allow_html=True)
                    elif alert['type'] == 'warning':
                        st.markdown(f"""
                        <div class="warning-alert">
                            <strong>{alert['title']}</strong><br>
                            {alert['message']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="success-alert">
                            <strong>{alert['title']}</strong><br>
                            {alert['message']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No active alerts")
            
            st.markdown("---")
            
            # Recent shipments
            st.subheader("📦 Recent Shipments")
            if data['recent_shipments']:
                df = pd.DataFrame(data['recent_shipments'])
                st.dataframe(df[['tracking_number', 'contents', 'status', 'created_at']], use_container_width=True)
            else:
                st.info("No shipments yet")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("Make sure the backend API is running at " + API_URL)

# === CONTRACTS PAGE ===
elif st.session_state.page == "Contracts":
    st.header("📄 Contract Management")
    
    tab1, tab2 = st.tabs(["Upload Contract", "View Contracts"])
    
    with tab1:
        st.subheader("Upload New Carrier Contract")
        
        col1, col2 = st.columns(2)
        
        with col1:
            carrier = st.selectbox("Select Carrier", ["FedEx", "UPS", "DHL", "Other"])
            if carrier == "Other":
                carrier = st.text_input("Enter Carrier Name")
            
            contract_name = st.text_input("Contract Name", f"{carrier} Service Agreement 2024")
        
        with col2:
            uploaded_file = st.file_uploader("Upload PDF Contract", type=['pdf'])
        
        if uploaded_file and st.button("Process Contract", type="primary"):
            with st.spinner("Processing contract... This may take a moment."):
                files = {"file": uploaded_file.getvalue()}
                data = {"carrier": carrier, "contract_name": contract_name}
                
                response = requests.post(
                    f"{API_URL}/api/contracts/upload",
                    files={"file": uploaded_file},
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Contract processed successfully!")
                    st.info(f"Extracted {result['rules_extracted']} rules from {result['carrier']} contract")
                    
                    # Show extracted rules
                    st.subheader("Extracted Rules")
                    st.json(result['rules'])
                else:
                    st.error(f"Error: {response.text}")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Processed Contracts")
        with col2:
            if st.button("🗑️ Delete All", type="primary", use_container_width=True):
                with st.spinner("Deleting all..."):
                    del_response = requests.delete(f"{API_URL}/api/contracts")
                    if del_response.status_code == 200:
                        st.success("All contracts deleted!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete all: {del_response.text}")
        
        response = requests.get(f"{API_URL}/api/contracts")
        if response.status_code == 200:
            contracts = response.json()
            if contracts:
                for contract in contracts:
                    with st.expander(f"{contract['contract_name']} - {contract['carrier_name']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Effective:** {contract['effective_date']}")
                            st.write(f"**Expiry:** {contract['expiry_date']}")
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"del_contract_{contract['id']}", type="primary"):
                                with st.spinner("Deleting..."):
                                    del_response = requests.delete(f"{API_URL}/api/contracts/{contract['id']}")
                                    if del_response.status_code == 200:
                                        st.success("Deleted! Refreshing...")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to delete: {del_response.text}")
                        
                        # Get rules for this contract
                        st.markdown("---")
                        st.write("**Rules:**")
                        rules_response = requests.get(f"{API_URL}/api/contracts/{contract['id']}/rules")
                        if rules_response.status_code == 200:
                            rules = rules_response.json()
                            if rules:
                                # Convert to a nicer display format
                                rules_data = {r['rule_type']: r['rule_value'] for r in rules}
                                st.json(rules_data)
                            else:
                                st.info("No rules extracted for this contract yet.")
                        else:
                            st.error("Failed to load rules.")
            else:
                st.info("No contracts uploaded yet")

# === SHIPMENTS PAGE ===
elif st.session_state.page == "Shipments":
    st.header("📦 Shipment Management")
    
    st.subheader("Add New Shipment")
    
    # Auto-fill from document
    st.markdown("##### 📄 Auto-fill from Document")
    uploaded_shipment_doc = st.file_uploader("Upload Shipping Label, Invoice, or Receipt", type=['pdf', 'png', 'jpg'], key="shipment_doc")
    
    if "shipment_prefill" not in st.session_state:
        st.session_state.shipment_prefill = {}
        
    if uploaded_shipment_doc and st.button("Extract Data", key="extract_shipment", type="secondary"):
        with st.spinner("Analyzing document with AI..."):
            try:
                response = requests.post(
                    f"{API_URL}/api/shipments/extract",
                    files={"file": uploaded_shipment_doc.getvalue()}
                )
                if response.status_code == 200:
                    st.session_state.shipment_prefill = response.json()
                    st.success("Data extracted successfully! The form below has been auto-filled.")
                    with st.expander("View Raw Extracted Data"):
                        st.json(st.session_state.shipment_prefill)
                else:
                    st.error(f"Extraction failed: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
                
    st.markdown("---")
    
    prefill = st.session_state.shipment_prefill
    
    with st.form("add_shipment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tracking_number = st.text_input("Tracking Number*", value=prefill.get('tracking_number', ''), placeholder="e.g. 1Z9999999999999999")
            
            # Match carrier if possible
            carrier_options = ["UPS", "FedEx", "DHL", "USPS", "Other"]
            carrier_idx = 0
            if prefill.get('carrier'):
                for i, c in enumerate(carrier_options):
                    if c.lower() in prefill.get('carrier', '').lower():
                        carrier_idx = i
                        break
            
            carrier = st.selectbox("Carrier*", carrier_options, index=carrier_idx)
            if carrier == "Other":
                carrier = st.text_input("Specify Carrier*", value=prefill.get('carrier', '') if carrier_idx == 0 else '')
                
            contents = st.text_input("Contents*", value=prefill.get('contents', ''), placeholder="e.g. Electronics, Clothing")
            value = st.number_input("Declared Value ($)*", min_value=0.0, value=float(prefill.get('value', 100.0)), step=10.0)
            
        with col2:
            # Handle Dates
            ship_date_val = datetime.now().date()
            if prefill.get('ship_date'):
                try:
                    ship_date_val = datetime.strptime(prefill.get('ship_date'), "%Y-%m-%d").date()
                except:
                    pass
            ship_date = st.date_input("Ship Date*", value=ship_date_val)
            
            is_delivered = st.checkbox("Shipment already delivered?", value=bool(prefill.get('delivery_date')))
            delivery_date = None
            if is_delivered:
                del_date_val = datetime.now().date()
                if prefill.get('delivery_date'):
                    try:
                        del_date_val = datetime.strptime(prefill.get('delivery_date'), "%Y-%m-%d").date()
                    except:
                        pass
                delivery_date = st.date_input("Delivery Date", value=del_date_val)
            
            # Handle Special Handling
            handling_options = ["Fragile", "Hazardous", "Perishable", "Oversize", "Adult Signature Required"]
            default_handling = []
            if prefill.get('special_handling'):
                for h in handling_options:
                    for ext_h in prefill.get('special_handling', []):
                        if isinstance(ext_h, str) and h.lower() in ext_h.lower():
                            default_handling.append(h)
            
            special_handling = st.multiselect(
                "Special Handling Requirements",
                handling_options,
                default=default_handling
            )
            
        submit = st.form_submit_button("Add Shipment", type="primary")
        
        if submit:
            if not tracking_number or not carrier or not contents:
                st.error("Please fill in all required fields (*).")
            else:
                with st.spinner("Adding shipment..."):
                    payload = {
                        "tracking_number": tracking_number,
                        "carrier": carrier,
                        "ship_date": ship_date.isoformat(),
                        "delivery_date": delivery_date.isoformat() if delivery_date else None,
                        "value": float(value),
                        "contents": contents,
                        "special_handling": special_handling
                    }
                    
                    try:
                        response = requests.post(f"{API_URL}/api/shipments", json=payload)
                        if response.status_code == 200:
                            st.success(f"✅ Shipment {tracking_number} added successfully!")
                            st.session_state.shipment_prefill = {} # Clear prefill after success
                        else:
                            st.error(f"Failed to add shipment: {response.text}")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")

# === CHAT PAGE ===
elif st.session_state.page == "Chat":
    st.header("💬 Chat with Contract Expert")
    
    # Agent selector
    agent = st.selectbox(
        "Select Agent",
        ["Contract Expert", "Claim Assistant", "Compliance Checker"],
        key="chat_agent"
    )
    
    # Carrier filter
    carrier_filter = st.selectbox(
        "Filter by Carrier (optional)",
        ["All", "FedEx", "UPS", "DHL"],
        key="carrier_filter"
    )
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message-user">👤 {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-agent">🤖 {message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Ask about contracts, deadlines, or claims...", key="chat_input")
    with col2:
        send = st.button("Send", type="primary", use_container_width=True)
    
    if send and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from API
        with st.spinner("Thinking..."):
            carrier = None if carrier_filter == "All" else carrier_filter
            response = requests.post(
                f"{API_URL}/api/chat",
                json={"query": user_input, "carrier": carrier}
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error."})
        
        st.rerun()
    
    # Suggested questions
    st.markdown("---")
    st.subheader("💡 Suggested Questions")
    col1, col2, col3 = st.columns(3)
    
    # Use session state to trigger the API call on the next rerun
    if "suggested_question" not in st.session_state:
        st.session_state.suggested_question = None
        
    with col1:
        if st.button("What's FedEx claim deadline?"):
            st.session_state.suggested_question = "What's FedEx claim deadline?"
            st.rerun()
    with col2:
        if st.button("Compare FedEx and DHL fragile rules"):
            st.session_state.suggested_question = "Compare FedEx and DHL rules for fragile items"
            st.rerun()
    with col3:
        if st.button("How to file a claim?"):
            st.session_state.suggested_question = "How do I file a claim for a damaged package?"
            st.rerun()
            
    # Process suggested question if one was clicked
    if st.session_state.suggested_question:
        q = st.session_state.suggested_question
        st.session_state.suggested_question = None # Clear it
        
        # Add user message
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Get response from API
        with st.spinner("Thinking..."):
            carrier = None if carrier_filter == "All" else carrier_filter
            response = requests.post(
                f"{API_URL}/api/chat",
                json={"query": q, "carrier": carrier}
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.messages.append({"role": "assistant", "content": result['response']})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, I encountered an error."})
        
        st.rerun()

# === DEADLINES PAGE ===
elif st.session_state.page == "Deadlines":
    st.header("⏰ Deadline Monitor")
    
    # Fetch deadlines
    response = requests.get(f"{API_URL}/api/deadlines?days=90")
    
    if response.status_code == 200:
        deadlines = response.json()
        
        if deadlines:
            # Convert to DataFrame
            df = pd.DataFrame(deadlines)
            
            # Color code row based on days remaining
            def highlight_row(row):
                days = row['days_remaining']
                if days < 0:
                    return ['background-color: #E2E8F0; color: #475569; text-decoration: line-through; font-weight: bold'] * len(row)
                elif days <= 1:
                    return ['background-color: #FEF2F2; color: #991B1B; font-weight: bold'] * len(row)
                elif days <= 3:
                    return ['background-color: #FFFBEB; color: #92400E; font-weight: bold'] * len(row)
                elif days <= 7:
                    return ['background-color: #F0FDF4; color: #166534'] * len(row)
                return [''] * len(row)
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                missed = len(df[df['days_remaining'] < 0])
                st.metric("Missed (< 0 days)", missed)
            with col2:
                critical = len(df[(df['days_remaining'] >= 0) & (df['days_remaining'] <= 1)])
                st.metric("Critical (0-1 day)", critical)
            with col3:
                warning = len(df[(df['days_remaining'] > 1) & (df['days_remaining'] <= 3)])
                st.metric("Warning (2-3 days)", warning)
            with col4:
                upcoming = len(df[(df['days_remaining'] > 3) & (df['days_remaining'] <= 7)])
                st.metric("Upcoming (4-7 days)", upcoming)
            
            # Display table with styling
            display_cols = ['tracking_number', 'carrier_name', 'deadline_type', 'deadline_date', 'days_remaining', 'value']
            display_df = df[display_cols].sort_values(by="days_remaining")
            styled_df = display_df.style.apply(highlight_row, axis=1)
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Visual timeline
            st.subheader("Deadline Timeline")
            
            fig = go.Figure()
            
            for _, row in df.iterrows():
                color = 'gray' if row['days_remaining'] < 0 else 'red' if row['days_remaining'] <= 1 else 'orange' if row['days_remaining'] <= 3 else 'green'
                
                fig.add_trace(go.Scatter(
                    x=[row['deadline_date']],
                    y=[row['tracking_number']],
                    mode='markers',
                    marker=dict(size=15, color=color),
                    text=f"${row['value']} - {row['days_remaining']} days left" if row['days_remaining'] >= 0 else f"${row['value']} - Missed by {abs(row['days_remaining'])} days",
                    name=row['tracking_number']
                ))
            
            fig.update_layout(
                title="Deadlines by Date",
                xaxis_title="Date",
                yaxis_title="Shipment",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("No upcoming deadlines")
    else:
        st.error("Failed to fetch deadlines")

# === CLAIMS PAGE ===
elif st.session_state.page == "Claims":
    st.header("📝 Claim Assistant")
    
    tab1, tab2 = st.tabs(["File New Claim", "View Claims"])
    
    with tab1:
        st.subheader("Start a New Claim")
        
        # Auto-fill from document
        st.markdown("##### 📄 Auto-fill from Damage Report")
        uploaded_claim_doc = st.file_uploader("Upload Damage Report or Photo Evidence (PDF)", type=['pdf'], key="claim_doc")
        
        if "claim_prefill" not in st.session_state:
            st.session_state.claim_prefill = {}
            
        if uploaded_claim_doc and st.button("Extract Data", key="extract_claim", type="secondary"):
            with st.spinner("Analyzing document with AI..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/claims/extract",
                        files={"file": uploaded_claim_doc.getvalue()}
                    )
                    if response.status_code == 200:
                        st.session_state.claim_prefill = response.json()
                        st.success("Data extracted successfully! The form below has been auto-filled.")
                        with st.expander("View Raw Extracted Data"):
                            st.json(st.session_state.claim_prefill)
                    else:
                        st.error(f"Extraction failed: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
                    
        st.markdown("---")
        
        prefill_claim = st.session_state.claim_prefill
        
        # Get shipments
        shipments_response = requests.get(f"{API_URL}/api/shipments?status=delivered")
        
        if shipments_response.status_code == 200:
            shipments = shipments_response.json()
            
            if shipments:
                shipment_options = {f"{s['tracking_number']} - ${s['value']}": s['id'] for s in shipments}
                selected = st.selectbox("Select Shipment", list(shipment_options.keys()))
                
                if selected:
                    shipment_id = shipment_options[selected]
                    
                    # Pre-fill description if available
                    default_desc = prefill_claim.get('damage_description', '')
                    if prefill_claim.get('estimated_value'):
                        default_desc += f"\n\nEstimated Value/Cost: ${prefill_claim.get('estimated_value')}"
                        
                    damage_desc = st.text_area("Describe the damage or issue", value=default_desc)
                    
                    if st.button("Start Claim", type="primary"):
                        with st.spinner("Creating claim..."):
                            response = requests.post(
                                f"{API_URL}/api/claims/start",
                                json={"shipment_id": shipment_id, "damage_description": damage_desc}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                st.session_state.current_claim = result
                                st.success("Claim started!")
                                st.session_state.claim_prefill = {} # Clear prefill
                                st.json(result)
                            else:
                                st.error("Failed to start claim")
            else:
                st.info("No delivered shipments found")
    
    with tab2:
        st.subheader("Active Claims")
        
        claims_response = requests.get(f"{API_URL}/api/claims")
        
        if claims_response.status_code == 200:
            claims = claims_response.json()
            
            if claims:
                df = pd.DataFrame(claims)
                st.dataframe(df[['claim_number', 'shipment_id', 'amount', 'status', 'filed_date']], use_container_width=True)
                
                # Claim details
                if len(claims) > 0:
                    claim_ids = [f"Claim {c['id']} - {c['status']}" for c in claims]
                    selected_claim = st.selectbox("View Claim Details", claim_ids)
                    
                    if selected_claim:
                        claim_id = int(selected_claim.split()[1])
                        claim_detail = requests.get(f"{API_URL}/api/claims/{claim_id}")
                        
                        if claim_detail.status_code == 200:
                            st.json(claim_detail.json())
            else:
                st.info("No claims found")

# === COMPLIANCE PAGE ===
elif st.session_state.page == "Compliance":
    st.header("✅ Compliance Checker")
    
    st.subheader("Check Shipment Compliance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        carrier = st.selectbox("Carrier", ["FedEx", "UPS", "DHL"])
        contents = st.text_input("Package Contents", "Electronics")
        value = st.number_input("Declared Value ($)", min_value=0, value=1000)
    
    with col2:
        special_handling = st.multiselect(
            "Special Handling",
            ["Fragile", "Hazardous", "Perishable", "Oversize"]
        )
        packaging_used = st.multiselect(
            "Packaging Used",
            ["Box", "Double-box", "Foam wrap", "Bubble wrap", "Pallet"]
        )
    
    if st.button("Check Compliance", type="primary"):
        shipment_data = {
            "carrier": carrier,
            "contents": contents,
            "value": value,
            "special_handling": special_handling,
            "packaging_used": packaging_used
        }
        
        with st.spinner("Checking compliance..."):
            response = requests.post(f"{API_URL}/api/compliance/check", json=shipment_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result['status'] == 'compliant':
                    st.success(result['message'])
                elif result['status'] == 'warning':
                    st.warning(result['message'])
                    if result.get('warnings'):
                        for w in result['warnings']:
                            st.info(f"⚠️ {w['rule']} - {w['suggestion']}")
                else:
                    st.error(result['message'])
                    if result.get('issues'):
                        for issue in result['issues']:
                            st.error(f"❌ {issue['rule']}")
            else:
                st.error("Failed to check compliance")

# Footer
st.markdown("---")
st.markdown("ContractIQ - AI-Powered Contract Intelligence for Logistics")