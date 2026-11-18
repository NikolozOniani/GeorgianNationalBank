# Can a forward-looking rule reproduce Georgian policy decisions?

The revised rule predicts the size of policy moves slightly better than always forecasting a hold on a squared-error criterion. Its response to expected inflation changes sign across historical samples. The registered tests therefore reject its use to set interest rates in the no-purchases simulation. The experiment evaluates the policy equation on its own. [Design committed before fitting](../../research/R3_RATE_RULE_DESIGN.md) · [Decision record](validation.json)

## What the NBG knew before each meeting

The [source register](../../data/r3_rate_sources.json) identifies 28 quarterly reports by hash, printed month, physical PDF page and a short locator for the real GDP growth forecast. The [vintage table](../../data/derived/r3_rate_rule/vintages.csv) contains three public signals. They are the annual inflation rate in the last completed quarter, the central inflation projection four quarters after that observation, and expected real GDP growth for the report's calendar year. The activity outlook includes expected supply growth as well as demand. The inflation forecast embodies the NBG's own assumptions about future policy. It measures a published central-bank expectation. Private expectations and the policymakers' confidential information set are unobserved. [NBG quarterly reports](https://nbg.gov.ge/en/publications/monetary-policy-reports)

Each decision draws on the latest report dated in an earlier calendar month, at most four months old. This conservative timing excludes the release accompanying the decision even when policymakers already possessed it. Several older catalogue dates disagree with the document mastheads. We use the report month printed in the document as the vintage and assume its information was public by month-end. Original day-specific release timestamps are unverified for the full archive. A current-year growth forecast can refer to the prior calendar year when reused early in January or February. [Meeting input ledger](meetings.csv)

The central curve and the 3% target line are vector paths in the inflation charts. The extractor maps the printed quarter ticks to path vertices, obtains the vertical scale from the percentage ticks and reads the two quarters from the central curve. Values are rounded to 0.1 percentage point. A cross-check chains Geostat's all-items monthly CPI and compares the average index each quarter with the same quarter a year earlier. The largest absolute difference across all 28 historical inflation values is 0.1084 percentage point. Rounding, chart precision and source vintages can contribute. This historical check supports the axis alignment. The forecasts themselves remain chart readings. [CPI cross-check](cpi_crosscheck.csv)

## Predictive test

There are 56 usable decisions in the 3% inflation-target period. The first fit uses 40 meetings from March 2018 through December 2022. The January 2018 meeting lacks a preceding eligible report. Sixteen meetings in 2023–2024 are evaluated chronologically, using only preceding decisions for each expanding fit. The holdout contains nine holds and seven cuts, with zero hikes. It uses nine distinct report vintages. Repeated quarterly information and the small holdout limit precision.

| Predicted change at next decision | RMSE, percentage points | Mean absolute error, percentage points |
|---|---:|---:|
| Revised rule, updated after each meeting | 0.288 | 0.209 |
| Same specification, fitted through 2022 and frozen | 0.474 | 0.395 |
| Updated rule omitting expected inflation | 0.292 | 0.214 |
| Always hold | 0.306 | 0.188 |
| Repeat previous meeting's change | 0.280 | 0.188 |

The 6.0% RMSE improvement against always holding depends on the year. RMSE is 0.312 versus 0.280 in 2023 and 0.262 versus 0.331 in 2024. Adding forecast inflation to the expanding rule improves pooled RMSE by only 0.004 percentage point. The frozen-through-2022 rule predicts a hike at all 16 meetings. The expanding rule anticipates the direction of four of the seven cuts. Exact-sign scoring gives no credit for predicting a small nonzero change at a hold. [Meeting predictions](predictions.csv) · [Full scores](scores.csv)

## Economic interpretation

The dependent variable is the announced change in percentage points. The regressors are a constant, the previous announced rate, the actual and expected inflation gaps relative to 3%, and forecast growth. At the full-sample coefficients, an extra percentage point of expected inflation predicts a 0.037 percentage point increase in the next rate change, holding the other regressors fixed. The corresponding coefficients on actual inflation and growth are 0.037 and 0.009. These are conditional historical associations. In particular, successful prospective tightening can bring the published inflation forecast toward target and weaken its measured association with later tightening.

The full-sample coefficient on the prior rate in the *level* equation is 0.886. At target inflation, a fixed growth forecast of 5%, and unchanged coefficients, its implied stationary rate is approximately 7.87%. This conditional steady state follows from setting the fitted change to zero. Interpreting it as a structural neutral rate would require evidence on real rates, potential output and the inflation outlook. Through 2022 the own-rate coefficient is 1.036 and the expected-inflation coefficient is −0.006. Omitting 2021 from the full sample also makes the expected-inflation coefficient negative (−0.007). The activity coefficient also flips sign when 2020 is omitted from the full sample. These diagnostics explain why the promising full-sample signs cannot justify adopting the block. [All coefficients and year-deletion fits](coefficients.csv)

Adoption required lower expanding RMSE than a hold, stable own-rate dynamics, and a consistently positive response to the forward inflation gap. Only the first criterion passes. A predictive rule for meeting dates would also need the inflation and growth forecasts that would prevail under the alternative policy before it could determine an episode interest-rate path. The observed quarterly forecasts are conditional on actual policy. This stage therefore supplies no new GEL/USD endpoint.

## Reproduction

From the repository root, run the following commands. Python 3.12, NumPy 2.3.5 and SciPy 1.17.0 reproduce the model and independent pivoted-QR check. Extraction additionally uses PyMuPDF 1.26.6. The optional Geostat cross-check uses openpyxl and the hash-pinned workbook in the archived NBG source manifest.

```sh
python src/r3_rate_rule.py --check
python replication/audit_r3_rate_rule.py
python src/r3_rate_sources.py --acquire --check
python replication/audit_r3_rate_rule.py --geostat-workbook /path/to/group_cpi.xlsx
python replication/check_repository.py --replicate
```

The first two commands run offline on committed extracts. The third fetches missing source PDFs into the ignored raw cache and verifies their SHA-256 hashes before extracting. With all PDFs cached, omit `--acquire` to check source extraction offline. The Geostat command writes the CPI comparison table. The independent audit rebuilds the decision-to-vintage join from the source extracts and verifies all 14 primary coefficient vectors and all 16 expanding predictions within 10⁻⁸ of the published numbers. [Decision history and original source hashes](../../archive/legacy/reports/nbg_source_manifest.json)
