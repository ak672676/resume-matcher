import PyPDF2
import io
from typing import Optional

class PDFProcessor:
    """Process PDF files and extract text content"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file: bytes) -> Optional[str]:
        """
        Extract text content from PDF file bytes
        
        Args:
            pdf_file: PDF file as bytes
            
        Returns:
            Extracted text string or None if failed
        """
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            
            # Extract text from all pages
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # Clean up the text
            text_content = text_content.strip()
            
            if not text_content:
                return None
                
            return text_content
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None
    
    @staticmethod
    def validate_pdf(pdf_file: bytes) -> tuple[bool, str]:
        """
        Validate PDF file
        
        Args:
            pdf_file: PDF file as bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size (max 10MB)
            if len(pdf_file) > 10 * 1024 * 1024:
                return False, "File size too large. Maximum size is 10MB."
            
            # Try to read the PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            
            # Check number of pages (max 20 pages)
            if len(pdf_reader.pages) > 20:
                return False, "PDF has too many pages. Maximum is 20 pages."
            
            # Check if it's a text-based PDF (not scanned images)
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            if not text or len(text.strip()) < 50:
                return False, "PDF appears to be scanned or image-based. Please upload a text-based PDF."
            
            return True, "PDF is valid"
            
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"

# Global instance
pdf_processor = PDFProcessor() 