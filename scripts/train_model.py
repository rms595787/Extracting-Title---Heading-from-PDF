# scripts/train_model.py

# Trains Gradient Boost model on training_data/
# This is the script to train the heading detection model
# It reads the input CSV, prepares features, trains a model,
# and saves the trained model and label encoder
# scripts/train_model.py

import pandas as pd
import joblib
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def load_and_merge_data(input_csv, output_csv):
    input_df = pd.read_csv(input_csv)
    output_df = pd.read_csv(output_csv)

    # Ensure page_number is int for consistent merge
    input_df["page_number"] = input_df["page_number"].astype(int)
    output_df["page_number"] = output_df["page_number"].astype(int)

    # Merge on keys
    merged_df = pd.merge(input_df, output_df, on=["file_name", "page_number", "text"], how="inner")
    return merged_df

def prepare_features(df):
    df["alignment"] = df.get("alignment", "left").fillna("left")
    df = pd.get_dummies(df, columns=["alignment"], drop_first=True)

    # Fill missing with 0 or appropriate value
    df["is_bold"] = df.get("is_bold", 0)
    df["is_italic"] = df.get("is_italic", 0)
    df["line_spacing_before"] = df.get("line_spacing_before", 0)
    df["line_spacing_after"] = df.get("line_spacing_after", 0)

    # Encode labels
    le = LabelEncoder()
    df["label"] = le.fit_transform(df["level"])

    # Base features
    features = [
        "font_size", "relative_to_max", "relative_to_mean", "above_std",
        "is_bold", "is_italic", "line_spacing_before", "line_spacing_after",
        "text_len", "y0", "page_number"
    ] + [col for col in df.columns if col.startswith("alignment_")]

    return df[features], df["label"], le

def main():
    INPUT_CSV = "training_data/v1/input.csv"
    OUTPUT_CSV = "training_data/v1/output.csv"
    MODEL_PATH = "models/heading_model.pkl"
    LABEL_ENCODER_PATH = "models/label_encoder.pkl"

    print("[INFO] Loading training data...")
    df = load_and_merge_data(INPUT_CSV, OUTPUT_CSV)

    print("[INFO] Preparing features...")
    df["relative_to_max"] = df["font_size"] / df["font_size"].max()
    df["relative_to_mean"] = df["font_size"] / df["font_size"].mean()
    df["above_std"] = (df["font_size"] - df["font_size"].mean()) / df["font_size"].std()
    df["text_len"] = df["text"].apply(len)

    X, y, label_encoder = prepare_features(df)

    print("[INFO] Splitting train/test set...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("[INFO] Training Gradient Boosting Classifier...")
    model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    print("[INFO] Evaluating model...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    print(f"[✓] Model saved to: {MODEL_PATH}")
    print(f"[✓] Label encoder saved to: {LABEL_ENCODER_PATH}")

if __name__ == "__main__":
    main()
