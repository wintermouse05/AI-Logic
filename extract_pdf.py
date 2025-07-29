#!/usr/bin/env python3
import PyPDF2
import sys

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
                
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

if __name__ == "__main__":
    pdf_path = "Project 2.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    
    if extracted_text:
        print(extracted_text)
        
        # Also save to a text file
        with open("project_requirements.txt", "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print("\nText saved to project_requirements.txt")
    else:
        print("Failed to extract text from PDF")
