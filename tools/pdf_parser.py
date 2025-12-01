# PDF Parser Tool - Text Extraction
import pdfplumber
import os

class PDFParserTool:
    def __init__(self):
        self.name = "pdf_parser"
    
    def extract_text(self, file_path: str) -> dict:
        """Extract text from PDF"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"File not found: {file_path}"}
            
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            return {
                "success": True,
                "text": text,
                "pages": len(pdf.pages) if 'pdf' in locals() else 0,
                "char_count": len(text)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
