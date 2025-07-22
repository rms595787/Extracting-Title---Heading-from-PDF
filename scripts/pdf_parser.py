# scripts/pdf_parser.py
# Uses PyMuPDF for structured PDFs
# This script extracts text blocks from a structured PDF using PyMuPDF
# It saves the extracted text blocks as JSON

import fitz  # PyMuPDF
import os
import json

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []
    prev_y1 = {}

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block_id, block in enumerate(blocks):
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span.get("text", "").strip()
                    font_name = span.get("font", "")
                    if not text:
                        continue

                    x0, y0 = span["bbox"][0], span["bbox"][1]
                    x1, y1 = span["bbox"][2], span["bbox"][3]

                    is_bold = "bold" in font_name.lower()
                    is_italic = "italic" in font_name.lower() or "oblique" in font_name.lower()
                    alignment = "indented" if x0 > 100 else "left"
                    if abs((x1 - x0) - page.rect.width) < 50:
                        alignment = "center"

                    line_spacing_before = round(y0 - prev_y1.get(page_num, 0), 2) if page_num in prev_y1 else None
                    prev_y1[page_num] = y1

                    text_blocks.append({
                        "text": text,
                        "font_size": span.get("size"),
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
                        "page_number": page_num + 1,
                        "block_id": block_id,
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
    result = extract_text_blocks(pdf_path)

    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join("extracted_json", f"{filename}_structured.json")

    os.makedirs("extracted_json", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[✓] Structured text saved to: {output_path}")
