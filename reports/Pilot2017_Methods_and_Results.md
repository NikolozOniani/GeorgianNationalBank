# 2017 household inflation exposure pilot

## Result and interpretation

The validated 2017 survey has **11,590 household-quarter records** and 6,866 distinct `DiaryID` values. Six expenditure fields can be related to published Geostat CPI groups. They represent a survey-weighted mean **40.92% of total household consumption**; **59.08% remains unmatched**. The weighted mean matched-category contribution to a frozen 2017 basket is **0.659 percentage points** for December 2017–December 2018 and **1.603 points** for December 2017–December 2019. These are partial price contributions and are not full household inflation rates, changes in actual spending, compensating variation, or welfare effects. They do not isolate NBG policy.

| Household group | 2017 matched share of total consumption | Matched contribution through Dec 2018, pp | Through Dec 2019, pp |
|---|---:|---:|---:|
| Quintile 1 (lowest equivalized consumption) | 36.17% | 0.676 | 1.494 |
| Quintile 2 | 36.65% | 0.629 | 1.463 |
| Quintile 3 | 39.22% | 0.621 | 1.514 |
| Quintile 4 | 43.67% | 0.651 | 1.649 |
| Quintile 5 | 48.89% | 0.722 | 1.893 |
| Rural | 36.24% | 0.596 | 1.448 |
| Urban | 44.19% | 0.704 | 1.711 |
| Household with member of pension age | 41.73% | 0.777 | 1.817 |
| No member of pension age | 40.12% | 0.541 | 1.388 |

The table's nominal differences cannot establish which group faced higher **total** inflation. The largest omitted field combines food, beverages, and tobacco, which span at least two CPI divisions; that omission is especially consequential for lower quintiles. The figure `figures/pilot2017_partial_exposure.png` displays only the matched contribution.

Mapping sensitivity is material: restricting to four direct group matches (clothing, health, transport, education) covers **24.35%** of weighted total consumption and produces **0.251 pp** for 2018, compared with 0.659 pp when household goods and fuel/electricity are included using approximate scopes. Neither figure is a full inflation estimate. Both versions appear in the CSV and figure.

## Sources, validation, and crosswalk

- Household source: the actual `2017.zip` asset of [GEOSTAT release](https://github.com/NikolozOniani/GeorgianNationalBank/releases/tag/GEOSTAT), SHA-256 `dc7ea470c7fa11ad608003af290979fc0cd144daec82f5d9e37c000a321c58ad`. ZIP CRC passes. `UID` is unique within each of the schedule, expenditure, family, and income files; one-to-one merges yield 11,590 observations. `DiaryID` is repeated across quarters and is treated as a cluster, not a panel outcome. Reference months run January–December 2017; quarters 83–86. Weight values are positive and observed for all records.
- Geostat's [official group CPI workbook](https://www.geostat.ge/media/83812/Consumer-Price-Indices-(Previous-month=100).xlsx), SHA-256 `5b2df9ab880ff87e07e3329b35826c301f3c318f35aa1313041ad1b55946b6b7`, has national monthly group indices from January 2004 to October 2026. All 24 months January 2018–December 2019 needed for the six matched groups and the total index are positive and present. We multiply 12 or 24 previous-month relatives, beginning after December 2017. The resulting total-index changes are 1.515% and 8.618%, respectively. This independently checks the official rounded 2018 December-over-December 1.5% and 2019 7.0% one-year series on [Geostat's CPI page](https://www.geostat.ge/en/modules/categories/26/cpi-inflation).
- The release's detailed CPI workbook spans 2011–2026; its 2017, 2018, and 2019 sheets have 305, 305, and 306 price item rows respectively, with no blank or nonnumeric monthly relatives in those rows. It identifies CPI divisions, but item-specific expenditure weights are not in the release. We therefore use official group indices rather than an unweighted average of item relatives. The release's annual consumer-basket workbook gives CPI group weights, not weights for each listed item.
- Versioned mapping: `crosswalk_2017_v1.csv`. The exact survey labels are retained. Clothing → CPI 3, household goods → CPI 5 (imperfect scope), healthcare → CPI 6, fuel and electricity → CPI 45 (gas ambiguity), transport → CPI 7, education → CPI 10. Food/beverages/tobacco, other consumption, and noncash consumption are unmatched and remain in the denominator. `saojaxo` and `energia` are disclosed approximations; removing them is a useful sensitivity check before treating even partial results as stable.
- Eight cash fields sum exactly to `samomxmXarjebi`; cash plus noncash consumption equals `MTlianimoxmareba_`; cash plus noncash expenditures equals `MTlianixarjebi_` for every row (tolerance 1e-7 GEL). Income identities also reconcile: cash income and transfers plus noncash income equals `Shemosavalisul`; cash inflows plus noncash income equals `Saxsrebi_Sul`. Borrowing/dissaving and property disposal are not treated as income. Required fields have no system missing values or negative amounts. User-defined missing codes in other fields have not been exhaustively classified.
- Survey-weighted mean monthly total expenditures are 1,092.21 GEL, within 0.79 GEL of [Geostat's published 2017 figure of 1,093 GEL](https://www.geostat.ge/en/modules/categories/51/households-expenditures). Weighted cash and noncash inflows are 1,110.72 GEL, matching the published [1,110.7 GEL](https://www.geostat.ge/en/modules/categories/50/households-income). Differences in published rounded figures and annualization explain no more than the stated gap; exact provider tabulation settings remain unverified.

## Estimand and uncertainty

For each 2017 household-quarter observation, the computed partial percentage-point contribution is `100 × sum(matched monthly expenditure × (chained group CPI − 1)) / total monthly consumption`. It holds the 2017 expenditure basket fixed at December 2017 prices for an illustrative counterfactual; survey interviews occurred throughout 2017, so the basket is **not** a literally observed December basket. Weighted quintiles use `MTlianimoxmareba_EqAdScale` and household weights; they are household, not person, quintiles. A household with either a pension-age man or woman is in the pensioner group. Urban/rural codes are 1/2 in the survey schedule.

The CSV includes 300 seeded percentile bootstrap intervals based on resampling `DiaryID` clusters. For the all-household 2018 contribution the exploratory interval is **0.643–0.675 pp**. The public files do not provide a verified PSU or stratum identifier. These intervals omit multi-stage survey design and CPI uncertainty; do not read them as design-valid confidence intervals. The survey's repeated household observations have been clustered, but not treated as an independent annual panel.

## Reproduction and gates

Run `python src/release_download.py`, then `python src/release_validation.py`, `python src/pilot2017.py`, and `python -m unittest discover -s tests -v` after installing `requirements.lock`. The group CPI is fetched from the official URL and pinned to the hash above. Raw microdata stay outside Git. CSV, validation JSON, crosswalk, and figure are committed.

The release downloader records all 13 outcomes independently: 11 pass, while 2020 and 2023 match their release-declared hashes but have invalid ZIP central directories. Those two archives are excluded. **GO** for this labeled partial descriptive result. **NO-GO** for a precise full-household inflation index until mixed categories and noncash consumption are allocated with evidence; **NO-GO** for causal NBG or household welfare claims. The causal-identification track in Phase 1 remains a separate later task.
