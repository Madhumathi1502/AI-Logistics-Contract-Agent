# backend/database/models.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# SQL for creating tables (we'll run this manually first)
CREATE_TABLES_SQL = """
-- Carriers table
CREATE TABLE IF NOT EXISTS carriers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Contracts table
CREATE TABLE IF NOT EXISTS contracts (
    id SERIAL PRIMARY KEY,
    carrier_id INTEGER REFERENCES carriers(id),
    contract_name VARCHAR(200),
    effective_date DATE,
    expiry_date DATE,
    document_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Rules extracted from contracts
CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id),
    rule_type VARCHAR(50), -- 'claim_deadline', 'liability_limit', 'packaging', etc.
    rule_value TEXT,
    unit VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Shipments tracking
CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    carrier_id INTEGER REFERENCES carriers(id),
    ship_date DATE,
    delivery_date DATE,
    value DECIMAL(10,2),
    contents TEXT,
    special_handling TEXT[],
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Deadlines tracking
CREATE TABLE IF NOT EXISTS deadlines (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id),
    rule_id INTEGER REFERENCES rules(id),
    deadline_date DATE NOT NULL,
    deadline_type VARCHAR(50),
    days_remaining INTEGER,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'actioned', 'missed'
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Claims tracking
CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER REFERENCES shipments(id),
    claim_number VARCHAR(100),
    filed_date DATE,
    amount DECIMAL(10,2),
    status VARCHAR(50), -- 'draft', 'filed', 'approved', 'denied'
    documents JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# Pydantic models for API
class Carrier(BaseModel):
    id: Optional[int]
    name: str

class Contract(BaseModel):
    id: Optional[int]
    carrier_id: int
    contract_name: str
    effective_date: str
    expiry_date: str

class Rule(BaseModel):
    id: Optional[int]
    contract_id: int
    rule_type: str
    rule_value: str
    unit: Optional[str]

class Shipment(BaseModel):
    id: Optional[int]
    tracking_number: str
    carrier_id: int
    ship_date: str
    delivery_date: Optional[str]
    value: float
    contents: str
    special_handling: List[str] = []
    status: str

class Deadline(BaseModel):
    id: Optional[int]
    shipment_id: int
    deadline_date: str
    deadline_type: str
    days_remaining: int
    status: str

class Claim(BaseModel):
    id: Optional[int]
    shipment_id: int
    claim_number: Optional[str]
    filed_date: Optional[str]
    amount: float
    status: str