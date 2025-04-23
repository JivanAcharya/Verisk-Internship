from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract

def parser(filepath):
    """
    Convert a PDF file to images and extract text from each page.
    """
    # Convert PDF to images
    pages = convert_from_bytes(filepath, dpi=300)

    all_text = ""
    for page in pages:
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(page)
        all_text += text + "\n"

    return all_text