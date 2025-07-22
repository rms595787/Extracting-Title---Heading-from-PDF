# scripts/evaluate_model.py

# this file evaluates the trained model on the test set
# comapres the predicted headings with the actual headings
# and generates a classification report and confusion matrix
import pandas as pd
import joblib
import os
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(input_csv, output_csv):
    input_df = pd.read_csv(input_csv)
    output_df = pd.read_csv(output_csv)

    df = pd.merge(input_df, output_df, on=["file_name", "page_number", "text"], how="inner")
    return df

def prepare_features(df, label_encoder):
    df["relative_to_max"] = df["font_size"] / df["font_size"].max()
    df["relative_to_mean"] = df["font_size"] / df["font_size"].mean()
    df["above_std"] = (df["font_size"] - df["font_size"].mean()) / df["font_size"].std()
    df["text_len"] = df["text"].apply(len)
    df["alignment"] = df["alignment"].fillna("left")
    df = pd.get_dummies(df, columns=["alignment"], drop_first=True)

    features = [
        "font_size", "relative_to_max", "relative_to_mean", "above_std",
        "is_bold", "is_italic", "line_spacing_before", "line_spacing_after", 
        "text_len", "y0", "page_number"
    ] + [col for col in df.columns if col.startswith("alignment_")]

    X = df[features]
    y_true = label_encoder.transform(df["level"])
    return X, y_true

def plot_confusion_matrix(y_true, y_pred, labels, title="Confusion Matrix"):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.savefig("evaluation/confusion_matrix.png")
    print("[✓] Saved confusion matrix to evaluation/confusion_matrix.png")

def plot_classification_metrics(report_dict, title="Per-Class Metrics"):
    metrics_df = pd.DataFrame(report_dict).T.drop(index=["accuracy"])
    metrics_df[["precision", "recall", "f1-score"]].plot.bar(figsize=(10, 6))
    plt.title(title)
    plt.ylabel("Score")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("evaluation/classification_report.png")
    print("[✓] Saved classification chart to evaluation/classification_report.png")

def main():
    INPUT_CSV = "parsed_csv/input.csv"
    OUTPUT_CSV = "parsed_csv/output.csv"
    MODEL_PATH = "models/heading_model.pkl"
    LABEL_ENCODER_PATH = "models/label_encoder.pkl"

    print("[INFO] Loading model and data...")
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    df = load_data(INPUT_CSV, OUTPUT_CSV)
    X, y_true = prepare_features(df, label_encoder)

    print("[INFO] Predicting...")
    y_pred = model.predict(X)

    print("[INFO] Generating classification report...")
    report_dict = classification_report(y_true, y_pred, output_dict=True, target_names=label_encoder.classes_)
    print(classification_report(y_true, y_pred, target_names=label_encoder.classes_))

    os.makedirs("evaluation", exist_ok=True)

    print("[INFO] Plotting results...")
    plot_confusion_matrix(y_true, y_pred, label_encoder.classes_)
    plot_classification_metrics(report_dict)

if __name__ == "__main__":
    main()