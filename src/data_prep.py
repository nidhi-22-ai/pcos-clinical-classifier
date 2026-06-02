"""
data_prep.py
------------
Loads the PCOS clinical dataset, runs basic quality checks, and creates a
stratified train/test split.

The most important design choice in this whole project lives here: the test set
is split off BEFORE any feature selection, scaling fit, or model tuning. That is
what stops the inflated accuracy seen in most versions of this analysis.
"""

import os
import pandas as pd
from sklearn.model_selection import train_test_split

# ----------------------------------------------------------------------
# Configuration: change these two lines if your file or label differ.
# ----------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pcos_clinical.csv")
LABEL_COLUMN = "PCOS"          # name of the 0/1 outcome column
TEST_SIZE = 0.25               # fraction held out and never touched during training
RANDOM_STATE = 42              # fixed so the split is reproducible


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load the clinical CSV and return a DataFrame."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find data at {path}. "
            "See data/README.md for how to obtain and place the dataset."
        )
    df = pd.read_csv(path)
    return df


def basic_quality_report(df: pd.DataFrame) -> None:
    """Print a short, honest snapshot of the data before modelling."""
    print("=" * 60)
    print("BASIC DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Rows (patients): {df.shape[0]}")
    print(f"Columns (features + label): {df.shape[1]}")
    print()

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) == 0:
        print("Missing values: none detected.")
    else:
        print("Missing values per column:")
        print(missing.to_string())
    print()

    if LABEL_COLUMN in df.columns:
        counts = df[LABEL_COLUMN].value_counts(dropna=False)
        print(f"Class balance for '{LABEL_COLUMN}':")
        print(counts.to_string())
        # Flag imbalance plainly, because it changes which metrics matter.
        if counts.min() / counts.max() < 0.5:
            print("\nNOTE: classes are imbalanced. Accuracy alone will be misleading.")
            print("ROC AUC and precision-recall AUC are reported for this reason.")
    else:
        print(f"WARNING: label column '{LABEL_COLUMN}' not found. "
              "Set LABEL_COLUMN at the top of data_prep.py.")
    print("=" * 60)
    print()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal, transparent cleaning. Kept deliberately simple and explicit so a
    reader can see exactly what was done. No silent dropping of rows.
    """
    df = df.copy()

    # Drop columns that are obviously identifiers, if present.
    for junk in ["Sl. No", "Patient File No.", "Unnamed: 0"]:
        if junk in df.columns:
            df = df.drop(columns=[junk])

    # Keep only numeric feature columns plus the label. Non-numeric columns are
    # reported, not silently coerced.
    non_numeric = [
        c for c in df.columns
        if c != LABEL_COLUMN and not pd.api.types.is_numeric_dtype(df[c])
    ]
    if non_numeric:
        print(f"Columns that are not numeric and will be dropped: {non_numeric}")
        print("If any of these are important, encode them explicitly before dropping.\n")
        df = df.drop(columns=non_numeric)

    # Fill remaining missing numeric values with the column median, and say so.
    n_missing = int(df.isnull().sum().sum())
    if n_missing > 0:
        print(f"Filling {n_missing} missing numeric value(s) with column medians.\n")
        df = df.fillna(df.median(numeric_only=True))

    return df


def make_split(df: pd.DataFrame):
    """
    Split into X_train, X_test, y_train, y_test.
    Stratified so the class ratio is preserved in both halves.
    """
    if LABEL_COLUMN not in df.columns:
        raise KeyError(
            f"Label column '{LABEL_COLUMN}' not found. "
            "Set LABEL_COLUMN at the top of data_prep.py."
        )

    y = df[LABEL_COLUMN].astype(int)
    X = df.drop(columns=[LABEL_COLUMN])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,            # preserves class ratio in both sets
    )
    print(f"Split done. Train: {X_train.shape[0]} patients, "
          f"Test: {X_test.shape[0]} patients (held out, untouched until final eval).\n")
    return X_train, X_test, y_train, y_test


if __name__ == "__main__":
    data = load_data()
    basic_quality_report(data)
    data = clean(data)
    make_split(data)
