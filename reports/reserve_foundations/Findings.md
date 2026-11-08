# Reserve adequacy and financial accounts: quantitative results

Research results, 9 November 2026. Baseline commit: `74ed88d58f37c8436b83eb72f4828c84bfc6ceba`. This release adds observations and calculations; it is not an academic-paper draft.

## Component reconstruction

Using the floating-rate ARA weights, the metric is 5% of exports of goods/services + 5% of M2 + 30% of residual-maturity short-term debt + 15% of other liabilities. All components below are USD million from the IMF's 2024 Article IV report, PDF p.53, printed p.48. The source page was also inspected visually. These are independently recomputed metrics **from the IMF's published component estimates**, not independently estimated national-account inputs.

| Component | 2022 | 2023 |
|---|---:|---:|
| Exports | 13,240 | 15,161 |
| M2 | 7,324 | 9,349 |
| Short-term debt, residual maturity | 4,811 | 5,282 |
| Other liabilities | 15,504 | 16,242 |
| Reconstructed ARA | 4,797.10 | 5,246.40 |
| Published ARA | 4,797 | 5,246 |
| Gross reserves | 4,901 | 5,009.7 |
| Reconstructed coverage | 102.166% | 95.488% |
| Reserves/M2 | 66.917% | 53.585% |
| Reserves/residual-maturity short-term debt | 101.871% | 94.845% |

The reconstruction reconciles within a USD 0.8m bound allowing rounded components and rounded published ARA. The 2024–2028 columns are retained in CSV **as projections from the 2024 vintage**. They are never substituted for realized observations. Import-cover ratios are retained as published figures, without claiming independent reconstruction of an import denominator not extracted here.

The ARA denominator rose USD 449.30m between 2022 and 2023: exports contributed USD 96.05m, M2 USD 101.25m, short-term debt USD 141.30m and other liabilities USD 110.70m. Reserves rose only USD 108.70m in this source vintage. Thus the decline in coverage is materially a denominator story, not evidence that reserves fell. Original NBG series have slightly different precision/vintage; do not splice them into this calculation silently.

## An unreconciled bank-buffer adjustment

The report also lists banks' short-term external deposit assets and liabilities. A transparent mechanical alternative replaces gross deposit liabilities by their nonnegative uncovered amount. Under the standard 30% debt weight this subtracts 30% of the lesser of bank assets and liabilities from ARA.

That calculation yields USD 4,230.40m in 2022 and USD 4,609.80m in 2023, versus published adjusted metrics of USD 3,960m and USD 4,347m. The remaining gaps are USD 270.40m and USD 262.80m, far exceeding rounding. The two adjustments therefore are not demonstrated to be identical. The net deposit amounts themselves reconcile: 2,778−1,889=889 and 3,141−2,122=1,019. This identifies an adjustment-definition or additional-input gap, not an accounting loss or proven IMF error. The conventional metric passes; the adjusted metric is not fully reproduced.

Some projection debt totals also fail the simple original-maturity debt plus amortization identity; these residuals are retained by year in `ara_reconstruction.csv`. The historical 2022/2023 debt splits reconcile exactly. Do not repair projection discrepancies by allocating them arbitrarily.

## Measured interest and FX exposures, 2020–2024

The 2021, 2023 and 2024 NBG audited statements and their comparative columns supply the historical observations. Amounts below are GEL million, accrued annual interest. Negative interest on reserve assets is deducted separately; an absent separately reported line in later statements is explicitly identified in the observation ledger and treated as zero for this category calculation, not as evidence of zero total reserve expenses.

| Year | Reserve interest after separately reported negative interest | Monetary-operation interest expense | IMF interest expense | FX assets minus FX liabilities, year end |
|---|---:|---:|---:|---:|
| 2020 | 123.411 | 46.587 | 12.602 | 4,537.659 |
| 2021 | 62.397 | 58.665 | 19.857 | 4,152.333 |
| 2022 | 139.593 | 80.946 | 46.347 | 4,487.277 |
| 2023 | 479.640 | 106.380 | 102.343 | 6,020.217 |
| 2024 | 439.181 | 95.361 | 101.102 | 3,348.369 |

All five annual total-interest expense and net-interest identities reconcile. Overlapping 2023 observations from successive audited reports agree for every extracted series. Source rows, hashes and exact PDF pages are retained. Currency translation, gains/losses, fees and reserve composition are not conflated with interest.

These data establish that reserve interest varies substantially across the rate cycle. They do not establish a reserve-accumulation profit: the expense categories finance broader central-bank operations; liabilities have different currencies and functions. IMF charges are not automatically wholly attributable to reserve holdings. FX assets less FX liabilities is a balance-sheet exposure, not usable reserves or the IMF NIR definition. Neither closing balances nor GEL accounting amounts are used to invent a matched-currency annual yield.

## Economic scale of alternative levels

Under the 2023 historical component denominator, 100%, 130%, 145% and 150% ARA correspond to USD 5,246.40m, 6,820.32m, 7,607.28m and 7,869.60m. Relative to that vintage's USD 5,009.70m reserves, the 145–150% levels require USD 2,597.58–2,859.90m more reserves. Assumed annual marginal net carry of 1–4% gives USD 25.98–114.40m/year across those endpoint combinations. Full level-by-cost combinations are in `reserve_level_scenarios.csv`.

These are **retrospective conditional financing scenarios**, not measured costs or a current recommendation. The carry is assumed to include the relevant return/funding spread, so reserve interest must not be subtracted again. Crisis insurance, liquidity services and spread benefits are not valued here. A positive carry cost alone does not reject accumulation. Conversely, an ARA ratio alone is not a welfare objective.

## Vintage evidence relevant to Cangul and Abel

The downloaded 2025 Article IV report's external-sector discussion (PDF p.58) gives 2024 coverage of 77.3%, or 83.5% with its bank-liability adjustment. The 2026 report (PDF p.53) describes end-2025 gross reserves around USD 6.2bn and 100% coverage, and reports USD 463m valuation gains, mainly gold. These observations show why reserve growth cannot be equated to FX purchases. They are recorded in the separate vintage ledger. They do not supply the full component vectors needed to independently reconstruct those later ratios.

Cangul and Abel's 2026 recommendation cannot legitimately be evaluated by applying 2024 projections or the 2023 denominator to current reserves. This release supplies the earlier component reconstruction and five-year financial accounts. **The 2024–2025 realized component reconstruction remains incomplete**, as does the precise published bank-adjustment rule. The exact remaining records are dated M2, exports, residual-maturity debt and other-liability vectors in the 2025/2026 IMF vintages, their original NBG source mappings, and the authors' GDP/ARA conversion. No later denominator is back-solved and mislabeled as independent evidence.

The new financial history supports measured category costs and exposure comparisons. A reserve-specific marginal cost requires instrument/currency balances and remuneration averaged over the holding interval, portfolio returns by currency and a financing allocation. Those missing allocations are why the conditional cost grid is kept separate from the measured accounts.
