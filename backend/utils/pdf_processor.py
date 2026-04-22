# backend/utils/pdf_processor.py

import PyPDF2
import io

class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(pdf_file):
        """Extract text from uploaded PDF file"""
        try:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
            
            # Clean text: Postgres text columns cannot contain null bytes (0x00)
            text = text.replace('\x00', '')
            
            return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    @staticmethod
    def extract_contract_metadata(text):
        """Extract basic metadata like carrier name, dates"""
        # Simple keyword matching - will be enhanced by LLM
        metadata = {
            "carrier": "Unknown",
            "effective_date": None,
            "expiry_date": None
        }  
        
        # Look for carrier names
        carriers = ["FedEx", "UPS", "DHL", "USPS", "Amazon"]
        for carrier in carriers:
            if carrier.lower() in text.lower():
                metadata["carrier"] = carrier
                break
        
        return metadata