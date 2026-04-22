import os
from fpdf import FPDF
from datetime import datetime, timedelta

def create_contract_pdf(filepath):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    text = """
AMAZON LOGISTICS MASTER REGIONAL SERVICE AGREEMENT 2024
----------------------------------------------------------------------------------------------------
Document Ref: AMZ-LOG-2024-8890 | Execution Copy | Confidential and Proprietary
Effective Date: January 1, 2024 | Expiry Date: December 31, 2025
Carrier Sub-entity: Amazon Logistics North America (AMZL-NA)
Service Level Designator: Priority Freight / FBA Standard Delivery / Next Day Air

SECTION 1: PURPOSE AND SCOPE OF AGREEMENT
This Master Service Agreement ("Agreement") is entered into by and between Amazon Logistics ("Carrier") and the undersigned 
merchant ("Shipper"). This Agreement governs the domestic and international transportation of goods, warehousing, and 
Fulfillment by Amazon (FBA) services. The terms contained herein supersede all previous verbal or written agreements.

SECTION 2: CLAIM FILING DEADLINES AND PROCEDURES
The Shipper must strictly adhere to the following timeline for filing claims related to lost, damaged, or delayed freight. Failure to 
file within these strict windows constitutes a full waiver of the Shipper's right to recovery:
2.1. Standard Delivery Claims: All claims for damage occurring during standard transit must be filed within 7 days from the physical delivery date.
2.2. Inventory Transit Claims: Claims regarding discrepancies between manifested inventory and received warehouse inventory must be filed within 14 days from the tender date.
2.3. Rate and Billing Disputes: Any contestation of overcharges or auditing errors must be submitted within 15 days of invoice generation.
2.4. FBA Internal Claims: Claims regarding damage occurring inside Amazon fulfillment centers must be submitted within 30 days of the item's logged arrival.

SECTION 3: LIABILITY LIMITATIONS AND VALUATION CAPS
In the event of lost, stolen, or damaged shipments, Amazon's liability is strictly governed by the following limits, regardless of the 
actual value of the goods, unless supplemental insurance was purchased prior to dispatch:
3.1. Standard Ground Coverage: Maximum liability is strictly capped at $100 per individual package.
3.2. FBA Inventory Replacements: Maximum liability is capped at the replacement value not to exceed $500 per individual SKU.
3.3. High-Value Declarations: Items exceeding $1,000 in value must utilize specialized FBA prep and vault services; otherwise, zero liability applies.

SECTION 4: PACKAGING, DUNNAGE, AND OPERATIONS REQUIREMENTS
The Shipper is solely responsible for ensuring all freight is packaged to withstand the rigors of automated sortation systems:
4.1. FBA Prep Protocol: "Frustration-Free" packaging is strictly required. Polybags must contain suffocation warnings if opening exceeds 5 inches.
4.2. Fragile Goods: Only Amazon-certified, drop-tested protective packaging (ISTA-6) is permitted for glassware or electronics.
4.3. Weight Limitations: Maximum safe lifting weight is 50 lbs per corrugated box. Items over 50 lbs require "Team Lift" stickers.
4.4. Dock Operations: Carrier pickup drivers are allotted a maximum window of 15 minutes at the Shipper's loading dock. Delays will incur a $50/hour detention fee.

SECTION 5: INDEMNIFICATION AND FORCE MAJEURE
5.1. The Shipper agrees to indemnify, defend, and hold harmless Amazon Logistics from any third-party claims arising from hazardous materials, improper packaging, or intellectual property infringement.
5.2. Neither party shall be held liable for delays or failures in performance resulting from acts of God, extreme weather, labor strikes, global pandemics, or acts of terrorism (Force Majeure).
    """
    for line in text.split('\n'):
        pdf.multi_cell(190, 5, txt=line)
        
    pdf.output(filepath)
    print(f"Created: {filepath}")

def create_shipment_pdf(filepath):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    past_ship = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    past_delivery = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    
    text = f"""
OFFICIAL SHIPPING INVOICE AND MANIFEST - COPY 1
====================================================================================================
Issued By: Fulfillment Services Direct
Carrier Assigned: Amazon Logistics (AMZL-NA)
Tracking Identification Number: TBA-Z999888777
Service Level: Next-Day Air Priority (Signature Required)

SHIPMENT ROUTING DETAILS
--------------------------------------------------
Origin Facility: Warehouse 42, Seattle, WA 98109
Destination: Tech Hub Offices, Austin, TX 78701
Shipment Tender Date: {past_ship}
Confirmed Delivery Date: {past_delivery}
Total Transit Time: 48 Hours

PHYSICAL CHARACTERISTICS
--------------------------------------------------
Total Gross Weight: 42.5 lbs
Dimensional Volume: 24 x 18 x 12 inches (Standard Corrugated)
Freight Class: Class 100 (Electronics)

COMMERCIAL INVOICE / PACKAGE CONTENTS
--------------------------------------------------
SKU: ESP-PRO-9000
Description: Commercial Grade Industrial Espresso Machine (Stainless Steel)
Quantity: 1 Unit
Harmonized Tariff Schedule (HTS) Code: 8419.81.90
Country of Origin: Italy

FINANCIAL DECLARATION
--------------------------------------------------
Declared Commercial Value: $450.00 USD
Freight Charges Paid: $65.50 USD
Insurance Premium: Declared

SPECIAL HANDLING INSTRUCTIONS AND MARKS
--------------------------------------------------
[x] EXTREMELY FRAGILE - DO NOT DROP
[x] UP ARROWS - KEEP UPRIGHT
[x] HEAVY - TEAM LIFT REQUIRED
[ ] HAZARDOUS MATERIALS - UN3481 LITHIUM ION BATTERIES
    """
    for line in text.split('\n'):
        pdf.multi_cell(190, 5, txt=line)
        
    pdf.output(filepath)
    print(f"Created: {filepath}")

def create_combined_pdf(filepath):
    # Generating the ultimate combined 3-page deep PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    past_ship = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    past_delivery = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    
    text = f"""
AMAZON LOGISTICS MASTER REGIONAL SERVICE AGREEMENT 2024
----------------------------------------------------------------------------------------------------
Agreement Number: AMZ-LOG-COMBINED
Carrier Sub-entity: Amazon Logistics North America (AMZL-NA)

SECTION 1: CLAIM FILING DEADLINES
The Shipper must strictly adhere to the following timeline for filing claims. Failure to file within these windows constitutes a waiver of recovery.
1.1. Standard Delivery Claims: Filed within 7 days from the physical delivery date.
1.2. Inventory Transit Claims: Filed within 14 days from the original tender date.
1.3. Rate Disputes: Filed within 15 days of invoice generation.
1.4. FBA Claims: Filed within 30 days of fulfillment center arrival.

SECTION 2: LIABILITY LIMITATIONS
2.1. Standard Coverage: Maximum liability is strictly capped at $100 per package.
2.2. FBA Inventory: Replacement value up to $500 max per item.

SECTION 3: PACKAGING REQUIREMENTS
3.1. Maximum Weight: 50 lbs per box.
3.2. Pickup Window: Drivers wait a maximum of 15 minutes.

[END OF LEGAL AGREEMENT]
====================================================================================================
[PAGE BREAK INTENDED - BEGIN SHIPPING MANIFEST]

TRACKING NUMBER: TBA-Z999888777
Carrier Assigned: Amazon Logistics (AMZL-NA)
Service Level: Next-Day Air Priority

Ship Date: {past_ship}
Delivery Date: {past_delivery}

Package Contents: 
- 1x Commercial Grade Industrial Espresso Machine (SKU: ESP-PRO-9000)
Weight: 42.5 lbs
Declared Commercial Value: $450.00 USD

Special Handling:
[x] EXTREMELY FRAGILE - DO NOT DROP
[x] HEAVY - TEAM LIFT REQUIRED

[END OF MANIFEST]
====================================================================================================
[PAGE BREAK INTENDED - BEGIN CUSTOMER DAMAGE REPORT]

DAMAGE INCIDENT REPORT - CUSTOMER CLAIMS DEPARTMENT
----------------------------------------------------------------------------------------------------
Date Filed: {datetime.now().strftime("%Y-%m-%d")}
Related Tracking ID: TBA-Z999888777
Customer Name: Tech Hub Facilities Management

INCIDENT NARRATIVE AND DAMAGE DESCRIPTION:
Upon receiving the package at our loading dock, our receiving manager immediately noted that the outer corrugated 
shipping box was severely compromised. The box lacked "Fragile" stickers on 3 of the 4 sides, despite our 
manifest stating it was required. 

Upon opening the box while the driver was present, we discovered the industrial espresso machine had been 
subjected to immense blunt force trauma, seemingly having been dropped off the back of the transport vehicle. 
The main pressurized water reservoir is completely shattered into glass shards. Furthermore, the internal boiler casing 
is deeply dented, compromising the pressure seals. The internal wiring harness is severed in two places.

Because this is commercial-grade equipment relying on high-pressure steam, the unit is entirely unsalvageable 
and repairing it would pose a significant safety hazard. We demand a full unit replacement immediately.

TOTAL ESTIMATED REPLACEMENT VALUE SOUGHT:
450.00
    """
    for line in text.split('\n'):
        pdf.multi_cell(190, 5, txt=line)
        
    pdf.output(filepath)
    print(f"Created: {filepath}")

def create_fedex_combined_pdf(filepath):
    # Generates a completely different company/values for the demo
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    past_ship = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
    past_delivery = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    text = f"""
FEDEX EXPRESS MASTER TRANSPORTATION AGREEMENT (2025)
----------------------------------------------------------------------------------------------------
Account Number: FDX-CORP-554100
Operating Entity: Federal Express Corporation ("FedEx")
Service Scope: International Priority / Domestic Overnight

ARTICLE I: RECOVERY TIMELINES AND CLAIM FILING DEADLINES
The customer ("Shipper") agrees that all recovery and reimbursement actions must be initiated within the 
following strict statutory timelines. No exceptions will be granted.
1.1. Delivery Exception Claims: Must be filed within 21 days from the published delivery date.
1.2. Concealed Damage Claims: Discovered after delivery with no outer box damage; must be filed within 14 days.
1.3. Invoice Auditing/Billing Disputes: Claims for misapplied fuel surcharges must be filed within 30 days.
1.4. International Freight Claims: Governed by the Warsaw Convention, filed within 45 days of arrival.

ARTICLE II: DECLARED VALUE AND MAXIMUM COVERAGE
Unless a higher value is declared on the airway bill and the applicable premium is remitted prior to tender, 
FedEx's liability is severely restricted.
2.1. Standard Default Liability: Coverage is strictly limited to $100.00 USD per shipment.
2.2. Electronics/Computer Equipment: Maximum authorized declared value is $5,000 USD per package.
2.3. Precious Metals/Jewelry: Strictly limited to $1,000 USD total liability regardless of declared value.

ARTICLE III: RESTRICTIONS AND HANDLING
3.1. Dimension Limits: Packages exceeding 108 inches in length will incur a $120 oversized penalty.
3.2. Weight Limits: Maximum gross weight per parcel is 150 lbs for Express services.

[END OF LEGAL AGREEMENT]
====================================================================================================
[PAGE BREAK INTENDED - COMMERCIAL INVOICE]

FEDEX EXPRESS AIRWAY BILL & MANIFEST
Airway Bill / Tracking No: FDX-1122334455
Service Level: Standard Overnight End-of-Day

Ship Date: {past_ship}
Delivery Date: {past_delivery}

Consigned Goods: 
- 5x Apple MacBook Pro 16-inch (M3 Max, 64GB RAM)
Weight: 28.5 lbs
Declared Insurance Value: $17,500.00 USD

Special Handling Instructions:
[x] SIGNATURE REQUIRED (ADULT 21+)
[x] HIGH VALUE SECURITY CAGE REQUIRED
[ ] SATURDAY DELIVERY

[END OF MANIFEST]
====================================================================================================
[PAGE BREAK INTENDED - LOSS/DAMAGE CLAIM REPORT]

FEDEX CARGO CLAIMS DEPARTMENT - OFFICIAL CLAIM FORM
----------------------------------------------------------------------------------------------------
Date of Submission: {datetime.now().strftime("%Y-%m-%d")}
Referenced AWB Tracking: FDX-1122334455

NATURE OF CLAIM: WATER DAMAGE IN TRANSIT

DETAILED DESCRIPTION OF LOSS:
The shipment containing 5 high-end laptops was left on our uncovered loading dock during a severe thunderstorm, 
despite the "Signature Required" directive on the airway bill. The driver forged the signature as "Dock Worker" 
and abandoned the freight. 

The corrugated master carton was entirely saturated with standing water. Upon inspecting the inner retail 
boxes, water had penetrated the plastic wrap. 2 of the 5 MacBook Pro laptops will not power on and show 
immediate signs of internal liquid corrosion on the motherboard logic boards.

We are claiming the total loss of 2 units at their wholesale value, plus a refund of the Express freight charges 
due to the severe breach of service contract (failure to obtain an authorized signature).

CLAIM AMOUNT REQUESTED:
7000.00
    """
    for line in text.split('\n'):
        pdf.multi_cell(190, 5, txt=line)
        
    pdf.output(filepath)
    print(f"Created: {filepath}")

if __name__ == "__main__":
    os.makedirs("demo_files", exist_ok=True)
    create_contract_pdf("demo_files/1_Amazon_Logistics_Contract.pdf")
    create_shipment_pdf("demo_files/2_Amazon_Shipping_Invoice.pdf")
    create_combined_pdf("demo_files/4_Amazon_Combined_All_In_One.pdf")
    create_fedex_combined_pdf("demo_files/5_FedEx_Combined_All_In_One.pdf")
    print("Heavy-content demo files generated successfully!")
