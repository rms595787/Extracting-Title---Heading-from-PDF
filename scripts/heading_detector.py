# scripts/heading_detector.py

# Uses model + heuristics to detect headings from input features
# this is the logic for detecting headings in a PDF
# using a trained model
# it extracts text blocks, computes features, and predicts headings
import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import List, Dict

# Keywords to filter out noisy or irrelevant content
IGNORE_TEXTS = ["author", "date", "page", "footer", "header", "contact", "copyright", "www.", "@", ".com"]

def is_noise(text: str) -> bool:
    text_lower = text.lower()
    return (
        any(keyword in text_lower for keyword in IGNORE_TEXTS)
        or text.strip().isdigit()
        or len(text.strip()) < 3
    )

def get_font_stats(blocks: List[Dict]) -> Dict:
    font_sizes = [b["font_size"] for b in blocks if not is_noise(b["text"])]
    return {
        "max_font": max(font_sizes),
        "mean_font": np.mean(font_sizes),
        "std_font": np.std(font_sizes)
    }

def extract_features(blocks: List[Dict], font_stats: Dict, title_text: str = None):
    rows = []
    for block in blocks:
        text = block.get("text", "")
        if is_noise(text):
            continue
        if title_text and text.strip() == title_text.strip():
            continue

        row = {
            "font_size": block.get("font_size"),
            "relative_to_max": block.get("font_size") / font_stats["max_font"],
            "relative_to_mean": block.get("font_size") / font_stats["mean_font"],
            "above_std": (block.get("font_size") - font_stats["mean_font"]) / font_stats["std_font"],
            "text_len": len(text),
            "is_bold": int("Bold" in block.get("font_name", "")),
            "is_italic": int("Italic" in block.get("font_name", "") or "Oblique" in block.get("font_name", "")),
            "alignment": block.get("alignment", "left"),
            "line_spacing_before": block.get("line_spacing_before", 0.0),
            "line_spacing_after": block.get("line_spacing_after", 0.0),
            "y0": block.get("y0", 0.0),
            "page_number": block.get("page_number", 1),
            "text": text
        }
        rows.append((block, row))
    return rows

def detect_headings(input_json_path: str, model_path: str, label_encoder_path: str, output_json_path: str):
    # Load JSON data
    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    blocks = data.get("text_blocks", [])
    pdf_name = data.get("pdf_name", "unknown.pdf")

    if not blocks:
        print(f"[!] No text blocks found in {input_json_path}")
        return

    # Step 1: Font stats for heuristic features
    font_stats = get_font_stats(blocks)

    # Step 2: Title detection from page 1
    page1_blocks = [b for b in blocks if b.get("page_number") == 1 and not is_noise(b.get("text", ""))]
    title_block = max(page1_blocks, key=lambda b: b.get("font_size", 0), default=None)
    title_text = title_block.get("text") if title_block else None

    # Step 3: Extract and prepare features
    features_data = extract_features(blocks, font_stats, title_text)
    if not features_data:
        print(f"[!] No valid text blocks found in {input_json_path}")
        return

    blocks_filtered, feature_rows = zip(*features_data)
    df = pd.DataFrame(feature_rows)

    # Step 4: One-hot encode alignment and prepare input
    df["alignment"] = df["alignment"].fillna("left")
    df = pd.get_dummies(df, columns=["alignment"], drop_first=True)
    X = df.drop(columns=["text", "page_number"])

    # Step 5: Load trained model and label encoder
    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)

    y_pred = model.predict(X)
    y_labels = label_encoder.inverse_transform(y_pred)

    # Step 6: Build structured output
    outline = []
    for i, label in enumerate(y_labels):
        if label == "None":
            continue
        outline.append({
            "level": label,
            "text": blocks_filtered[i]["text"],
            "page": blocks_filtered[i]["page_number"]
        })

    output_data = {
        "title": title_text or "Untitled",
        "outline": outline
    }

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"[✓] Output saved to {output_json_path}")
