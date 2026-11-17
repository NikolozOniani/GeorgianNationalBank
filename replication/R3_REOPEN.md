# Reproduce the R3 reopening experiment

This supplement accompanies the [decision report](../reports/r3_reopen_2026_11_16/README.md) and [pre-fit design](../research/R3_REOPEN_DESIGN_2026_11_16.md). The primary model fails its release gate. Successful execution reproduces that rejection, not a validated counterfactual estimate.

## Environment and offline reproduction

Tested with Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8. Install the narrowly scoped environment before running the repository tests:

```sh
python -m pip install -r replication/requirements-r3-reopen.txt
python src/r3_reopen.py --check
python src/r3_reopen_figures.py --check
python replication/audit_r3_reopen.py
python -m unittest discover -s tests -p test_r3_reopen.py -v
python replication/check_repository.py --replicate
```

The first model command recomputes all fits, hindcasts and 199 block resamples from committed extracts, then compares all numerical outputs byte-for-byte. NumPy is needed for the model and tests, SciPy for the independent QR/matrix audit, and Matplotlib for the figure. No network is required for these commands. Other platforms/BLAS versions can differ in their last numerical digits; the independent audit applies explicit tolerances. Do not silently replace committed outputs to bypass a mismatch.

To regenerate this dated experiment intentionally, omit `--check` from the model and figure commands. They write only `reports/r3_reopen_2026_11_16/`. To store a fresh independent audit, pass `--report` with a new destination; preserve existing dated verification records. The general repository checker reproduces archived generators only in a temporary copy. Its verification metadata does not describe the new R3 fitting as absent.

## Original-source checks and retrieval

Raw source files are ignored by Git. Exact URLs, access failures, acquisition dates, byte counts and SHA-256 hashes are in [the new manifest](../data/r3_reopen_source_manifest.json). Three successful files are pinned: World Bank GDP JSON, Adler–Lisack–Mano PDF and Chen et al. PDF. Failed canonical/alternate attempts are preserved as failed attempts, not silently promoted to success.

With those raw files cached and `pdftotext` from Poppler available:

```sh
python src/r3_reopen.py --verify-sources --check
```

To acquire missing successfully pinned source files from their recorded public URLs and perform the same checks:

```sh
python src/r3_reopen.py --acquire --check
```

Downloads are bounded at 15 MB and checked before being written. A provider revision or an inaccessible old vintage fails explicitly. Acquisition does not retry entries already documented as failed. No promise is made that a provider will indefinitely retain the same bytes.

Verification compares the committed annual GDP rows to the source JSON and the calibration inputs to the **actual Table A11 rows on physical PDF p.41**, including all four nominal FXI coefficients and the autoregressive coefficient. Chen et al. is a hashed reference for model review, not a numerical input to the candidate. The earlier NBG, exchange-rate and global-series extraction procedures remain in [acquisition replication](ACQUISITION.md), [R1](R1.md), [R2 report](../reports/r2_2026_11_11/README.md) and [original manifests](../data/source_manifest.json). The offline model check verifies arithmetic from extracts, not fresh extraction of all earlier raw vintages.

## Input/output map

| Input or output | Definition |
|---|---|
| `data/derived/r3_reopen_2026_11_16/gdp_observations.csv` | Five observed annual nominal USD GDP values, 2020–2024; GDP is converted to USDm inside the model |
| `research/r3_reopen_calibration.json` | Four external nominal response specifications; primary chosen before fitting; source coefficients and converted signs |
| `model_panel.csv` | 81 monthly rows, observed inputs, normalization status and available daily observation counts |
| `coefficients.csv` | Seven fitted cases; `ai`: intercept, lagged rate, lagged FX change, lagged intervention, dollar change, VIX; `ay`: intercept, current rate, lagged rate, dollar change, VIX; `aq`: `ai` regressors followed by current rate; `b`: current intervention and lags 1–3; `rho`, `theta`, `det`: scalar dynamics, reaction and clearing determinant |
| `external_kernels.csv` | Rounded-source external impulse responses and two diagnostic challengers over 61 impulse horizons; not the full Georgian closed-system response |
| `hindcasts.csv` | Six kernels × 24 withheld months; GDP-scale sensitivity shares the primary pre-period fit |
| `candidate_paths.csv` | Seven specifications × 21 episode months, with rejected-release labels; FX, rates, sales, reserves and cash diagnostics |
| `model_comparison.csv` | Point-fit checks and terminal/average diagnostics; `preliminary_checks_only` is not release approval |
| `bootstrap.csv` | All 199 primary six-month moving-block pairs draws; no failed draw discarded |
| `residual_diagnostics.csv` | Three equation residual summaries for each of seven cases |
| `validation.json` | Input/output hashes, fixed design commit, counts and explicit `preferred_path_released: false`; selected-draw percentiles are not a confidence interval |
| `independent_checks.json` | Separate QR and matrix-solve arithmetic check; does not import the production model |
| `rejected_model_diagnostics.svg` | Deterministic diagnostic figure, generated by `src/r3_reopen_figures.py` |

All output paths in the table are under `reports/r3_reopen_2026_11_16/`. The folder date identifies the experiment's start, not an assertion that every source was downloaded that day. Existing episode data end in September 2026; no later observation is fabricated or interpolated.

## Interpretation safeguards

The model's exchange variable is `100 log(GEL per USD)` and intervention is percentage points of an **annual** GDP denominator. A higher exchange variable means depreciation. The primary reported gap is `100 × (observed / candidate − 1)`; `quote_decline_pct` uses the different denominator `100 × (1 − candidate / observed)`. The rates are percentage points, flows/stocks USDm, and the financing-cash diagnostic GELm. The cash diagnostic uses month-end prices and must not be called measured settlement cash or an economic cost.

The unobserved gross treatment, adaptive information structure, orthogonality restriction, frozen GDP scale, SOFR return proxy and omitted reserve-confidence channel remain assumptions. The unrestricted baseline reconstruction is an identity with recovered shocks. Passing software tests does not validate those assumptions. No candidate is authorized for downstream R4–R7 incidence or welfare estimation.
