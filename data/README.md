# Data

The raw dataset is **not** committed to this repository. This is deliberate and is
standard practice: raw data files are kept out of version control to keep the repo
small and to avoid redistributing data whose licence and provenance are unclear.

## How to obtain the data

1. Obtain an open PCOS clinical and hormonal dataset (commonly distributed via Kaggle).
2. Place the CSV file in this `data/` folder.
3. Name it `pcos_clinical.csv`, or update the path near the top of
   `src/data_prep.py` to match your filename.

## Expected shape

The code expects a table where:

- each row is one patient,
- one column is the PCOS label (0 for non-PCOS, 1 for PCOS),
- the remaining columns are clinical, hormonal, or ultrasound-derived features.

If the label column has a different name, set it in `src/data_prep.py`.

## Provenance note

The clinical origin and collection protocol of the common open PCOS dataset are not
well documented in a peer reviewed source. Treat any result built on it as a learning
and portfolio exercise, not as a research or clinical finding about PCOS.
