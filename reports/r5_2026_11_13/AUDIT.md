# Audit of the R5 release

**Disposition.** Supersede the December-repriced basket amounts, their standard errors, and the six food and nonalcoholic beverage regression rows in the [original commit](https://github.com/NikolozOniani/GeorgianNationalBank/commit/d4b1b2d5abb8cbf34583c0658c0836feef0a4d21). Use the corrected [group estimates](groups.csv), [category exposures](category_exposures.csv), [crosswalk](crosswalk.csv) and [diagnostics](price_diagnostics.csv). The survey-price exposure and transfer arithmetic reproduces independently. Household effects attributable to the purchase program remain unidentified.

## Defect and consequences

The first program built a dictionary keyed by numeric CPI code. Geostat’s Georgia sheet uses 11 and 12 at **two hierarchy levels**. Rows 8 and 9 contain Food and Non-alcoholic beverages (level 3). Rows 53 and 56 contain Restaurants and hotels and Miscellaneous goods and services (level 2). Later rows overwrote the intended series. The crosswalk in the initial commit displayed the wrong labels. Its tests checked exposure totals and row counts, which can pass with the wrong prices.

| Metric | Original | Corrected |
|---|---:|---:|
| National 2024 partial basket saving at December prices, GEL/month | 2.495543 | 2.498056 |
| Rural 2024 partial basket saving at December prices, GEL/month | 2.074394 | 2.076616 |
| National 2025 partial basket saving at December prices, GEL/month | 2.825238 | 2.830907 |
| Food appreciation slope, 0-month lag | −0.048256 | −0.080481 |
| Food appreciation slope, 1-month lag | +0.072475 | −0.355497 |
| Food appreciation slope, 3-month lag | −0.125613 | +0.153640 |
| Nonalcoholic beverage appreciation slope, 0-month lag | −0.071783 | +0.018882 |

The price error affects both appreciation and depreciation slopes for both food series at all three lags. Comparing all shared numeric fields against the original commit isolates 48 changed December category amounts across 216 cells, all 24 December-valued group means and associated savings and standard errors, and six pairs of diagnostic slopes. Neither the original 19 published-aggregate checks nor the two survey-validation rows changed. The standardized basket amount changes little because the survey spending amounts and imposed common 0.25% price decline were already fixed. Only the interview-month-to-December conversion was wrong. The diagnostic regressions use the monthly CPI observations directly, so even slope signs changed. Their coefficients are descriptive.

The revised loader requires the expected level, numeric code and exact label, exactly once, with a complete positive finite series. Each output identifies the CPI level, and the crosswalk records the worksheet and source row. A regression test includes both unrelated divisions before and after the intended rows, and checks that ambiguous, missing and mislabeled inputs fail.

## Independent checks

The original generator reproduced its original CSVs before repair. For the corrected version, a separate executable reads the source files without importing the production crosswalk or exposure functions. It joins survey records in SQLite, matches five-digit diary codes by string prefix, assigns household quintiles by cumulative weight, and prices expenditure by multiplying indices **after** the interview month through December. December observations receive a unit factor. It checks nine category means and shares in each of 12 groups for each year, the two coverage definitions, group counts, weighting, and the two scenario channels. It independently recomputes the diary-cluster errors from household scores and the signed FX regressions by calendar-month demeaning and QR factorization. [Verifier](../../replication/audit_r5.py) · [Results and source hashes](independent_checks.json)

- **Survey checks.** Unique household-quarter joins, positive weights, the expenditure identities, and the ratio of consumption to the released equivalence scale agree. Both annual purchase diaries have unique UID/product pairs. The respective 337 and 307 household-quarter records without a diary purchase row keep their unmatched spending. The one six-digit 2024 code remains unallocated. Repeat interviews enter the clustered uncertainty calculation.
- **Official benchmarks.** The 19 original survey aggregates reconcile at published precision. The audit also matches 2025 urban and rural average household expenditure (GEL 2,015 and 1,799), cash consumption as a share of total expenditure (69.3%), and the food/beverage/tobacco share of cash consumption (38.7%). These are ratios of weighted totals. [Geostat 2025 release, p. 5](https://www.geostat.ge/media/79215/Indicators-of-Living-Conditions-%28Household-Income-and-Expenditures%29---2025.pdf)
- **Rounded headline and threshold.** At survey prices the 2024 broad and strict matched shares are 75.33% and 60.20%. Recipients’ break-even USD exposure share remains 31.8%. It is the ratio of two weighted group means and describes the break-even share of total recipient transfers under a common price scenario. It gives neither a fraction of households that lose nor an individually estimated threshold.
- **Overlap and precision.** The annual archives share 4,099 DiaryIDs. They support separately weighted annual comparisons. No across-year independence assumption, panel estimate or standard error on the change is justified here. Within-year diary-cluster errors condition on the assigned quintiles and omit the unknown primary-area sampling design. A small sampling error does not measure uncertainty in the stipulated FX shock or price response.
- **Scope of tests.** The general repository suite tests preservation and internal consistency. Its generic validation metadata describes that verification command. The raw rebuild and independent audit are separate commands and require the pinned surveys, price workbook and Python dependencies. Independently verified calculations can still share source errors or economic assumptions. No identified category pass-through, observed currency-sensitive remittance share, or aggregate welfare effect emerges from these checks.

Reproduction commands are in the [R5 report](README.md#reproduction). The original Git commit remains available for comparisons.
