#using pymupdf for text extraction
import fitz  # PyMuPDF
import io
def parser(filepath):
    """
    Extract text directly from a PDF file using PyMuPDF.
    """
    text = ""
    pdf_stream =  io.BytesIO(filepath)
    with fitz.open(stream=pdf_stream, filetype='pdf') as doc:
        for page in doc:
            text += page.get_text() + "\n"
    print("Parser output :",text)
    return text




# from pdf2image import convert_from_bytes
# from PIL import Image
# import pytesseract

# def parser(filepath):
#     """
#     Convert a PDF file to images and extract text from each page.
#     """
#     # Convert PDF to images
#     pages = convert_from_bytes(filepath, dpi=300)

#     all_text = ""
#     for page in pages:
#         # Use pytesseract to extract text from the image
#         text = pytesseract.image_to_string(page)
#         all_text += text + "\n"

#     return all_text