"""
run_analysis.py
---------------
Single entry point. Running this one file reproduces the whole analysis:
load -> quality report -> clean -> honest split -> train -> evaluate ->
ROC plot -> calibration plot -> feature importance table.

Usage:
    python src/run_analysis.py
"""

import os
import matplotlib
matplotlib.use("Agg")  # write figures to file without needing a screen
import matplotlib.pyplot as plt
import pandas as pd

import data_prep
import model as M

# Output locations
HERE = os.path.dirname(__file__)
FIG_DIR = os.path.join(HERE, "..", "results", "figures")
TAB_DIR = os.path.join(HERE, "..", "results", "tables")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)


def main():
    # 1. Load and inspect
    df = data_prep.load_data()
    data_prep.basic_quality_report(df)

    # 2. Clean (transparent, no silent row dropping)
    df = data_prep.clean(df)

    # 3. Honest split: test set carved off before anything is learned
    X_train, X_test, y_train, y_test = data_prep.make_split(df)
    feature_names = list(X_train.columns)

    # 4. Build and train models
    models = M.build_models()
    results = []
    roc_curves = {}
    calib_curves = {}

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)             # fit only on training data
        res = M.evaluate(pipe, X_test, y_test, name)
        results.append(res)
        roc_curves[name] = M.roc_points(y_test, res["y_proba"])
        calib_curves[name] = M.calibration_points(y_test, res["y_proba"])

        # Save feature importance per model
        ranked = M.feature_importance(pipe, feature_names, name)
        if ranked is not None:
            imp_df = pd.DataFrame(ranked, columns=["feature", "importance"])
            imp_path = os.path.join(TAB_DIR, f"feature_importance_{name}.csv")
            imp_df.to_csv(imp_path, index=False)
            print(f"Saved feature importance: {imp_path}")
            print("Top 10 features:")
            print(imp_df.head(10).to_string(index=False))
            print("Sanity check: do these match known PCOS clinical markers? "
                  "If the top features are collection artefacts, treat with caution.\n")

    # 5. Save a summary metrics table
    summary = pd.DataFrame([
        {"model": r["name"], "accuracy": r["accuracy"],
         "roc_auc": r["roc_auc"], "pr_auc": r["pr_auc"]}
        for r in results
    ])
    summary_path = os.path.join(TAB_DIR, "model_summary.csv")
    summary.to_csv(summary_path, index=False)
    print(f"Saved metrics summary: {summary_path}\n")

    # 6. ROC curve figure
    plt.figure(figsize=(6, 6))
    for name, (fpr, tpr) in roc_curves.items():
        plt.plot(fpr, tpr, label=name)
    plt.plot([0, 1], [0, 1], "k--", label="random guess")
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("ROC curves (held-out test set)")
    plt.legend()
    plt.tight_layout()
    roc_path = os.path.join(FIG_DIR, "roc_curves.png")
    plt.savefig(roc_path, dpi=150)
    plt.close()
    print(f"Saved figure: {roc_path}")

    # 7. Calibration figure
    plt.figure(figsize=(6, 6))
    for name, (mean_pred, frac_pos) in calib_curves.items():
        plt.plot(mean_pred, frac_pos, marker="o", label=name)
    plt.plot([0, 1], [0, 1], "k--", label="perfectly calibrated")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Observed fraction positive")
    plt.title("Calibration curves (held-out test set)")
    plt.legend()
    plt.tight_layout()
    calib_path = os.path.join(FIG_DIR, "calibration_curves.png")
    plt.savefig(calib_path, dpi=150)
    plt.close()
    print(f"Saved figure: {calib_path}")

    print("\nDone. All outputs are in results/. "
          "Read the limitations section of the README before interpreting anything.")


if __name__ == "__main__":
    main()
