# main.py
import os
import sys
import json
from extract.pdf_outline_extractor import PDFOutlineExtractor

INPUT_DIR = "input"
OUTPUT_DIR = "output"


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_filename>")
        return

    filename = sys.argv[1]
    input_path = os.path.join(INPUT_DIR, filename)

    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline(input_path)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, filename.replace(".pdf", "_outline.json"))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Outline saved to {output_file}")


if __name__ == "__main__":
    main()
