"""
model.py
--------
Model definitions and honest evaluation helpers.

Design choices that matter:
- Scaling is fit on the training data only, inside a pipeline, so the test set
  never leaks into preprocessing.
- We report ROC AUC and precision-recall AUC, not just accuracy.
- We produce a calibration curve to check whether predicted probabilities mean
  anything.
"""

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    average_precision_score,
    roc_curve,
    confusion_matrix,
    classification_report,
)
from sklearn.calibration import calibration_curve


def build_models(random_state: int = 42) -> dict:
    """
    Return a dictionary of named model pipelines.

    Logistic regression is the interpretable baseline. A reader should always be
    able to ask 'is the fancy model actually beating a simple one?'
    Random forest is the comparison.
    """
    models = {
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, random_state=random_state)),
        ]),
        "random_forest": Pipeline([
            ("scaler", StandardScaler()),  # harmless for trees, keeps pipeline uniform
            ("clf", RandomForestClassifier(
                n_estimators=300,
                random_state=random_state,
            )),
        ]),
    }
    return models


def evaluate(model, X_test, y_test, name: str) -> dict:
    """Evaluate one fitted model on the held-out test set and print honest metrics."""
    y_pred = model.predict(X_test)
    # predict_proba for the positive class, needed for AUC and calibration
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_proba)
    pr = average_precision_score(y_test, y_proba)

    print("-" * 60)
    print(f"MODEL: {name}")
    print("-" * 60)
    print(f"Accuracy          : {acc:.3f}   (can be misleading on imbalanced data)")
    print(f"ROC AUC           : {roc:.3f}")
    print(f"PR AUC (avg prec) : {pr:.3f}   (more honest when positives are rarer)")
    print()
    print("Confusion matrix (rows = true, cols = predicted):")
    print(confusion_matrix(y_test, y_pred))
    print()
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=3))
    print()

    return {
        "name": name,
        "accuracy": acc,
        "roc_auc": roc,
        "pr_auc": pr,
        "y_proba": y_proba,
        "y_pred": y_pred,
    }


def roc_points(y_test, y_proba):
    """Return false-positive and true-positive rates for plotting an ROC curve."""
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    return fpr, tpr


def calibration_points(y_test, y_proba, n_bins: int = 10):
    """
    Return points for a calibration curve.

    A well-calibrated model: when it says 0.8, about 80 percent of those cases are
    truly positive. Most PCOS repos never check this. We do.
    """
    frac_pos, mean_pred = calibration_curve(y_test, y_proba, n_bins=n_bins)
    return mean_pred, frac_pos


def feature_importance(model, feature_names, name: str):
    """
    Return a simple, honest importance ranking.

    For logistic regression: absolute coefficient size (after scaling).
    For random forest: built-in impurity importance.
    SHAP is added separately in run_analysis if the library is available, because
    it is more trustworthy but heavier to compute.
    """
    clf = model.named_steps["clf"]
    if hasattr(clf, "coef_"):
        importances = np.abs(clf.coef_[0])
    elif hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
    else:
        return None

    order = np.argsort(importances)[::-1]
    ranked = [(feature_names[i], float(importances[i])) for i in order]
    return ranked
