# scripts/ocr_pdf_parser.py

# Uses pdf2image + pytesseract for scanned PDFs
# it extracts text blocks from a scanned PDF using OCR
# using pytesseract and pdf2image libraries
# saves the extracted text blocks as JSON

import pytesseract
from pdf2image import convert_from_path
import os
import json

def ocr_extract_text_blocks(pdf_path, dpi=300):
    images = convert_from_path(pdf_path, dpi=dpi)
    text_blocks = []

    for page_num, image in enumerate(images, start=1):
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        n = len(data['text'])
        prev_y1 = None

        for i in range(n):
            text = data['text'][i].strip()
            if not text:
                continue

            x0 = data['left'][i]
            y0 = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            x1 = x0 + w
            y1 = y0 + h

            font_size = h
            font_name = "OCR"
            is_bold = False
            is_italic = False

            alignment = "indented" if x0 > 100 else "left"
            if w > 500:
                alignment = "center"

            line_spacing_before = round(y0 - prev_y1, 2) if prev_y1 else None
            prev_y1 = y1

            text_blocks.append({
                "text": text,
                "font_size": font_size,
                "font_name": font_name,
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "is_bold": is_bold,
                "is_italic": is_italic,
                "alignment": alignment,
                "line_spacing_before": line_spacing_before,
                "line_spacing_after": None,
                "page_number": page_num,
                "block_id": i
            })

    # Add line_spacing_after
    for i in range(len(text_blocks) - 1):
        if text_blocks[i]["page_number"] == text_blocks[i + 1]["page_number"]:
            text_blocks[i]["line_spacing_after"] = round(text_blocks[i + 1]["y0"] - text_blocks[i]["y1"], 2)

    return {
        "pdf_name": os.path.basename(pdf_path),
        "text_blocks": text_blocks
    }

if __name__ == "__main__":
    import sys
    pdf_path = sys.argv[1]
    result = ocr_extract_text_blocks(pdf_path)

    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join("extracted_json", f"{filename}_ocr.json")

    os.makedirs("extracted_json", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[✓] OCR text saved to: {output_path}")
