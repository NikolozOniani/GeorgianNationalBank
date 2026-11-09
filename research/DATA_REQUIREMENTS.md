# Research-data requirements and acquisition plan

**Study:** The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author:** Nikoloz Oniani

**Fixed question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

Scope and counterfactual are fixed in [the protocol](PROTOCOL.md). This is an actionable data specification, not a new empirical study. The [machine-readable register](data_requirements.json) contains the exact variables, units, frequencies, periods, access status and validation requirements for **18 datasets**. Source IDs below refer to the [primary-source register](SOURCES.md).

## 1. Existing data: what can be reused immediately

The supporting archive has useful accounting inputs but does not yet identify the episode's exchange-rate effect. Reuse the following without reacquiring completed historical data:

- **60 monthly observations, 2020–2024:** reserve stocks/components, official month-end exchange rates, policy rates and TIBR. The intervention, government-FX and reserve-valuation fields are blank throughout. Missing does not mean zero.
- **Two annual intervention benchmarks, 2023/2024, and one executed auction sale:** useful for reconciliation and schemas. They do not supply 2025–2026 executed purchases or monthly gross flows.
- **1,250 daily TIBR observations in 2020–2024:** a pre-episode money-market reference. The separate policy decision file already extends through the **21 October 2026 decision, effective 22 October**; inspect/reuse those observations before requesting the same history again.
- **20 quarterly external observations:** limited pre-episode BOP information. Quarterly data cannot be converted into observed monthly or daily flows by interpolation.
- **Audited 2020–2024 reserve-interest, monetary-operation expense and FX exposure categories:** a historical cost/return reference. Year-end exposures and annual interest are insufficient to price the incremental reserve purchases.
- **Standard ARA reconstruction for historical 2022/2023:** an arithmetic check on the IMF's published components. Later columns in that 2024 source are forecasts. The adjusted metric remains unresolved; none of these columns is an independently reconstructed realized 2025–2026 component vector.
- **Limited Cangul-Abel model audit:** useful questions about derivatives, units and channel magnitude. It is not a full replication of the objective, simulations or optimum.

Exact files, source manifests and limitations are in the [evidence catalogue](../evidence/README.md). Historical household and credit work is preserved but excluded from the active study.

## 2. Acquisition period and priority

Collect the **2025–2026 purchase episode**, with **2024 opening balances and pre-episode observations**, extending relevant pre-period series to **2020**. A longer 2015–2019 history is justified only where it supports a specified model and comparable definitions. Historical stress data can extend further for insurance calibration. These extensions do not create additional treatment episodes.

The source review is frozen at **8 November 2026**. Full-year 2026 transactions, annual financial statements and future observations are not yet available as completed annual data. Maintain an explicit last-observed date for every series and estimate on an agreed information vintage. Fix the episode boundary from execution and policy evidence before examining estimated effects.

**P0** identifies the treatment and counterfactual. **P1** establishes costs and benefits and can proceed alongside public P0 acquisition. **P2** refines consequences after the essential records are secured.

| Priority / ID | Required observations and frequency | Sources and current access | Deliverable / what a missing record prevents |
|---|---|---|---|
| P0 / D01 | Executed gross purchases/sales by BMatch, auction and other instrument; original currency, price, trade/settlement/disclosure times; transaction or daily | S01–S06, S29. Public monthly net summaries and auction results; full gross/day-level BMatch detail requires investigation or request | Reconciled treatment ledger. Without it, no credible daily purchase exposure or complete no-purchases inventory path |
| P0 / D02 | Pre/post USD/GEL quotes, trades, volume, bid–ask spread, market depth and non-NBG order flow; tick/1–5 minute and daily | S01, S07, S29. Public market aggregates; historical Bloomberg access/licensing or anonymized NBG records unresolved | Price-impact and market-depth evidence. The daily official fix cannot substitute for a pre-execution quote |
| P0 / D03 | USD/GEL, EUR/GEL, daily NEER and monthly REER with dates, weights and direction | S01, S02, S07, S08. Public; existing API pattern reusable | Aligned observed exchange-rate path and robustness outcome |
| P0 / D04 | Applicable BMatch/auction rules, thresholds, quantity constraints, deviations, information sets and anticipated operations; dated events | S05–S07, S29. Public descriptions are partial; detailed historical rule/decision inputs require investigation/request | Assessment of exogeneity, anticipation and selection. A rule contingent on appreciation is not an instrument merely because it is a rule |
| P0 / D05 | Government conversions, Treasury FX balances, disbursements, debt service and Eurobond settlements; daily/monthly | S06, S09, S14, S23, S24, S29. Public debt totals; conversion channel and settlement detail may require NBG/MoF request | Separate NBG market demand from government FX/accounting flows and contemporaneous financing shocks |
| P0 / D06 | Trade, travel/services, transfers, investment flows and nonresident deposits; native monthly/quarterly plus dated news | S01, S02, S10, S21–S23, S28. Public aggregate data; daily client flows unresolved | Competing explanations for appreciation pressure; explicit endogenous versus exogenous controls |
| P0 / D07 | Global USD, regional FX, USD rates and risk measures; daily with release times | S25–S27. Public global series; comparison-country intervention coverage unresolved | Common-shock controls. No unexamined comparison currency or automatic exclusion restriction |
| P1 / D08 | Reserve components, market/government transactions, income, FX/gold/securities valuation, reclassifications; monthly bridge | S04, S09, S10, S14–S16, S29. Public stocks and some flows; full decomposition may require request | Reconciled additional reserves. An unexplained residual remains unexplained |
| P1 / D09 | Refinancing, one-month operations, CDs, facilities, securities, bank reserves and maturities; daily/auction balances | S01, S02, S11, S12, S14, S29. Public instruments and broad tables; detailed averages unresolved | Liquidity absorption versus reduced refinancing. Gross purchases do not determine financing costs by themselves |
| P1 / D10 | Policy/facility rates, TIBR/volume, CD and Treasury yields, reserve requirements; event/daily | S01, S02, S12, S13. Public; policy decisions already partly acquired through 2026 | Actual rates and policy changes needed for both paths; avoid duplicate acquisition |
| P1 / D11 | Average reserve holdings by currency/instrument, income, fees, valuation, duration and liquidity; monthly plus annual audit | S14–S16, S26, S29. 2025 annual report listed publicly; granular exposure/return may need request | Matched portfolio return and risk. Foreign short rates alone are not measured reserve returns |
| P1 / D12 | Funding liabilities, remuneration, IMF/SDR charges and earning assets displaced by purchases; monthly averages/accruals | S11, S12, S14, S15, S23, S29. Public broad accounts; detailed attribution unresolved | Incremental financial cost and public-sector consolidation, without charging all NBG expenses to reserves |
| P1 / D13 | Realized exports, M2, residual-maturity debt, other liabilities, ARA weights/adjustments; annual/quarterly vintages | S09, S11, S17, S18, S21, S22, S28, S29. Public aggregates; precise component export and adjusted rule unresolved | Independent ARA denominator and explanation of reported-ratio differences |
| P1 / D14 | Usable assets, encumbrances, derivatives and predetermined/contingent drains, bank buffers; monthly/quarterly by maturity | S01, S09, S16, S18, S22, S23, S29. Public template and aggregate external statistics; usability and stress access require investigation | Liquidity insurance rather than gross reserves alone |
| P1 / D15 | Original Cangul-Abel/QIPF code, calibration, objective, constraints, horizon and simulation draws; versioned | S18–S20. Public papers; replication package not obtained; investigate supplements, then request from authors/IMF | Replicated benchmark and meaningful sensitivity. Printed inconsistencies are not proof of code failure |
| P1 / D16 | Eurobond prices/spreads, maturity-matched risk-free curve, issue terms/fees and refinancing volumes; daily/event | S01, S23–S27. Public issue/debt information; secondary-price source/license unresolved | Financing benefit on actual exposure, subject to causal attribution; not the whole debt stock multiplied by an unexplained spread change |
| P1 / D18 | Crisis likelihood, duration/loss, financing gaps, usable buffers, alternative facilities and discounting; historical events/quarterly | S09, S16, S18–S20, S23. Public history and model assumptions; country-specific marginal benefit unresolved | Same-horizon insurance valuation and break-even conditions; no invented crisis probability |
| P2 / D17 | Trade/income currency exposure, sector FX positions, invoicing/hedges, quantity and price responses; monthly/quarterly | S01, S21–S23, S28, S29. Public broad exposures; fine detail investigation/request | Consequences of the same exchange-rate counterfactual, with real resource effects separated from transfers |

## 3. What identifies the exchange rate without purchases?

The decisive missing evidence is **why, when and in what quantity NBG purchased relative to the market information available at that moment**. Purchases during strong inflows are selected precisely when the lari could appreciate. Regressing the exchange rate on purchases would mix that selection with the effect of NBG demand.

D01–D04 must establish the time sequence and whether any purchase variation can be treated as independent of unobserved FX demand. D05–D07 address competing government, private and global flows. An announced-versus-executed auction difference is not automatically a surprise; a delayed BMatch disclosure is not its execution shock. A contemporaneous global variable that also affects GEL directly cannot serve as an excluded instrument merely because it predicts purchases.

With valid local variation, estimate price impact and test duration, anticipation, placebo dates and sensitivity to concurrent news. The full episode requires a dynamic model connecting those effects to expectations, private flows and monetary responses. Without valid quasi-experimental variation, the counterfactual must remain explicitly structural and conditional, with parameter ranges, validation and feasibility checks. Monthly aggregates can reconcile an episode but cannot by themselves identify a precise two-year path from a short sample.

Do not select an instrument, threshold, comparison country or preferred model because it produces a larger appreciation estimate. Register the selection argument and tests before outcome estimation. Distinguish uncertainty in measured flows, model parameters and identification assumptions; a regression confidence interval does not cover all three.

## 4. What is needed to measure costs and benefits?

**Financial cost:** D08–D12 must link additional reserves to the actual change in remunerated liabilities or foregone earning assets. Required quantities are average outstanding balances, rates, currency and duration, with accrual/settlement alignment. The 2025 audited statement is the next public accounting anchor. Monthly 2026 information can be provisional, but cannot be called a completed annual audit.

**Economic cost:** D17 links the estimated counterfactual exchange rate to external purchasing capacity, production margins and currency exposures. The welfare measure needs behavioral response, incidence and a feasible alternative. A nominal valuation change, a domestic interest transfer and a real resource cost are different objects. Report measured components even if a national welfare total remains unidentified.

**Reserve benefit:** D13–D18 establish usable rather than headline reserves, stress drains, the model's insurance value, and any financing benefit on actual issuance/refinancing. Required assumptions are crisis probability per specified horizon, duration/severity, the marginal effect of accessible reserves and feasible alternative liquidity. Reconcile and test Cangul-Abel before applying its target to the episode. Do not count sovereign-spread relief, crisis-loss reduction and an FX liquidity buffer as three independent benefits when their mechanisms overlap.

The judgment compares the same observed and no-purchases paths on one horizon, numeraire and discount basis. Report the parameter combinations under which benefits exceed costs, and whether Georgian evidence rules any of those combinations out. ARA coverage alone cannot answer that question.

## 5. Availability and exact next acquisitions

1. **Public now, but incomplete in this repository:** 2025–2026 NBG net-purchase releases and auction results; daily official exchange rates; current TIBR/operation tables; reserve stocks and monthly balances; 2025 Annual Report; NBG/Geostat external flows; MoF debt and issuance records; IMF reserves template and ARA listing. Retrieve these first under new source vintages. Do not overwrite older hashes or treat a catalogue listing as an acquired dataset.
2. **Investigate before asserting a gap:** complete BMatch gross purchase/sale export, daily historical market volume, NEER export and weighting vintages, monthly reserve/currency return detail, current ARA component workbook, bank-adjustment definition, security-level market prices, and model supplements. The source register distinguishes a dynamic-page or reader failure from nonpublication. The 2025 Annual Report link is known; the reader's file-size limit is not a reason to request a publicly listed report.
3. **Likely request-dependent if public investigation fails:** nonidentifying BMatch execution times and gross daily flows, historical rule inputs/deviations, NBG-government FX conversions, separated valuation/flow bridges, average currency/instrument balances and remuneration, and usable-liquidity/stress information. Ask for aggregated or delayed disclosure when confidentiality prevents transaction-level release. The [NBG specification](NBG_REQUEST_SPECIFICATION.md) gives the fields and fallback detail. Model code belongs with the authors/IMF; licensed quotes belong with their provider. No requests have been sent.

Two verified definition risks require explicit treatment: S28 flags microbank coverage changes starting January 2025 and a growth-rate comparability transition in June 2026; S23 flags accrued interest included in debt stocks from 2026. Determine which selected series are affected rather than inserting a generic break dummy without investigation.

## 6. Required evidence before quantitative conclusions

The next substantive deliverable should be a **reconciled episode ledger and aligned market/liquidity dataset**, with coverage/missingness, source vintages, sign conventions and public-versus-requested detail. It must resolve G1 and identify the empirical support for G2 before a causal result is claimed. Concurrently acquire public D08–D14 so the reserve path and cost accounts can be evaluated on the same episode.

Then record the accepted identifying assumptions, the policy response in the no-purchases counterfactual, residual accounting discrepancies, cost allocation and insurance calibration. Only after G2–G4 are adequately supported should the joint assessment proceed. If one remains unresolved, release the valid accounting results and the conditional ranges with that specific limitation. Do not replace the fixed question or fill missing observations to manufacture a complete answer.
