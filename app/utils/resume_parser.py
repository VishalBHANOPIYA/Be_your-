import os
import pdfplumber
import docx
import re

class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text

    @staticmethod
    def extract_text_from_docx(docx_path):
        text = ""
        try:
            doc = docx.Document(docx_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
        return text

    @staticmethod
    def extract_text(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return ResumeParser.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            return ResumeParser.extract_text_from_docx(file_path)
        return ""

    @staticmethod
    def clean_text(text):
        # Remove extra whitespaces and special characters
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\x00-\x7f]', r'', text) # Remove non-ascii
        return text.strip()
