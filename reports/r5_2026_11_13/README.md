# Household exposure to an appreciation of the lari

**R5 decision, 13 November 2026.** The 2024 survey measures baseline consumption and foreign-transfer exposure. A stronger lari can reduce the cost of purchases while also reducing the GEL value of a foreign transfer. Among households reporting transfers, the second channel can outweigh the first even when domestic prices fall. The sign depends on what proportion of the transfer retains a fixed dollar value. Neither that proportion nor the retail response to an episode-specific currency shock is identified. The R3 evidence therefore permits no household gain or loss attributable to NBG purchases.

## Results in GEL per household per month

Consider a 1% decline in the GEL price of a dollar. For illustration, assume prices of the nine matched consumption categories fall 0.25% once, with fixed quantities. The 0.25 coefficient is a sensitivity choice, common to all categories. The first two columns below are survey measurements. The savings column values the matched basket at December 2024 category prices. The last column is a separate calculation at reported transfer values, assuming the entire receipt retains a fixed USD value, with no sender or fee response. Figures are weighted group means. [All groups and standard errors](groups.csv) · [Amounts by category](category_exposures.csv)

| 2024 household group | Consumption at survey prices | Unmatched spending | Conditional basket saving | Conditional transfer loss |
|---|---:|---:|---:|---:|
| All | 1,306.00 | 24.67% | 2.50 | 0.61 |
| Lowest equivalized consumption quintile | 488.55 | 24.32% | 0.94 | 0.23 |
| Highest quintile | 2,481.44 | 25.53% | 4.68 | 1.33 |
| Urban | 1,382.44 | 21.83% | 2.74 | 0.68 |
| Rural | 1,175.44 | 30.36% | 2.07 | 0.49 |
| At least one pension-age household member | 1,234.15 | 24.50% | 2.37 | 0.50 |
| Positive foreign transfers in survey period | 1,563.16 | 24.36% | 3.00 | 9.31 |

For the bottom and top quintiles, the partial basket savings at survey prices equal **0.189% and 0.186%** of total consumption. The larger GEL saving in the top quintile mainly reflects its larger basket. Unmatched categories and different pass-through across categories can reverse a percentage ranking. Rural noncash consumption averages GEL 207.58 versus GEL 26.56 in urban households. The missing price channel is especially material for rural households.

**Transfer recipients.** In the 2024 positive-receipt group (764 household-quarter records, 544 distinct diaries), monthly foreign transfers average GEL 930.94. For a like-for-like two-channel comparison at survey prices, conditional saving is GEL 2.96. If no reported transfer is fixed in USD its direct USD conversion loss is zero. If all are fixed in USD the loss is GEL 9.31 and the two-channel balance is **−6.35**. The break-even USD-sensitive share under this price assumption is **31.8%** (2.955769 / 9.309357). These endpoints describe stipulated currency exposures. The Shinda 05 questionnaire §2.2 includes money, goods, services and third-party payments from abroad. The aggregate reports GEL equivalents and does not identify USD amounts. With a different price response, currency mix or sender adjustment the threshold changes. Across all households the corresponding all-USD two-channel balance is +1.85. These are partial nominal flows. No statement about realized welfare follows.

**2025 sensitivity.** Applying the same procedure to a separately validated annual sample yields GEL 1,438.73 mean consumption and 22.54% unmatched spending. The standardized saving averages GEL 2.83 at December 2025 prices. Each year uses its own December price base. The difference combines price and composition changes and cannot measure a within-household treatment effect.

## Validation and coverage

The release archives passed locked SHA-256 and ZIP CRC checks. Within each year, the schedule, household size, expenditure and income files have the same unique household-quarter identifiers. All twelve interview months are present. The 2024 file contains 13,105 observations from 7,667 diaries and the 2025 file 13,341 from 7,773. Weights are positive. Consumption, cash/noncash expenditure and inflow identities close record by record. Monthly averages use the released weights pooled over quarters, normalized within group. Quintiles rank households by the published equivalent-adult consumption measure with scale exponent 0.6. Pension-age groups use reported age counts and distinguish age from pension receipt. No individual observations are redistributed. [Survey checks](survey_validation.csv)

Nineteen weighted means reproduce the published values within GEL 0.05. The checks include 2024 national, urban and rural consumption and remittances, nine national spending components, and national expenditure and cash/noncash inflows for both years. National 2024 total expenditure reproduces GEL 1,735.7 and total inflows GEL 1,895.7. Consumption excludes nonconsumption outlays such as saving and lending. [Computed reconciliation](geostat_checks.csv) · [Geostat yearbook, income and expenditure by residence](https://www.geostat.ge/media/76141/Yearbook_2025.pdf) · [Expenditure](https://www.geostat.ge/en/modules/categories/51/households-expenditures) · [Income](https://www.geostat.ge/en/modules/categories/50/households-income)

The purchase diary records average monthly GEL paid by household and COICOP product. Five-digit codes with prefixes 11, 12 and 21 map to food, nonalcoholic beverages and alcohol. Their sums are deducted from the mixed cash total exactly once. Every residual stays unmatched, including the one unrecognized six-digit 2024 code. Absence of a purchase row means no recorded expenditure in that diary code. It does not zero the household's residual mixed spending. Total unmatched expenditure averages GEL 40.02 residual mixed spending, 188.72 other cash consumption and 93.40 noncash consumption in 2024. Household goods and housing are approximate matches: the SPSS energy label is narrower than the yearbook housing label, although its weighted mean reproduces the published housing amount. Removing both approximations raises the unmatched share to **39.80%**. [Crosswalk](crosswalk.csv) · [Release and variable documentation](https://github.com/NikolozOniani/GeorgianNationalBank/releases/tag/GEOSTAT)

For matched amount B reported in interview month m, the December cost proxy is B × CPI(December)/CPI(m) for its category. National chained monthly indices supply a common price month within each survey year. The interview month approximates the reference price of diary and retrospective reports. Regional price levels and within-category substitution are unobserved. A full December-valued denominator is unavailable for unmatched spending. Reported percentages of **total** consumption therefore use survey prices for both numerator and denominator. The positive/negative transfer scenarios use the same records as the basket. The 2025 result is a composition sensitivity from a repeated cross-section.

## What the pre-episode prices support

For each category we checked monthly price growth against signed changes in the mean official GEL/USD rate, separately at 0, 1 and 3 months, using 2020–24 data only. Each descriptive least-squares fit includes calendar-month effects, lagged category inflation and the broad dollar change at the FX lag. Regressors are log changes × 100. Negative FX changes represent appreciation. Samples range from 56 to 59 monthly observations. These single-lag slopes do not cumulate to a dynamic response. Food's appreciation slope changes from −0.048 at lag zero to +0.072 at one month and −0.126 at three months. Transport's depreciation slope changes from +0.395 to −0.290 at one month. These patterns provide no stable empirical category schedule for a policy-counterfactual calculation. Freight, foreign product prices, invoicing, tariffs, administered-price changes and domestic demand are not jointly isolated. Sign splits are descriptive, with no test establishing causal asymmetry. [All 27 diagnostics](price_diagnostics.csv)

The IMF 2025 Selected Issues chapter reports approximately 0.5 percentage points more inflation at a two-year horizon for a 10% depreciation. That aggregate inflation response supplies neither a bilateral appreciation elasticity by category nor a cumulative retail price-level effect. We therefore release the reusable category amounts. For any independently justified category price decline, multiply its share or GEL amount by that decline and sum. Zero pass-through gives zero basket saving. A response of half the illustrative size halves each basket result. [IMF benchmark, figure 13](https://www.imf.org/-/media/files/publications/cr/2025/english/1geoea2025002-source-pdf.pdf)

| Other channel or uncertainty | Evidence limit and consequence |
|---|---|
| Sampling | Diary-cluster linearized standard errors hold group thresholds fixed and allow repeated quarterly reports. The national basket scenario has SE GEL 0.030, the recipient two-channel survey-price result GEL 0.442. PSU/stratum identifiers and replicate weights are unavailable in the released schedule. These approximations omit multistage design, price, mapping and FX uncertainty. |
| Debt service and asset revaluation | The borrowing/dissaving variable mixes flows. Household debt-service schedules, asset balances and currencies are unresolved. No group-level FX balance is imputed. |
| Employment, sector profits and imported inputs | Household earnings totals cannot identify firm pricing, export revenue, imported-input exposure or wage responses. Full household net income remains unresolved. |
| Time, attribution and welfare | An episode-specific FX path and dynamic category responses are missing. No episode lag, substitution response or compensating variation is estimated. |

## Reproduction

Use Python 3.12 with pandas, NumPy, openpyxl and pyreadstat (tested with pyreadstat 1.3.7). Place the 2024 and 2025 ZIP release assets in a directory without extracting them. Supply the same [Geostat group CPI workbook](https://www.geostat.ge/media/83812/Consumer-Price-Indices-(Previous-month=100).xlsx) as the archived pilot, SHA-256 `5b2df9ab880ff87e07e3329b35826c301f3c318f35aa1313041ad1b55946b6b7`. From the repository root run:

```sh
python src/r5_exposure.py --release-dir /path/to/release --group-cpi /path/to/group_cpi.xlsx --check
python replication/check_repository.py
```

The first command reproduces six CSVs from raw inputs. The second includes offline checks on the committed aggregates. The [locked release register](../../archive/legacy/reports/release_assets.json) identifies the exact downloadable assets. The two NBG/Fed FX inputs are tracked under data/derived/episode_2026_11_09 with [provenance](../../data/source_manifest.json).
