"""
run_analysis_no_follicle.py
---------------------------
A second version of the analysis that removes the two follicle-count columns
(Follicle No. (L) and Follicle No. (R)) before training.

WHY THIS EXISTS
In the first analysis, follicle count was by far the strongest predictor. But
follicle count (polycystic ovarian morphology) is itself one of the Rotterdam
diagnostic criteria for PCOS. So a model leaning on it is partly re-learning the
definition of the label, a soft form of label leakage.

This script answers a concrete question: how much of the model's performance
depended on that near-diagnostic feature? We remove the two follicle columns and
re-run the exact same pipeline. Then we compare the ROC AUC against the original.

- If ROC AUC stays high: the model has real independent signal from genuine
  clinical symptoms.
- If ROC AUC drops sharply: performance was driven largely by the leaked feature.

Everything else (the split, the random seed, the models) is identical to the
original, so the comparison is fair.

Usage (from the project folder, with pcos-clf active):
    python src/run_analysis_no_follicle.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import data_prep
import model as M

# Columns to drop for this experiment. We match flexibly in case of stray spaces.
FOLLICLE_KEYWORDS = ["follicle no"]

HERE = os.path.dirname(__file__)
FIG_DIR = os.path.join(HERE, "..", "results", "figures")
TAB_DIR = os.path.join(HERE, "..", "results", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)


def drop_follicle_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove any column whose name mentions follicle number."""
    to_drop = []
    for col in df.columns:
        name = str(col).strip().lower()
        if any(k in name for k in FOLLICLE_KEYWORDS):
            to_drop.append(col)
    if to_drop:
        print(f"Dropping follicle-count column(s) for this experiment: {to_drop}\n")
        df = df.drop(columns=to_drop)
    else:
        print("WARNING: no follicle-count columns found to drop. "
              "Check the column names in your data.\n")
    return df


def main():
    print("=" * 64)
    print("SECOND ANALYSIS: follicle-count columns REMOVED")
    print("Testing how much performance depended on the near-diagnostic feature")
    print("=" * 64 + "\n")

    # 1. Load and inspect (same as original)
    df = data_prep.load_data()
    data_prep.basic_quality_report(df)

    # 2. Clean (same transparent cleaning as original)
    df = data_prep.clean(df)

    # 3. THE ONLY DIFFERENCE: drop the follicle-count columns
    df = drop_follicle_columns(df)

    # 4. Same honest split (same RANDOM_STATE means the same patients are held out)
    X_train, X_test, y_train, y_test = data_prep.make_split(df)
    feature_names = list(X_train.columns)

    # 5. Same two models
    models = M.build_models()
    results = []
    roc_curves = {}
    calib_curves = {}

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        res = M.evaluate(pipe, X_test, y_test, name)
        results.append(res)
        roc_curves[name] = M.roc_points(y_test, res["y_proba"])
        calib_curves[name] = M.calibration_points(y_test, res["y_proba"])

        ranked = M.feature_importance(pipe, feature_names, name)
        if ranked is not None:
            imp_df = pd.DataFrame(ranked, columns=["feature", "importance"])
            imp_path = os.path.join(TAB_DIR, f"feature_importance_{name}_no_follicle.csv")
            imp_df.to_csv(imp_path, index=False)
            print(f"Saved feature importance: {imp_path}")
            print("Top 10 features (follicle removed):")
            print(imp_df.head(10).to_string(index=False))
            print()

    # 6. Save summary with a clear label
    summary = pd.DataFrame([
        {"model": r["name"], "accuracy": r["accuracy"],
         "roc_auc": r["roc_auc"], "pr_auc": r["pr_auc"]}
        for r in results
    ])
    summary_path = os.path.join(TAB_DIR, "model_summary_no_follicle.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved metrics summary: {summary_path}\n")

    # 7. ROC figure (clearly named)
    plt.figure(figsize=(6, 6))
    for name, (fpr, tpr) in roc_curves.items():
        plt.plot(fpr, tpr, label=name)
    plt.plot([0, 1], [0, 1], "k--", label="random guess")
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("ROC curves (follicle columns removed)")
    plt.legend()
    plt.tight_layout()
    roc_path = os.path.join(FIG_DIR, "roc_curves_no_follicle.png")
    plt.savefig(roc_path, dpi=150)
    plt.close()
    print(f"Saved figure: {roc_path}")

    # 8. Print a direct comparison reminder
    print("\n" + "=" * 64)
    print("COMPARE THESE NUMBERS AGAINST THE ORIGINAL RUN:")
    print("  Original ROC AUC was about 0.940 (logistic) and 0.945 (forest).")
    print("  See the numbers above for the follicle-removed version.")
    print("  The size of the drop tells you how much the model leaned on")
    print("  the near-diagnostic follicle feature.")
    print("=" * 64)


if __name__ == "__main__":
    main()
