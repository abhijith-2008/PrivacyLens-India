"""Train the PrivacyLens OPP-115 multi-label privacy-practice classifier."""
from pathlib import Path
import argparse
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score

DEFAULT_DATA = Path(__file__).resolve().parent.parent / "opp115_segment_dataset_threshold075.csv"
DEFAULT_OUT = Path(__file__).resolve().parent / "privacylens_model.joblib"


def parse_labels(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [label.strip() for label in str(value).split(";") if label.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    df = df.dropna(subset=["text", "categories"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0].copy()
    labels = [parse_labels(v) for v in df["categories"]]
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(labels)

    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2,
            max_features=100_000, sublinear_tf=True, strip_accents="unicode")),
        ("char_tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5),
            min_df=2, max_features=100_000, sublinear_tf=True, strip_accents="unicode")),
    ])
    classifier = OneVsRestClassifier(LogisticRegression(
        max_iter=2000, class_weight="balanced", C=2.0, solver="liblinear"
    ))
    X = features.fit_transform(df["text"])
    classifier.fit(X, y)

    bundle = {
        "features": features,
        "classifier": classifier,
        "label_binarizer": mlb,
        "threshold": 0.50,
        "categories": list(mlb.classes_),
        "training_rows": int(len(df)),
        "training_policies": int(df["policy_group"].nunique()) if "policy_group" in df else None,
        "dataset_note": "OPP-115 privacy-practice labels; these are not DPDP compliance labels.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, args.output, compress=3)
    print(f"Saved model: {args.output}")
    print(f"Training segments: {len(df)}")
    print(f"Distinct policies: {bundle['training_policies']}")
    print(f"Categories ({len(mlb.classes_)}):")
    for category in mlb.classes_:
        print(f" - {category}")
    print("Note: this deployment model is fitted on all labelled segments. Report the separate held-out evaluation metrics, not training scores.")

if __name__ == "__main__":
    main()
