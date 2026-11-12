# Reserve adequacy and usable foreign liquidity

**R2 decision.** The public balance sheets support an independent reconstruction of the conventional reserve benchmark, a schedule of disclosed drains and tests of the published model equations. Georgia's official component vectors and the model's numerical optimum remain unreproduced. G4 remains partial. These results cannot value the additional insurance purchased during the episode.

## How much cover did Georgia have?

At end-2025 gross international reserves were USD 6,159.28 million. Applying floating-regime weights to public inputs gives the following results. Amounts are USD millions. Coverage is gross reserves divided by the reconstructed denominator.

| Domestic money measure | Reconstructed denominator | Coverage | Gap to April 2026 IMF DataMapper |
|---|---:|---:|---:|
| M2 | 6,369.80 | 96.70% | +1.84 pp |
| M3 | 6,792.38 | 90.68% | −4.17 pp |

The denominator is 5% of annual goods and services exports, plus 5% of broad money converted at the closing rate, plus 30% of external principal due within one year outside direct investment, plus 15% of portfolio and other investment liabilities after removing that principal. This last subtraction avoids counting the same debt twice. The QEDS payment schedule is a proxy for a residual-maturity position. Deposits, arrears, direct investment and revisions must be treated consistently to match an institutional vintage.

At end-2025 the QEDS sector sum was USD 7,811.56 million, including USD 375.15 million of intercompany principal. Its supplementary maturity series reported zero alongside positive scheduled principal. The reconstruction excludes that supplementary observation. In June 2026 the national and QEDS total principal schedules differ by USD 0.453 million, entirely in other sectors. The output preserves the discrepancy.

The change in money definition shifts the 2025 denominator by USD 422.59 million and coverage by 6.02 percentage points. Compare the published 94.85% in April 2026 DataMapper, 100% in the 2026 Article IV staff table (p. 4) and 104.8% in NBG's 2025 Annual Report (p. 47). Neither construction matches all three. Differences in component vintages and institutional adjustments remain unresolved. The common-numerator implied denominators in the concordance are diagnostic. The June 2026 trailing-four-quarter M3 result is 101.40%. Only M3 could be independently tied to the June closing balance in the depository survey.

[Component observations](ara_components.csv) · [Vintage comparisons](ara_vintage_concordance.csv) · [Debt schedules](one_year_principal.csv) · [Sector reconciliation](national_qeds_reconciliation.csv)

## Liquidity in a stress

The NBG reserve template permits 1-, 3- and 12-month calculations at 22 month-ends from December 2024 through September 2026. At end-2025, deducting disclosed net predetermined section II.1 drains over twelve months leaves USD 4,821.39 million. Calling all section III.1 contingent claims leaves USD 2,646.17 million. Assuming all gold is also unavailable leaves USD 1,643.85 million. These calculations assume disjoint incremental claims, face value for remaining assets and no other net flows. They supply neither stress probabilities nor a verified unconditional usable stock. Blank collateral disclosures remain missing. The three cumulative horizons must never be added together.

In a separate bank self-insurance calculation, assume access to 0%, 50% or 100% of banks' short external deposits and securities, capped by their short deposit liabilities and the measured debt exposure. Reducing the 30%-weighted debt component by the covered amount times its weight takes 2025 M3 coverage to 90.68%, 95.98% or 101.93%. Access assumptions alone can move coverage across 100%. Bank assets belong to banks. This exercise establishes no NBG right to draw on them. The simple historical adjustment also misses the IMF's published adjusted denominator by USD 270.4 million in 2022 and USD 262.8 million in 2023.

[Reported schedules](liquidity_schedule.csv) · [Stress assumptions and outcomes](liquidity_stress.csv) · [Bank buffers](bank_buffer_sensitivity.csv) · [Historical adjustment](historical_adjustment_check.csv)

## Cangul and Abel benchmark

Page references refer to Selected Issues Paper SIP/2026/051. The implementation separates the p. 6 baseline, p. 13 expected utility, p. 14 marginal condition and p. 15 dollarization channel.

| Input or convention | Value used | Basis and limitation |
|---|---|---|
| Crisis probability | 0.10 | Published sensitivity point. A horizon must be matched before interpreting marginal rates |
| Log spread slope | 0.0575 | Interpretation of p. 14 in fraction units. From 10% to 20% reserves/GDP the spread falls 50.03 basis points |
| Fixed loss in the p. 14 diagnostic | 0.10 of GDP | Illustrative choice drawing on the p. 15 base loss. The p. 14 calibration is unconfirmed |
| Dollarization and crisis loss | 0.60 − 0.10 log(1+r), loss = 0.10 × (1 + 0.50 × dollarization) | Printed p. 15 channel, r is reserves/GDP |
| Nominal GDP | USD 38.1 billion | Rounded 2025 GDP, 2026 Article IV p. 4. With statistical reserves gives r = 0.16166 |
| Baseline debt, loss, premium, risk aversion and solver bounds | Unresolved as a jointly verified Georgian calibration | No parameter fitted to recover a published target |

The literal p. 13 specification has a domain problem if reserves are unbounded and the log spread has positive slope coefficient and no floor. As reserves increase without limit, the spread becomes negative without limit. Both normal-state consumption and crisis-state consumption then increase without bound. Any finite feasible allocation is eventually dominated under increasing utility. An upper bound, spread floor or different financing specification can change this result. The authors' implemented domain is unknown.

The p. 14 average-loss condition also differs from differentiating the p. 13 utility function. Under the illustrative fixed loss above, the combined cost intercept required for a stationary solution reaches its minimum of 635.52 basis points at reserves of 39.66% of GDP. Below that intercept the equation has no positive root, at the threshold one, and above it two. Root existence alone does not select an optimum. At the observed end-2025 reserve ratio the isolated p. 15 loss derivative gives a marginal carrying-rate equivalent of 4.78 basis points under the same probability and horizon assumption. It excludes other welfare channels.

The reported baseline near 130% of ARA and combined recommendation of 145–150% remain nonreplicated. Resolving them requires the Georgian parameter vector and ARA conversion, implemented objective and bounds, and joint simulation specification, shocks and working-liquidity overlap adjustment. The public calculations neither validate nor refute the numerical recommendation.

[Equation diagnostics](model_equation_checks.csv) · [Channel-specific missing inputs](model_target_status.csv)

## Replication

From the repository root run `python src/r2_reserves.py --check` for a byte comparison of the ten generated tables and their validation record against tracked observations. With pinned NBG and QEDS raw files present, `python src/r2_reserves.py --from-raw --check` also rebuilds the QEDS and bank extracts. Run `python replication/check_repository.py` for the wider suite. The R2 acquisition script checks the source pins and records partial failures. Two supplementary background PDF retrievals failed. The archived model paper and verified provider observations support the calculations above.

[New source manifest](../../data/r2_source_manifest.json) · [National source manifest](../../data/source_manifest.json) · [Archived model source register](../../archive/legacy/reports/paper/sources.json) · [Archived IMF source register](../../archive/legacy/reports/reserve_foundations/sources.json) · [Input and output hashes and numerical checks](validation.json)
