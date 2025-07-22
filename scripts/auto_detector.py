# scripts/auto_detector.py

# Detects whether a pdf file is scanned or structured
# and extracts text blocks accordingly
import os
import fitz  # PyMuPDF
import json
from scripts.pdf_parser import extract_text_blocks
from scripts.ocr_pdf_parser import ocr_extract_text_blocks

def is_scanned_pdf(pdf_path: str, max_pages_to_check: int = 3, threshold_empty_ratio: float = 0.9) -> bool:
    """
    Checks if a PDF is scanned by analyzing text presence on the first few pages.
    """
    doc = fitz.open(pdf_path)
    empty_pages = 0

    for page_num in range(min(len(doc), max_pages_to_check)):
        page = doc[page_num]
        text = page.get_text().strip()
        if len(text) < 10:
            empty_pages += 1

    ratio = empty_pages / min(len(doc), max_pages_to_check)
    return ratio >= threshold_empty_ratio


def detect_pdf_type_and_extract(pdf_path: str) -> str:
    """
    Detects whether the PDF is scanned or structured and extracts content accordingly.
    Saves the extracted text blocks as JSON and returns the output file path.
    """
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs("extracted_json", exist_ok=True)

    if is_scanned_pdf(pdf_path):
        print(f"🔍 Detected scanned PDF → using OCR for: {filename}.pdf")
        result = ocr_extract_text_blocks(pdf_path)
        output_file = f"extracted_json/{filename}_ocr.json"
    else:
        print(f"🧾 Detected structured PDF → using direct extraction for: {filename}.pdf")
        result = extract_text_blocks(pdf_path)
        output_file = f"extracted_json/{filename}_structured.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[✓] Saved extracted JSON to: {output_file}")
    return output_file
