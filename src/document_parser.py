import os
import fitz
import docx

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file using PyMuPDF.
    
    Args:
        file_path (str): The absolute or relative path to the PDF file.
        
    Returns:
        str: The extracted text from all pages of the PDF.
    """
    #initialize an empty string to hold the text
    extracted_text = ""
    
    try:
        #open the pdf document
        pdf_document = fitz.open(file_path)
        
        #iterate through every page in the document
        for page_num in range(len(pdf_document)):
            #load the current page
            page = pdf_document.load_page(page_num)
            
            #extract text and append it to our string
            extracted_text += page.get_text()
            
        #close the document to free up memory
        pdf_document.close()
        
    except Exception as e:
        #handle potential file reading errors gracefully
        return f"error reading pdf: {str(e)}"
        
    return extracted_text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts raw text from a DOCX file using python-docx.
    
    Args:
        file_path (str): The absolute or relative path to the DOCX file.
        
    Returns:
        str: The extracted text from all paragraphs in the document.
    """
    #initialize an empty list to hold paragraphs
    text_paragraphs = []
    
    try:
        #load the word document
        word_document = docx.Document(file_path)
        
        #iterate through all paragraphs in the document
        for paragraph in word_document.paragraphs:
            #append the paragraph text to our list if it is not empty
            if paragraph.text.strip():
                text_paragraphs.append(paragraph.text)
                
    except Exception as e:
        #handle potential file reading errors gracefully
        return f"error reading docx: {str(e)}"
        
    #join the paragraphs with a newline character
    return "\n".join(text_paragraphs)

def parse_document(file_path: str) -> str:
    """
    Determines the file type and routes it to the appropriate text extraction function.
    
    Args:
        file_path (str): The path to the document file.
        
    Returns:
        str: The extracted raw text, or an error message if the format is unsupported.
    """
    #check if the file actually exists
    if not os.path.exists(file_path):
        return f"error: file not found at {file_path}"
        
    #convert file path to lower case to handle extensions like .PDF or .Docx
    file_path_lower = file_path.lower()
    
    #route based on file extension
    if file_path_lower.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path_lower.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        #return an error for unsupported file types
        return "error: unsupported file format. please provide a .pdf or .docx file."