"""
convert_pcos_excel.py
---------------------
One-time helper to turn the Kaggle PCOS Excel file into a clean CSV that the
analysis code can read.

Why this exists:
- The analysis expects a CSV, but Kaggle gives this dataset as .xlsx.
- This file is known to contain a stray empty column and one or two numeric
  columns accidentally stored as text. This script reports those and fixes the
  obvious ones, WITHOUT silently changing real values.

Usage (run from inside the project folder, with the pcos-clf environment active):
    python convert_pcos_excel.py "data/PCOS_data_without_infertility.xlsx"

It writes: data/pcos_clinical.csv
"""

import sys
import os
import pandas as pd


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_pcos_excel.py <path-to-xlsx>")
        sys.exit(1)

    xlsx_path = sys.argv[1]
    if not os.path.exists(xlsx_path):
        print(f"File not found: {xlsx_path}")
        sys.exit(1)

    # A workbook may have several sheets (this dataset has an 'Instructions'
    # sheet and a data sheet). We pick the sheet that actually contains the
    # data, identified by having a column that mentions PCOS, rather than
    # blindly taking the first sheet.
    xls = pd.ExcelFile(xlsx_path)
    print(f"Sheets found: {xls.sheet_names}")

    chosen_sheet = None
    for sheet in xls.sheet_names:
        peek = pd.read_excel(xlsx_path, sheet_name=sheet, nrows=1)
        if any("PCOS" in str(c).upper() for c in peek.columns):
            chosen_sheet = sheet
            break

    if chosen_sheet is None:
        # fall back to the sheet with the most columns (the data sheet)
        widths = {s: pd.read_excel(xlsx_path, sheet_name=s, nrows=1).shape[1]
                  for s in xls.sheet_names}
        chosen_sheet = max(widths, key=widths.get)
        print(f"No PCOS column found by name; using widest sheet: [{chosen_sheet}]")
    else:
        print(f"Using data sheet: [{chosen_sheet}]")

    df = pd.read_excel(xlsx_path, sheet_name=chosen_sheet)

    # Strip leading/trailing spaces from column names (this dataset has several,
    # e.g. 'Height(Cm) ' and ' Age (yrs)').
    df.columns = [str(c).strip() for c in df.columns]

    print(f"\nLoaded {df.shape[0]} rows and {df.shape[1]} columns.")
    print("\nColumn names exactly as they appear:")
    for c in df.columns:
        print(f"  [{c}]")

    # 1. Drop fully empty columns (the known stray 'Unnamed' column).
    empty_cols = [c for c in df.columns if df[c].isnull().all()]
    if empty_cols:
        print(f"\nDropping fully empty column(s): {empty_cols}")
        df = df.drop(columns=empty_cols)

    # Also drop any leftover unnamed columns that are not real features.
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed:
        print(f"Dropping unnamed column(s): {unnamed}")
        df = df.drop(columns=unnamed)

    # 2. Report columns stored as text that look numeric, and convert them.
    #    We convert with errors='coerce' so anything truly non-numeric becomes
    #    blank rather than crashing. We report how many values that affects, so
    #    nothing is changed silently.
    for c in df.columns:
        if df[c].dtype == object:
            converted = pd.to_numeric(df[c], errors="coerce")
            n_bad = converted.isnull().sum() - df[c].isnull().sum()
            if converted.notnull().sum() > 0:
                # column is mostly numeric stored as text
                if n_bad > 0:
                    print(f"\nColumn [{c}] looks numeric but {int(n_bad)} value(s) "
                          f"could not be parsed and will become blank.")
                df[c] = converted

    # 3. Drop obvious identifier columns so they are never used as features.
    for junk in ["Sl. No", "Sl.No", "Patient File No.", "Patient File No"]:
        if junk in df.columns:
            print(f"Dropping identifier column: [{junk}]")
            df = df.drop(columns=[junk])

    # 4. Standardise the label column name to exactly 'PCOS' (0/1), so the
    #    analysis code works without any edits. We only rename; we do not
    #    change any values.
    label_candidates = [c for c in df.columns if "PCOS" in str(c).upper()]
    if len(label_candidates) == 1:
        original = label_candidates[0]
        if original != "PCOS":
            print(f"\nRenaming label column [{original}] to [PCOS] for convenience.")
            df = df.rename(columns={original: "PCOS"})
    elif len(label_candidates) > 1:
        print(f"\nWARNING: more than one column mentions PCOS: {label_candidates}.")
        print("Pick the 0/1 diagnosis column and rename it to 'PCOS' yourself, "
              "or set LABEL_COLUMN in src/data_prep.py.")

    out_path = os.path.join("data", "pcos_clinical.csv")
    df.to_csv(out_path, index=False)
    print(f"\nClean CSV written to: {out_path}")
    print("\nFirst 3 rows of the cleaned data:")
    print(df.head(3).to_string())

    # Confirm the label is present and report class balance.
    if "PCOS" in df.columns:
        print(f"\nLabel column 'PCOS' is ready. Class balance:")
        print(df["PCOS"].value_counts().to_string())
        print("\nYou can now run: python src/run_analysis.py")
    else:
        print("\nNo single 'PCOS' label column was set. Open the column list above "
              "and set LABEL_COLUMN in src/data_prep.py to the correct name.")


if __name__ == "__main__":
    main()
