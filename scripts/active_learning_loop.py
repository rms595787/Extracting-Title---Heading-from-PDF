# scripts/active_learning_loop.py

# It promotes corrected rows from parsed_csv to training_data
# and retrains the model with the updated training data
# This is useful for active learning scenarios where user corrections are incorporated

import os
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Paths
PARSED_INPUT = "parsed_csv/input.csv"
PARSED_OUTPUT = "parsed_csv/output.csv"
TRAIN_INPUT = "training_data/v1/input.csv"
TRAIN_OUTPUT = "training_data/v1/output.csv"
MODEL_PATH = "models/heading_model.pkl"
ENCODER_PATH = "models/label_encoder.pkl"

def promote_corrected_rows():
    print("[INFO] Promoting corrected rows from parsed_csv to training_data...")
    
    parsed_input_df = pd.read_csv(PARSED_INPUT)
    parsed_output_df = pd.read_csv(PARSED_OUTPUT)

    merged_df = pd.merge(parsed_input_df, parsed_output_df, on=["file_name", "page_number", "text"], how="inner")

    os.makedirs(os.path.dirname(TRAIN_INPUT), exist_ok=True)

    if os.path.exists(TRAIN_INPUT):
        input_train_df = pd.read_csv(TRAIN_INPUT)
        output_train_df = pd.read_csv(TRAIN_OUTPUT)

        input_combined = pd.concat([input_train_df, merged_df[parsed_input_df.columns]], ignore_index=True)
        output_combined = pd.concat([output_train_df, merged_df[parsed_output_df.columns]], ignore_index=True)
    else:
        input_combined = merged_df[parsed_input_df.columns]
        output_combined = merged_df[parsed_output_df.columns]

    input_combined.to_csv(TRAIN_INPUT, index=False)
    output_combined.to_csv(TRAIN_OUTPUT, index=False)

    print("[✓] Promoted corrected data to training_data/v1/")

def prepare_features(df):
    df["alignment"] = df["alignment"].fillna("left")
    df = pd.get_dummies(df, columns=["alignment"], drop_first=True)

    df["relative_to_max"] = df["font_size"] / df["font_size"].max()
    df["relative_to_mean"] = df["font_size"] / df["font_size"].mean()
    df["above_std"] = (df["font_size"] - df["font_size"].mean()) / df["font_size"].std()
    df["text_len"] = df["text"].apply(len)

    le = LabelEncoder()
    df["label"] = le.fit_transform(df["level"])

    features = [
        "font_size", "relative_to_max", "relative_to_mean", "above_std",
        "is_bold", "is_italic", "line_spacing_before", "line_spacing_after", 
        "text_len", "y0", "page_number"
    ] + [col for col in df.columns if col.startswith("alignment_")]

    return df[features], df["label"], le

def retrain_model():
    print("[INFO] Retraining model with updated training data...")
    
    df_input = pd.read_csv(TRAIN_INPUT)
    df_output = pd.read_csv(TRAIN_OUTPUT)

    df = pd.merge(df_input, df_output, on=["file_name", "page_number", "text"], how="inner")

    X, y, label_encoder = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    print("[INFO] Evaluating model on test set...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(label_encoder, ENCODER_PATH)

    print(f"[✓] Model saved to: {MODEL_PATH}")
    print(f"[✓] Label encoder saved to: {ENCODER_PATH}")

def main():
    promote_corrected_rows()
    retrain_model()

if __name__ == "__main__":
    main()
