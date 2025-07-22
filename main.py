# main.py
<<<<<<< HEAD
import sys
import os
from scripts.auto_detector import detect_pdf_type_and_extract
from scripts.generate_csv import generate_input_csv
from scripts.heading_detector import detect_headings

INPUT_PDF_DIR = "input_pdfs"
OUTPUT_JSON_DIR = "parsed_csv/output_json"  # ✅ output JSON moved inside parsed_csv
PARSED_CSV_DIR = "parsed_csv/input_json"    # ✅ input JSON moved inside parsed_csv
MODEL_PATH = "models/heading_model.pkl"
LABEL_ENCODER_PATH = "models/label_encoder.pkl"

def get_pdf_name(pdf_path):
    return os.path.splitext(os.path.basename(pdf_path))[0]

def main(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return

    pdf_name = get_pdf_name(pdf_path)
    print(f"[INFO] Processing PDF: {pdf_name}")

    # Step 1: Extract JSON using auto-detector
    input_json_path = detect_pdf_type_and_extract(pdf_path)

    # Move input_json to parsed_csv/input_json
    os.makedirs(PARSED_CSV_DIR, exist_ok=True)
    input_json_target = os.path.join(PARSED_CSV_DIR, f"{pdf_name}.json")
    os.rename(input_json_path, input_json_target)

    # Step 2: Generate input.csv from input_json
    input_csv_path = "parsed_csv/input.csv"
    generate_input_csv(PARSED_CSV_DIR, input_csv_path)

    # Step 3: Run heading detection
    output_json_path = os.path.join(OUTPUT_JSON_DIR, f"{pdf_name}.json")
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    detect_headings(input_json_target, MODEL_PATH, LABEL_ENCODER_PATH, output_json_path)

    print(f"[✓] Processing complete.\nInput JSON → {input_json_target}\nOutput JSON → {output_json_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py input_pdfs/yourfile.pdf")
    else:
        os.makedirs(INPUT_PDF_DIR, exist_ok=True)
        main(sys.argv[1])
=======
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
>>>>>>> 7a8c88b8e6cfd8145055e0a2c56349ef372becfa
