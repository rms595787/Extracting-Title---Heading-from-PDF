# scripts/generate_csv.py

# This helpes generate input and output CSV files
# from the JSON files in extracted_json/ and output_json/
# for training the heading detection model
# scripts/generate_csv.py
# Generates input and output CSV files from extracted JSON
# scripts/generate_csv.py

import os
import json
import csv
import argparse

def parse_input_json_file(json_file):
    rows = []
    with open(json_file, 'r') as f:
        data = json.load(f)
        pdf_name = data.get("pdf_name", os.path.basename(json_file).replace(".json", ".pdf"))
        for block in data.get("text_blocks", []):
            rows.append({
                "file_name": pdf_name,
                "page_number": block.get("page_number"),
                "text": block.get("text"),
                "font_size": block.get("font_size"),
                "font_name": block.get("font_name"),
                "x0": block.get("x0"),
                "y0": block.get("y0"),
                "x1": block.get("x1"),
                "y1": block.get("y1"),
                "is_bold": "Bold" in block.get("font_name", ""),
                "is_italic": "Italic" in block.get("font_name", "") or "Oblique" in block.get("font_name", ""),
                "alignment": block.get("alignment"),
                "line_spacing_before": block.get("line_spacing_before"),
                "line_spacing_after": block.get("line_spacing_after")
            })
    return rows

def generate_input_csv(json_input, output_csv):
    rows = []

    if os.path.isdir(json_input):
        for file in os.listdir(json_input):
            if file.endswith(".json"):
                file_path = os.path.join(json_input, file)
                rows.extend(parse_input_json_file(file_path))
    else:
        rows.extend(parse_input_json_file(json_input))

    if not rows:
        print(f"[!] No valid text blocks found in: {json_input}")
        return

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] Input CSV saved to: {output_csv}")

def parse_output_json_file(json_file):
    rows = []
    with open(json_file, 'r') as f:
        data = json.load(f)
        pdf_name = data.get("title", os.path.basename(json_file).replace(".json", ".pdf"))
        for item in data.get("outline", []):
            rows.append({
                "file_name": pdf_name,
                "page_number": item.get("page"),
                "text": item.get("text"),
                "level": item.get("level")
            })
    return rows

def generate_output_csv(json_input, output_csv):
    rows = []

    if os.path.isdir(json_input):
        for file in os.listdir(json_input):
            if file.endswith(".json"):
                file_path = os.path.join(json_input, file)
                rows.extend(parse_output_json_file(file_path))
    else:
        rows.extend(parse_output_json_file(json_input))

    if not rows:
        print(f"[!] No valid headings found in: {json_input}")
        return

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] Output CSV saved to: {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate input/output CSV files for training")
    parser.add_argument("--mode", choices=["input", "output"], required=True, help="Choose mode: input or output")
    parser.add_argument("--json_dir", default="extracted_json", help="Path to JSON file or directory")
    parser.add_argument("--output_csv", default=None, help="Output CSV file path")

    args = parser.parse_args()

    if args.mode == "input":
        out_path = args.output_csv or "parsed_csv/input.csv"
        generate_input_csv(args.json_dir, out_path)

    elif args.mode == "output":
        out_path = args.output_csv or "parsed_csv/output.csv"
        generate_output_csv(args.json_dir, out_path)
