# Results and Discussion

Honest evaluation of a machine learning model on an open PCOS clinical dataset.

> **Provenance caveat:** the clinical origin and collection protocol of this dataset
> are not well documented in a peer-reviewed source. All results below are a learning
> and portfolio exercise, not a clinical or research claim about PCOS diagnosis.

---

## 1. Dataset and setup

- **Patients:** 541 women, from an open PCOS clinical and hormonal dataset (Kaggle).
- **Features:** after removing identifier columns and one non-numeric column
  (Blood Group), 40 clinical and hormonal features were kept alongside the binary
  PCOS label.
- **Class balance:** imbalanced, 364 non-PCOS vs 177 PCOS. Because of this,
  accuracy alone is unreliable, so ROC AUC and PR AUC are the primary metrics.
- **Missing values:** 4 missing numeric values (marriage status, beta-HCG, AMH,
  fast food intake) were filled with column medians.
- **Split:** a stratified split held out 136 patients (25%) as a test set that was
  never used during training or model selection.
- **Models:** logistic regression (interpretable baseline) and random forest.

---

## 2. Results

### 2.1 Performance on the held-out test set

| Metric | Logistic regression | Random forest |
|---|---|---|
| Accuracy | 0.882 | 0.897 |
| ROC AUC | 0.940 | 0.945 |
| PR AUC (average precision) | 0.915 | 0.928 |

Both models performed similarly, with the random forest marginally ahead. The
closeness of a simple linear model and a more complex ensemble indicates the
predictive signal is genuine and not an artifact of an over-powered model.

### 2.2 Confusion matrix (random forest, test set)

|  | Predicted non-PCOS | Predicted PCOS |
|---|---|---|
| **Actual non-PCOS** | 90 | 2 |
| **Actual PCOS** | 12 | 32 |

Of the 44 true PCOS patients in the test set, the model correctly identified 32 and
missed 12. That is a **recall of 0.73** for the PCOS class. The model is accurate
overall but misses about a quarter of true cases, a limitation the headline accuracy
of 0.897 conceals.

### 2.3 Top features by importance

| Rank | Logistic regression | Random forest |
|---|---|---|
| 1 | Follicle No. (R) | Follicle No. (R) |
| 2 | Hair growth (Y/N) | Follicle No. (L) |
| 3 | Weight gain (Y/N) | Skin darkening (Y/N) |
| 4 | Cycle (R/I) | Hair growth (Y/N) |
| 5 | Skin darkening (Y/N) | Weight gain (Y/N) |
| 6 | Follicle No. (L) | AMH (ng/mL) |

Both models ranked ovarian follicle counts as the strongest predictors by a clear
margin, followed by signs of androgen excess (hair growth, skin darkening, weight
gain) and cycle irregularity.

---

## 3. Discussion

### 3.1 The model is good, but not a diagnostic tool

An ROC AUC near 0.94 indicates strong discrimination on this dataset. But recall of
0.73 means the model would miss about a quarter of true cases, which is unacceptable
for standalone diagnostic use. More fundamentally, the performance must be read in
light of how the most important feature relates to the diagnosis itself (below).

### 3.2 The follicle-count leakage problem (the key point)

The single strongest predictor in both models was ovarian follicle count. This is
**not an independent discovery**. Ovarian follicle count, as polycystic ovarian
morphology on ultrasound, is one of the defining diagnostic criteria for PCOS.

Based on articles retrieved from PubMed, the 2003 Rotterdam consensus established
that PCOS is diagnosed when at least two of three cardinal features are present:
oligo- or anovulation, clinical or biochemical hyperandrogenism, and polycystic
ovarian morphology. The consensus was published simultaneously in 2004 in
*Fertility and Sterility*
([DOI](https://doi.org/10.1016/j.fertnstert.2003.10.004)) and in
*Human Reproduction* ([DOI](https://doi.org/10.1093/humrep/deh098)).

Because follicle count is part of the criteria used to assign the PCOS label in the
first place, a model that relies heavily on it is partly **re-learning the definition
of the outcome** rather than predicting it from independent information. This is a
soft form of label leakage. It is not a coding error, but it constrains the claim:
the model cannot be described as predicting PCOS from independent clinical signals
while follicle counts are among its inputs.

The other top features behave differently. Hyperandrogenic signs (hair growth, skin
darkening, weight gain) and cycle irregularity are clinical *manifestations* of PCOS,
not parts of the imaging-based diagnostic measurement, so their predictive value is
more defensible. The model relies on a mixture of one near-circular feature and
several legitimate ones.

### 3.3 Why the honest accuracy is lower than published reports

Many published analyses of this dataset report 96 to 99% accuracy. The lower figure
here (about 0.88 to 0.90) is a consequence of methodological discipline, not a weaker
model. A genuine test set was held out before any feature selection or tuning,
removing the optimistic bias that arises when the same data informs both model
building and evaluation. A lower but trustworthy estimate beats a higher but inflated
one.

---

## 4. Limitations

- Dataset provenance is weakly documented; metrics describe this dataset, not PCOS
  in the general population.
- Follicle count, the strongest predictor, overlaps with the diagnostic criteria
  (soft label leakage). This was tested directly; see Section 5.
- Recall for the PCOS class is 0.73; the model misses about a quarter of true cases.
- Sample size is modest (541 patients, 177 positive), so estimates carry meaningful
  uncertainty.
- Some binary symptom features are self-reported, which can introduce reporting bias.

---

## 5. Leakage experiment: removing the follicle-count features

To quantify how much the model depended on the near-diagnostic follicle-count
features, the full pipeline was repeated with **both follicle-count columns
(Follicle No. (L) and Follicle No. (R)) removed**. Everything else was held
identical: the same cleaning, the same random seed and train/test split, and the
same two models. Only the two columns changed, so the comparison is fair.

### 5.1 Before-and-after comparison (random forest)

| Metric | With follicle count | Without follicle count | Change |
|---|---|---|---|
| ROC AUC | 0.945 | 0.899 | -0.046 |
| PR AUC (average precision) | 0.928 | 0.791 | -0.137 |
| Accuracy | 0.897 | 0.816 | -0.081 |
| Recall (PCOS class) | 0.73 (32/44) | 0.52 (23/44) | -0.21 |

(Logistic regression behaved the same way: ROC AUC fell from 0.940 to 0.868, and
PR AUC from 0.915 to 0.748.)

### 5.2 Confusion matrix without follicle count (random forest, test set)

|  | Predicted non-PCOS | Predicted PCOS |
|---|---|---|
| **Actual non-PCOS** | 88 | 4 |
| **Actual PCOS** | 21 | 23 |

Of the 44 true PCOS patients, the model now catches only 23 and misses 21, against
32 caught when follicle count was included.

### 5.3 Top features after removing follicle count (random forest)

Skin darkening, hair growth, weight gain, AMH, and cycle length. These are all
recognised clinical signs of PCOS (hyperandrogenism and menstrual dysfunction)
rather than parts of the ultrasound-based diagnostic measurement. The model that
remains is therefore leaning only on genuine symptoms.

### 5.4 Interpretation (a two-part finding)

The headline result is that the experiment splits cleanly into two halves, and both
matter.

**Part one: the model is robust in its ranking ability.** ROC AUC fell only
slightly, from 0.945 to 0.899. ROC AUC measures how well the model separates PCOS
from non-PCOS across all thresholds. Its small drop shows the model retains real,
independent predictive signal from genuine clinical symptoms even with the
near-diagnostic feature removed. The model was never *only* a follicle-count
detector.

**Part two: the leakage mattered where it counts clinically.** Recall for the PCOS
class fell sharply, from 0.73 to 0.52, and PR AUC fell from 0.928 to 0.791. At the
chosen decision threshold the model now misses nearly half of true PCOS cases
instead of a quarter. Follicle count was doing heavy lifting in the model's ability
to actually *catch* positive cases, which is the behaviour a clinician cares about
most. This is direct, quantified evidence that the soft label leakage inflated the
original model's apparent sensitivity.

Taken together: the follicle-removed model is arguably the more *honest* model,
because every feature it uses is a true symptom rather than part of the diagnosis,
but it is also the less *sensitive* model, because the feature it lost was carrying
much of the detection power. Both statements are true at once, and reporting only
one of them would misrepresent the result.

### 5.5 Remaining limitation

Follicle *size* (Avg. F size) was retained and still appears among the top features
in the logistic regression. Follicle size derives from the same ultrasound
assessment as follicle count, so a stricter version of this experiment would remove
all imaging-derived features. This was not done here, and is noted as a known
limitation.

---

## Reference

Based on articles retrieved from PubMed:

- The Rotterdam ESHRE/ASRM-Sponsored PCOS Consensus Workshop Group. Revised 2003
  consensus on diagnostic criteria and long-term health risks related to polycystic
  ovary syndrome. *Fertility and Sterility.* 2004;81(1):19-25.
  DOI: https://doi.org/10.1016/j.fertnstert.2003.10.004
- The Rotterdam ESHRE/ASRM-Sponsored PCOS Consensus Workshop Group. Revised 2003
  consensus on diagnostic criteria and long-term health risks related to polycystic
  ovary syndrome (PCOS). *Human Reproduction.* 2004;19(1):41-47.
  DOI: https://doi.org/10.1093/humrep/deh098
