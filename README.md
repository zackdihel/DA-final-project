# DA-final-project
ECON 5200 final project
# Does Higher Education Cause Lower Unemployment?
### A Causal Analysis Using Instrumental Variables | Massachusetts & New Hampshire (2000–2024)

---

## Objective

This project estimates the **causal effect of college degree attainment on individual unemployment probability** using a two-stage least squares (2SLS) instrumental variables framework. The central research question — *does attaining a higher education degree cause a reduction in unemployment?* — is motivated by the well-documented positive correlation between education and employment outcomes, and the critical need to distinguish selection effects from true causal mechanisms.

The analysis is restricted to Massachusetts and New Hampshire, two neighboring New England states with meaningfully different public university cost structures, providing the cross-state tuition variation necessary to instrument for endogenous education decisions.

---

## Data

| Source | Description | Coverage |
|---|---|---|
| **IPUMS USA (ACS)** | Individual-level microdata: employment status, educational attainment, demographics | 2000–2024 |
| **SHEEO SHEF Database** | State-level net tuition per FTE enrollment at public universities | 2000–2024 |

**Final analytical sample:** 759,980 working-age individuals (ages 25–64) in the labor force across Massachusetts (STATEFIP 25) and New Hampshire (STATEFIP 33).

---

## Tech Stack

- **Data manipulation:** `pandas`, `numpy`
- **Causal inference / econometrics:** `statsmodels`, `linearmodels` (IV2SLS)
- **Machine learning / prediction:** `scikit-learn` (RandomForestClassifier, cross_val_predict)
- **Visualization:** `matplotlib`, `seaborn`, `plotly`
- **Dashboard:** `streamlit`

---

## Methodology

- **Identification strategy:** Instrumental Variables (2SLS), chosen over OLS, DiD, RD, and RCT given the observational nature of the data and endogeneity of college degree attainment
- **Instrument:** Net tuition per FTE at public universities by state and year (SHEF), which affects college enrollment decisions through cost but has no direct path to individual unemployment outcomes
- **Treatment variable:** Binary college degree attainment (EDUCD ≥ 101: bachelor's degree or higher)
- **Outcome variable:** Binary unemployment indicator (EMPSTAT = 2, conditional on labor force participation)
- **Controls:** Age, sex, race, Hispanic ethnicity, state indicator (is_MA), year fixed effects (2000–2024)
- **Balance check:** Pre-estimation covariate comparison between treated (degree) and untreated (no degree) groups to motivate IV over OLS
- **First stage:** OLS regression of college degree on tuition instrument and controls; F-statistic evaluated against Stock-Yogo (>10) and Lee et al. 2022 (>104) weak instrument thresholds
- **Second stage:** IV 2SLS via `linearmodels.IV2SLS` with heteroskedasticity-robust standard errors
- **Prediction benchmark:** Random Forest classifier (n=100,000 subsample, 5-fold CV) to contrast predictive accuracy (AUC-ROC) against causal precision
- **Robustness checks:** Five IV specifications — baseline, dropping recession years (2008, 2009, 2020), alternative instrument (is_MA), minimal controls, and expanded industry fixed effects — to assess stability of causal estimates

---

## Key Findings

### Naive OLS (Biased Benchmark)
A college degree is associated with a **3.22 percentage point reduction** in unemployment probability (coef = -0.0322, p < 0.001). This estimate is statistically significant but upward-biased due to positive selection — degree holders are systematically wealthier, less Hispanic, and more likely to reside in Massachusetts, all of which independently reduce unemployment risk.

### First Stage — Instrument Relevance
Net tuition per FTE is a strong and statistically significant predictor of college degree attainment (coef = -0.000005, p = 0.0002). The first-stage F-statistic of **1,176.33** far exceeds both the Stock-Yogo threshold (>10) and the more conservative Lee et al. 2022 threshold (>104), confirming the instrument is not weak. The negative sign is consistent with economic intuition: higher tuition costs reduce the probability of obtaining a degree.

### IV 2SLS — Causal Estimate
The IV estimate of the causal effect of college degree on unemployment is **-0.0944** (SE = 0.1042, 95% CI: [-0.2987, +0.1099], p = 0.365). While the point estimate is directionally consistent with human capital theory and nearly three times larger in magnitude than the naive OLS, it is **statistically insignificant** at conventional levels. We fail to reject the null hypothesis that higher education has no causal effect on unemployment. The wide confidence interval reflects the inherent precision cost of IV estimation, which isolates only the thin slice of college enrollment variation driven by tuition changes.

### Predictive Model (Random Forest)
The Random Forest classifier achieves an **AUC-ROC of 0.733** on a 100,000-observation subsample, demonstrating moderate predictive accuracy. This contrast — a model that predicts unemployment well but cannot support causal inference — illustrates the fundamental distinction between prediction and causation that motivates the IV approach.

### Robustness Checks
IV estimates are stable in sign and insignificance across four of five specifications (baseline, drop recessions, minimal controls, expanded industry fixed effects), with estimates ranging from -0.07 to -0.32. First-stage F-statistics exceed 700 in all specifications, confirming instrument relevance is robust. The alternative instrument (is_MA) produces a statistically significant but opposite-signed estimate (+0.1039, p < 0.001), consistent with a violation of the exclusion restriction — state of residence directly affects unemployment through labor market quality, independent of education — validating the choice of tuition per FTE as the primary instrument.

---

## Interpretation

While descriptive evidence strongly suggests higher education is associated with lower unemployment (OLS: -3.22pp), IV estimates using state tuition costs as an instrument are consistent with a negative causal effect (-9.44pp) but are insufficiently precise to reject the null hypothesis. The result should be interpreted as **suggestive but inconclusive evidence** of a causal effect, bounded by the exclusion restriction assumption and the narrow geographic scope of the two-state design. Future work expanding to a multi-state panel with historically determined instruments (e.g., land-grant college distance) would substantially improve identification precision.

---

## Dashboard

An interactive Streamlit dashboard allows users to simulate the effect of tuition policy changes on unemployment probability in real time, with dynamic confidence bands and counterfactual scenario analysis.

👉 **[Live Dashboard](https://da-final-project-d2nado2dmhlkup3teta3fd.streamlit.app/)**
