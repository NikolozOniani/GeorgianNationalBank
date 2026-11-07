# Who Pays for Monetary Stability? Georgia research feasibility assessment

Phase 1 decision package • 7 November 2026 • No empirical estimates produced

## Decision

**GO for Phase 2 data acquisition and validation. NO-GO for causal welfare claims on the evidence currently verified.** The research question is viable; its strongest promised result—an identified welfare loss caused by NBG reserve purchases—is not yet feasible. Public disclosure frequency, endogenous policy timing, and incomplete household balance sheets are binding obstacles, not details to resolve after estimation.

This package provides all eight requested planning components. It is a scoped primary-source literature review and feasibility assessment, not a completed systematic review or validation of all historical datasets. Dataset-specific verification levels are stated below. Phase 2 must close the access and definition gaps before estimation. No academic manuscript or Georgian investigative report is warranted.

The public-facing premise remains untested. A weaker lari can raise consumption costs while benefiting foreign-currency income recipients and asset holders; sales can protect unhedged borrowers while depleting insurance buffers. Neither the exchange-rate direction nor central-bank accounting profit measures net household welfare.

## 1. Literature review and documented search protocol

### Protocol and evidence quality

Search date: 2026-11-07. Sources: IMF publications/eLibrary, NBG, Geostat, BIS, NBER, journal publisher and author pages. Search families included Georgia 2025/217 FX intervention; Georgia 2025/2026 Article IV; macroprudential policies and dollarization 2021; NBG pass-through research; IPF quantitative models; reserve adequacy; FX intervention and credit; shock-dependent pass-through; monetary redistribution; distributional CPI. Both web search engines were used for core institutional sources.

Include primary institutional documents, original theoretical/empirical research, methods papers, and official metadata. Retain contrary findings. Exclude media claims as empirical evidence, undated commentary, and numerical claims without traceable sources. Treat duplicate working-paper/journal versions as one research contribution. Record publication vintage separately from access date; do not treat a report's forecasts as later realized outcomes.

Quality codes: **I** institutional description/measurement; **S** structural/model-dependent; **E** empirical evidence requiring identification appraisal; **M** measurement/methodology. These are evidence types, not a ranking of institutions. Search/abstract-only papers are explicitly identified; they cannot support detailed reconstruction or effect-size transfer. Full-text review of every cited paper and comprehensive citation-chain saturation remain open. No claim of a completed exhaustive review is made.

### Mandatory 2025 IMF benchmark: reconstruction

IMF Country Report 25/217, pp. 4–18, uses a Bayesian QIPF DSGE estimated on quarterly Georgian data, 2000–2023. Limited FX intermediary risk-bearing capacity gives sterilized intervention real effects. Historical exercises examine 2020–2024; counterfactuals remove intervention or replace shallow markets with deep ones. Intervention is proxied using external estimates and NBG information. The no-intervention exercise implies higher peak core inflation and policy rates in 2020–2021, by 1.5 and 2.4 percentage points respectively. These are model outputs, not experimentally identified effects. The report also warns about depleted reserves, credibility, market development, and mistaking fundamental news for sentiment. Its short-run benefits do not establish net long-run welfare gains—or losses. [R1]

Replication priorities: obtain executable code, data vintages, observation equations, priors, filtering/smoothing settings, intervention-proxy construction, policy closure, and shock histories. Reproduce the published counterfactuals before extending the model. Source code and complete replication inputs were not verified here. Do not digitize charts and call that model replication.

### Synthesis across the required literature

| Literature | Verified reference and review depth | Implication for this project | Evidence limit |
|---|---|---|---|
| Sterilized/nonsterilized FXI; shallow markets; policy transmission | Adrian et al. 2021 WP 21/292; Chen et al. 2023 WP 23/135; IMF 2023 FXI principles [R6–R8], publication/abstract and selected text | Separate FX portfolio effects from monetary accommodation. Model policy-rate and liquidity responses jointly. | S/I: model mechanisms do not establish a Georgian intervention shock. |
| Intervention measurement | Adler et al. 2021 WP 21/47 and IMF WPFXI [R9], metadata/selected text | Transaction data outrank unadjusted reserve changes; preserve official/proxy distinction. | M: proxy error can contaminate timing and magnitude. |
| Exchange rates, dollar pricing, pass-through | Gopinath et al. 2020; Forbes et al. 2018/2020 [R10–R12], abstracts | Invoice currency and the shock causing depreciation matter. Avoid applying one unconditional pass-through coefficient to every intervention. | E/S: foreign-country coefficients are not Georgian estimates. |
| Georgian financial dollarization and prices | Sopromadze, Barbakadze and Mkhatrishvili 2021, NBG WP 01/2021 [R5], relevant full-text sections | Domestic producers' FX liabilities provide a cost channel in addition to imported inputs. | E/S: panel evidence and a model, not a causal estimate of NBG purchases; working paper is explicitly not peer-reviewed. |
| Prudential policy and currency mismatch | IMF 2021 FSAP, CR 21/220 [R4], executive summary/selected text | Include borrower credit risk and bank FX liquidity. Dollarization policy alters transmission across time. | I: institutional assessment cannot identify household treatment effects. |
| Optimal reserves and insurance | Jeanne–Rancière working-paper precursor (2006); IMF 2026 Georgia reserve study; ARA guidance [R13–R15], abstracts/selected sections | Balance carrying costs against crisis consumption smoothing; adequacy is state-dependent. | S/M: crisis probabilities, severity and opportunity costs drive rankings. |
| FXI and credit supply | Hofmann, Shin and Villamizar-Villegas, BIS WP 774 [R16], abstract | Sterilization does not imply zero credit effects; study bank capital and borrower mismatch. | E: Colombia's microdata evidence cannot be imported as Georgia's coefficient. |
| Monetary redistribution | Auclert 2019 [R17], publication/abstract | Earnings, nominal wealth and interest-rate exposure must accompany consumption prices. | S/E: required Georgian exposures remain unverified. |
| Inflation heterogeneity | Jaravel 2021 review and 2024 DP19802 [R18–R19], publication/abstract | Household baskets support distributional price exposure; within-category prices and substitution remain important. | M/E: US patterns do not establish which Georgian quantiles lose. |
| Balance-sheet/sterilization accounting, hedging incentives | IMF FXI principles and NBG operations/statistics [R8, D3–D4] | Reconcile liquidity absorption, interest expense, reserve income, valuation and fiscal transfers; test incentive channels separately. | I/S: dedicated Georgian audited-account extraction and hedging evidence still needed. |

The 2025 Article IV recommends exchange-rate flexibility and opportunistic reserve rebuilding, while noting low reserve coverage and communication problems around monetary implementation. The 2026 Article IV materials instead describe stronger buffers and above-target inflation, supporting a tighter, data-dependent stance. These are different vintages, not contradictory observations of the same state. Full staff-report extraction encountered access restrictions; consulted sections and official release links are in the bibliography. [R2–R3]

The 2026 reserve study expands the Jeanne–Rancière framework with sovereign financing, dollarization and FX-market liquidity channels; its reported optimum is about 145–150% of ARA versus about 130% in its baseline. This is a model benchmark, not a demonstrated universal target. A study merely adding an optimal-reserve calculation would now duplicate existing work. [R14]

### Contribution and novelty test

The proposed contribution is a transparent bridge from separately identified or explicitly bounded intervention shocks to Georgian household exposure, combined with policy comparisons that price reserve insurance and disclose distributional weights. It must distinguish purchase and sale episodes, auction and BMatch instruments, and consumption-price exposure from total welfare.

Relative to R1, add household heterogeneity and explicit measurement/identification bounds. Relative to R14, add distributional incidence and uncertainty in policy rankings. These are proposed extensions, not established literature gaps: complete citation-chain review before claiming novelty. If independent intervention variation cannot be recovered, retitle the empirical contribution as distributional exposure and model-dependent policy analysis.

## 2. Source-verified inventory and access audit

Verification levels: **V1** official page found; **V2** definitions/documentation inspected; **V3** complete file downloaded and parsed; **V4** historical contents reconciled and validated. No dataset reaches V4 in this phase. Files downloaded only for access checks do not constitute Phase 2 acquisition.

| Component | Provider/source | Frequency, units, definition | Verification and actual usability | Gate |
|---|---|---|---|---|
| Household files 2009–2025 | Geostat [D1] | Annual packages; underlying quarter/month records; GEL flows and survey weights | V2. Page lists annual ZIPs. 2025 URL responds, but full transfers failed integrity; no household observations accepted. Other years not downloaded. | GO for acquisition; no estimation yet |
| Household metadata | Geostat [D2] | Household-quarter UID; DiaryID for time in sample; Weights; ProductCode; urban/rural and region | V2. Documentation names these fields, but annual schema equivalence is unverified. | Conditional GO for repeated cross-sections; NO-GO for assumed long panel |
| Detailed CPI | Geostat [D5] | Monthly indices, previous month=100 | V3. XLSX parsed; sheets 2011–2026; 2026 header January–October. 2011–2019 sheets have 316 rows, 2020–2026 310; investigate item changes. | GO for validation and crosswalk |
| CPI aggregate/category basket weights | Geostat [D6–D7] | Monthly indices; annual basket/classification metadata | V1. Page verified; historical weights and crosswalk not parsed. | Conditional GO |
| Auction transactions | NBG [D8], IMF exchange-arrangement annex [R3] | Event dates, bought/sold currency; exact units to confirm in export | V2 institutional disclosure; same-day results. Complete event file/timestamps not acquired. | GO for descriptive acquisition; causal gate closed |
| BMatch operations | NBG statement [D3] | Monthly disclosed transactions; execution-level fields not public in reviewed evidence | V2; monthly publication with lag. Historical export and sign conventions unvalidated. | GO monthly description; NO-GO intraday design |
| GEL/USD, NEER, REER | NBG [D4, D9] | Official GEL rate daily; effective-rate frequency/base to verify | V1/V2; daily official-rate mechanism documented; no full export parsed. | Conditional GO; official fix is not an intraday quote |
| Reserves and balance of payments | NBG [D4]; IMF [R15] | Stock vs transaction flows; frequency/currency/valuation to verify per series | V1; reserve composition, government operations, SDRs, gold and returns reconciliation open. | GO accounting acquisition; NO-GO stock-change FXI proxy |
| Policy rate, TIBR, liquidity, CDs, reserve requirements | NBG [D4] | Decision/daily/monthly series depending on instrument; rates %, stocks/flows GEL | V1, navigation identified; data exports not verified. | Conditional GO |
| Loans/deposits by currency, rates, credit | NBG [D4] | Aggregate banking series; currency shares and GEL/currency amounts | V1; household linkage and borrower hedging unavailable in this audit. | Aggregate GO; household incidence conditional |
| Audited accounts, monetary/financial stability reports | NBG [D4] | Annual accounts, periodic reports | Publication routes verified, relevant historical files not exhaustively reviewed. | GO documentary acquisition |
| Earnings, employment, imports, GDP | Geostat official statistics linked from D1/D6 | Household/aggregate, various frequencies | Candidate series; item definitions and access unverified. | Conditional GO |
| Remittances, tourism, capital flows | NBG external-sector routes [D4] | Monthly/quarterly flows; USD/GEL conversion required | V1 only. Money transfers must not automatically equal balance-of-payments remittances. | Conditional GO |
| Global dollar, foreign policy rates, commodities, fiscal stance | BIS, central banks, IMF, World Bank, Georgian Ministry of Finance | Daily to quarterly; provider-specific | Candidate controls; exact series/download/licensing not verified here. | NO-GO as analysis-ready inputs |

All inspected sources were accessed on 2026-11-07. Licensing and redistribution permissions remain unverified unless recorded otherwise. Public access is not a redistribution license. Missing observations, first usable dates, revisions and all units must remain **unknown** until parsed, not silently filled with assumptions. The checksum/access manifest records the complete CPI download and the NBG HTML inspection. No checksum is assigned to a successful household dataset because none was accepted.

### Data dictionary specification

One row per series/version: `series_id, provider, source_url, download_url, retrieved_at_utc, published_at, reference_start, reference_end, frequency, units, currency, scale, seasonal_adjustment, original_definition, instrument, sign_convention, observation_time, release_time, vintage, revision_policy, missing_codes, missing_count, license, permissible_use, local_filename, sha256, parser_version, validation_status`.

For household variables also retain questionnaire/table, year-specific name, label, recall period, unit of observation, population, weight type, PSU/stratum, household rotation identifiers, and crosswalk version. V2 documentation is not evidence that all fields exist in 2025. Do not join a member weight onto household expenditures. Separate cash income from borrowing, asset sales and withdrawals from savings.

Reserve identity to reconcile in Phase 2: end stock minus beginning stock = FX intervention transactions + other reserve transactions + investment income (consistent with accounting convention) + FX valuation + gold valuation + other adjustments. Avoid counting reinvested income twice. A residual is an unexplained reconciliation item, not intervention.

## 3. Causal-identification feasibility matrix

Define e as GEL per USD, so an increase is depreciation; purchases are positive USD acquired by NBG. Primary causal estimand: the response of log e and category prices to an unexpected, separately identified purchase, with sales estimated separately. Fix scale after validating market turnover and transaction units.

| Design | What it can estimate | Requirements and threats | Formal decision now |
|---|---|---|---|
| Intraday event study | Local surprise response at execution/announcement | Exact timestamps, pre-event expectations, bid/ask quotes, concurrent news; execution and disclosure differ | **NO-GO** with monthly BMatch/daily official fixes; reopen only with timestamped inputs |
| Daily auction event study | Short-window response around disclosed auctions | Announcement timing, auction selection, anticipation, hidden BMatch and policy simultaneity | **NO-GO causal**, conditional GO descriptive; dates alone are insufficient |
| Reaction function | Predictable intervention response to available information | Real-time information set, thresholds, policy regimes, market stress | **GO descriptive** after data validation; residuals are not automatically shocks |
| External IV / natural experiment | Local effect for instrument-induced intervention | Demonstrated assignment, exclusion and relevance; no verified instrument exists | **NO-GO**. Elections, remittances and global rates directly affect outcomes and are not default instruments |
| Threshold/RD | Local intervention effect near a rule cutoff | Documented pre-existing rule, running variable, no manipulation, no other cutoff policies | **NO-GO** pending rule and microdata evidence; “rules-based” is insufficient |
| Local projections | Dynamic responses conditional on a valid shock | Same identification requirement as IV; adequate sample and inference | **Conditional GO associational**; causal label barred without a valid shock |
| SVAR/sign restrictions | Set of responses under explicit restrictions | Restrictions independently defensible; shock separation and sensitivity | **Conditional GO structural**; cannot assume a purchase weakens GEL and then claim to test H1 |
| Matched episodes / cross-country controls | Comparative descriptive dynamics | Comparable shocks/regimes, no spillovers, defensible parallel trends | **NO-GO causal** on current evidence; supplementary description only |
| QIPF structural replication | Model-dependent common-shock counterfactuals | Verified code/data or transparent reconstruction; parameter identification and policy closure | **GO planning**, implementation conditional on replication inputs |
| Partial identification | Sensitivity sets under stated confounding/missing-channel bounds | Economically defensible bounds and proof of mapping | **GO design**; unbounded confounding can yield uninformative sets, which must be reported |

Pre-specify outcomes and shock construction before examining estimates. For any surviving design: test leads/anticipation, non-overlapping and matched placebo windows, alternate lags, structural breaks, alternative controls, leave-one-event-out sensitivity, heteroskedasticity/autocorrelation and overlapping-horizon inference. Use event or time blocks appropriate to dependence; do not inflate sample size with many households exposed to one aggregate shock. Instrument work requires weak-IV-robust intervals and exclusion arguments, not only a first-stage statistic. Negative controls must have a theory of zero response; nontradables are not automatically valid.

Avoid contemporaneous controls that are policy mediators. For total intervention effects, conditioning on post-intervention policy rates or credit can remove part of the effect. Pre-register a causal diagram and distinguish confounders from mediators.

## 4. Hypotheses and falsification matrix

Primary monthly horizons: 1, 3, 6, 12 months; 24 months secondary only if sample supports it. Intraday horizons require a separate timestamp protocol. Use two-sided 95% confidence sets and Holm correction across six primary hypothesis tests, with simultaneous horizon bands within each hypothesis; distributional/subgroup exploration receives separate false-discovery control. Failure to reject is not confirmation of zero. Economic importance thresholds must be frozen before outcome estimation, informed by measurement precision and policy relevance.

| Hypothesis | Outcome/null | Predicted sign under premise | Falsification / competing account | Decision |
|---|---|---|---|---|
| H1 | Purchase-shock response of log e; H0: response = 0 | Positive; sales need not be symmetric | Leads, news-adjusted placebos, no effect, opposite effect, sensitivity to hidden BMatch | NO-GO causal now |
| H2 | Category price response to the same identified intervention; H0: price response = 0 | Generally positive following depreciation, not universal | Direct global commodity/demand channels; different shock types; policy-rate offset | Conditional on H1 shock and category data |
| H3 | Bottom-versus-top quantile loss as share of pre-policy resources; H0: difference = 0 | Bottom larger under premise | Remittances, own production, debt/asset exposure, alternate quantiles and weights | GO exposure; NO-GO total causal welfare |
| H4 | Marginal net social benefit of reserves; H0: benefit-cost ≥ 0 at evaluated state | Negative only in alleged excessive-accumulation states | Higher crisis losses, financing benefits, dollarization effects, valuation correction | GO model-dependent design only |
| H5 | Candidate-minus-A welfare and stability constraints; H0: no feasible candidate improves welfare | Positive gain without violating constraints | Equal-shock tests, out-of-sample performance, parameter/risk-weight sensitivity | NO-GO dominance claim; GO comparison plan |
| H6 | Joint welfare/volatility/debt-distress response; H0: policy welfare gain ≤ 0 | Positive beneficial-policy alternative | Small insurance benefit, large consumption/credit cost, adverse distribution | Same evidentiary standard as H1–H5 |

No logical requirement makes H1 imply H3, or H4 imply H5. Purchasing FX may depreciate GEL while improving net welfare. A credible rejection of the public premise is an acceptable result.

## 5. Household mapping and model-comparison plan

For baseline household h, first-order fixed-basket price exposure is `L_h = sum_k s_hk * Δlog(p_k)`. Its GEL equivalent is baseline consumption spending times L_h. Positive L_h denotes an additional consumption cost, **not total welfare loss**. Freeze pre-policy shares where possible; show lagged and updated-share sensitivity. Aggregate with survey weights and disclose whether quantiles refer to people or households and whether resources are equivalized. Prefer weighted equivalized consumption quintiles initially, with income quintiles as sensitivity.

Use category-specific policy price responses only when identified; otherwise label the exercise observed inflation exposure or conditional scenario exposure. Propagate joint macro-estimation draws and survey sampling uncertainty; retain cross-category covariance. PSU/stratum information is required for design-based variance; if absent, disclose the limitation and seek provider guidance. Preserve household rotation dependence if verified. Treat rural own-produced food separately from purchased food and account for corresponding producer income.

Debt principal stocks, repayments and consumption are different objects. Add FX asset/liability and earnings channels only with matched data or clearly labeled bounds. A remittance's GEL revaluation is not necessarily a fixed foreign-currency transfer. Do not double-count consumption-price loss and real-income loss, or debt stock revaluation and the full stream of debt payments. Compensating variation requires an expenditure function and behavioral assumptions; the fixed-basket index alone is not CV.

| Regime | Operational rule to specify | Monetary/financing treatment | Principal stress test |
|---|---|---|---|
| A Observed | Separate auctions/BMatch and purchases/sales; estimate behavior with available information | Reconstruct rate, liquidity and sterilization jointly | Regime changes and measurement error |
| B Minimal intervention | Zero discretionary FXI; explicit emergency trigger, reserve-floor and exceptional financing provisions | Endogenous inflation-targeting response, not the observed rate path held fixed | Sudden stops, FX mismatch and market illiquidity |
| C Volatility contingent | Predefined spread/depth/realized-volatility threshold, caps and stop rule | Same monetary framework; liquidity effects explicitly offset or accommodated | False triggers from fundamental news; threshold manipulation |
| D Adequacy contingent | Reserve band, accumulation speed cap, market-liquidity condition; transparent emergency use | Consistent sterilization costs and reserve returns | ARA denominator shocks, unusable reserves, gold liquidity |
| E Constrained optimization | Optimize transparent implementable rule parameters rather than perfect-foresight actions | Full budget and balance-sheet consistency | Overfit, parameter instability, unrealistic information advantage |

Use identical initial reserves, debt stocks, shocks and information sets. Start historical comparisons only where observed inputs overlap. Use real-time information for decisions and distinguish historical decomposition from forward simulation. Run 1-year, 3-year and 10-year horizons with terminal reserve/debt conditions to prevent artificial gains from depleting assets at the endpoint. Include normal, capital-inflow, sudden-stop, commodity and fundamental-news scenarios. Define emergency external finance availability identically across regimes.

Report consumption-equivalent or explicitly defined money-metric welfare, inflation variability, FX variability, credit/output where supported, usable-reserve adequacy, and expected crisis loss separately. Crisis frequencies are model scenarios unless a defensible empirical probability model exists. The balance-sheet cost ledger includes interest paid, reserve income and operational costs; fiscal transfers and valuation are not automatically additional social losses.

Use equal-person weights, baseline-consumption marginal-utility weights, and a transparent prioritarian sensitivity family. Vary risk aversion and discounting; report rankings across the grid. An uncertainty-aware frontier retains nondominated rules across household welfare and expected crisis loss, with reserve and inflation constraints. No numerical frontier is produced in Phase 1. Require positive welfare gains with joint uncertainty and pre-specified noninferiority margins for stability before asserting dominance; if margins are unsettled, report the frontier without a winner.

## 6. Reproducibility specification

Phase 2 repository layout: README.md; pyproject.toml; a resolved dependency lockfile; data/raw with source manifests; data/processed; src; tests; notebooks; models; results; figures; manuscript (empty until authorized/supported); logs; references.bib.

Proposed commands: `fetch`, `validate`, `build`, `estimate`, `counterfactual`, `report`. Each command must fail when required inputs are absent or fail checksums. Pin Python and all dependencies after choosing a tested environment; do not fabricate a lockfile now. Use a fixed documented seed (proposed 20261107) and explicit random generators, with nondeterministic numerical components noted. Notebooks are views of scripted outputs, never the sole processing path.

Raw bytes are immutable; record HTTP source, retrieval timestamp, content type, SHA-256, release vintage and license. Every processed output links input hashes, transformation version and git commit. Restricted microdata stay out of git; provide retrieval and schema-validation instructions. Tests must verify transaction signs, stock/flow reconciliation, index chaining, survey weight handling, crosswalk coverage and missingness, identity uniqueness, no future information leakage, accounting identities and model limiting cases.

Maintain logs for assumptions, failed access/tests, identification limitations, model changes and protocol deviations. Snapshot the pre-analysis protocol before estimates; log exploratory deviations instead of silently rewriting it. CI runs small authorized fixtures, schema checks and deterministic builds; no artificial fixture is historical evidence. A clean rerun by the same implementation is reproducibility testing, not independent replication.

GitHub: a search of connected installations for “Georgia” returned no repository. No remote was selected or changed. The report and audit files are portable; an owner/repository destination is required before committing them remotely. Repository construction and dependency locking belong to Phase 2 under the mandate.

## 7. Identification-risk and uncertainty register

| ID | Risk and severity | Detection / mitigation | Consequence if unresolved |
|---|---|---|---|
| U01 | Endogenous intervention, critical | Validate assignment or explicit model restrictions; anticipation checks | Association only |
| U02 | Monthly BMatch timing, critical | Obtain execution records and disclosure timestamps | No intraday identification |
| U03 | Fundamental news misclassified as sentiment, critical | Add news shocks; real-time narratives; alternative decompositions | Structural welfare bounds widen; policy ranking can reverse |
| U04 | Reserve valuation mistaken for purchases, critical | Currency/gold/returns/government reconciliation | No transaction inference from stock changes |
| U05 | Household financial exposures missing, critical | Linked authorized data or explicit missing-channel bounds | No total household welfare claim |
| U06 | 2017 survey transition and rotation, high | Compare questionnaires, weights, frames and identifier rules by year | Analyze separate periods; no assumed long panel |
| U07 | CPI basket/item/quality change, high | Versioned crosswalk; unmatched expenditure mass; alternative aggregation | Restrict common coverage and disclose omitted categories |
| U08 | Pandemic, war, migration, political/fiscal shocks, high | Pre-specified breaks and information timing; influence diagnostics | Shorter samples, weaker power; no causal shortcut |
| U09 | Weak instruments and scarce events, critical | Weak-IV-robust inference; prospective power/MDE calculations | Report uninformative intervals; do not mine new instruments |
| U10 | Generated shocks/pass-through and sampling error, high | Joint uncertainty propagation, not fixed plug-in coefficients | No precise welfare claims |
| U11 | Crisis tails and reserve insurance uncertain, critical | Range of probabilities/severities; usable reserves; external financing assumptions | Scenario frontier only |
| U12 | Sterilization/fiscal double counting, high | Consolidated accounting with a single welfare ledger | Suspend aggregate loss estimate |
| U13 | Lucas critique and hedging responses, high | Endogenous expectations and portfolio sensitivity; implementable rules | Local counterfactuals only |
| U14 | Researcher degrees of freedom, high | Frozen outcomes/horizons, multiple-testing correction, null-result log | Exploratory designation |
| U15 | Downloads, licensing, revision vintages, high | Byte integrity, schema audits, provider terms, archived manifests | No redistribution or estimation from unvalidated inputs |
| U16 | Novelty overstated, medium | Forward/backward citations, 2026 benchmark comparison | Narrow or revise contribution |
| U17 | Imported coefficients/institutional authority substituted for identification, high | Country-specific evidence and sensitivity; separate opinion/model/data | No causal transfer of effect sizes |

## 8. Explicit Phase 2 handoff and stopping rule

1. Select the GitHub owner/repository and inspect its instructions. Create the documented research structure and tested environment. Preserve the original mandate unchanged.
2. Close literature access gaps: obtain complete 2025/2026 Article IV reports, the 2026 reserve paper, QIPF replication materials and relevant audited NBG accounts. Extend citation chains for FXI effectiveness, sterilization and welfare accounting. Record exclusions and review depth.
3. Retrieve and verify household packages and metadata across the 2016/2017 boundary and recent years first; only then expand through 2009–2025. Reject truncated archives. Inspect formats before choosing parsers. Resolve licensing.
4. Acquire intervention transactions and release metadata, FX quotes/fixes, reserves and reconciliation components, monetary/liquidity series, and a minimal justified control set. Do not infer absence of intervention from absent records.
5. Build the household-price crosswalk; validate weighted aggregates against Geostat publications; document own-production, non-consumption spending and recall periods. Establish usable FX financial-exposure fields or mark them absent.
6. Deliver a frozen dictionary, checksums, validation report, access log and updated identification matrix. Perform sample/event counts and prospective precision analysis before approving any causal design.
7. Reassess gates: causal work requires an independently defensible shock; total welfare requires sufficient channels or meaningful bounds; structural comparison requires replication inputs and internally consistent policy closures. Otherwise proceed only with explicitly descriptive/model-dependent components.

**Phase 1 stops here.** No regressions, calibrated policy results, manuscript, allegations, or Georgian public report have been produced. Phase 2 is a data and validation handoff, not permission to bypass these gates.

## Bibliography and source routes

Publication identifiers are supplied where verified. Access date for all entries: 2026-11-07. “Abstract/selected text” indicates limited review, not a claim to have read the entire work.

- **R1.** IMF (2025), *Georgia: Selected Issues*, Country Report 25/217, July 28; underlying report completed July 7. DOI 10.5089/9798229021029.002. [Official PDF](https://www.imf.org/-/media/files/publications/cr/2025/english/1geoea2025002-source-pdf.pdf), FXI chapter pp. 4–18 inspected.
- **R2.** IMF (2025), *Georgia: 2025 Article IV Consultation—Press Release; and Staff Report*, CR 25/216. DOI 10.5089/9798229017022.002. [Report](https://www.elibrary.imf.org/abstract/journals/002/2025/216/article-A001-en.xml). Selected text inspected; direct full-text route returned 403.
- **R3.** IMF (2026), *Georgia: 2026 Article IV Consultation*, CR 26/133. [Report](https://www.elibrary.imf.org/view/journals/002/2026/133/article-A001-en.xml); [annex](https://www.elibrary.imf.org/view/journals/002/2026/133/article-A002-en.xml); [June 10 official release](https://www.imf.org/en/news/articles/2026/06/10/pr-26197-georgia-imf-executive-board-concludes-2026-article-iv-consultation). Selected text/release inspected; direct report route returned 403.
- **R4.** IMF Monetary and Capital Markets Department (2021), *Georgia: FSAP—Technical Note—Macroprudential Policies and De-Dollarization*, CR 21/220, September 30. DOI 10.5089/9781557753533.002. [Official publication](https://www.imf.org/en/publications/cr/issues/2021/09/29/georgia-financial-sector-assessment-program-technical-note-macroprudential-policies-and-de-470360).
- **R5.** Sopromadze, Tamta; Giorgi Barbakadze; Shalva Mkhatrishvili (2021), *Dominant Currency Paradigm: Financial Dollarization View*, NBG WP 01/2021, April. [PDF](https://nbg.gov.ge/fm/wp/nbg-wp-2021-01.pdf).
- **R6.** Adrian, Tobias; Christopher Erceg; Marcin Kolasa; Jesper Lindé; Pawel Zabczyk (2021), *A Quantitative Microfounded Model for the Integrated Policy Framework*, IMF WP 21/292. [DOI](https://doi.org/10.5089/9781616356538.001).
- **R7.** Chen, Kaili; Marcin Kolasa; Jesper Lindé; Hou Wang; Pawel Zabczyk; Jianping Zhou (2023), *An Estimated DSGE Model for Integrated Policy Analysis*, IMF WP 23/135. [DOI](https://doi.org/10.5089/9798400245763.001).
- **R8.** IMF (2023), *Integrated Policy Framework—Principles for the Use of Foreign Exchange Intervention*, December 20. [Publication](https://www.imf.org/en/Publications/Policy-Papers/Issues/2023/12/20/Integrated-Policy-Framework-Principles-for-the-Use-of-Foreign-Exchange-Intervention-542881).
- **R9.** Adler, Gustavo; Kyun Suk Chang; Rui Mano; Yuting Shao (2021), *Foreign Exchange Intervention: A Dataset of Public Data and Proxies*, IMF WP 21/47. [DOI](https://doi.org/10.5089/9781513566672.001). [Dataset metadata](https://data.imf.org/en/datasets/IMF.STA%3AWPFXI); metadata also identifies a 2024 journal version, DOI 10.1111/jmcb.13137.
- **R10.** Gopinath, Gita; Emine Boz; Camila Casas; Federico Díez; Pierre-Olivier Gourinchas; Mikkel Plagborg-Møller (2020), *Dominant Currency Paradigm*, AER 110(3), 677–719. [DOI](https://doi.org/10.1257/aer.20171201).
- **R11.** Forbes, Kristin; Ida Hjortsoe; Tsvetelina Nenova (2018), *The Shocks Matter: Improving Our Estimates of Exchange Rate Pass-Through*, NBER WP 24773. [Publication](https://www.nber.org/papers/w24773).
- **R12.** Same authors (2020), *International Evidence on Shock-Dependent Exchange Rate Pass-Through*, NBER WP 27746. [Publication](https://www.nber.org/papers/w27746).
- **R13.** Jeanne, Olivier; Romain Rancière (2006), *The Optimal Level of International Reserves for Emerging Market Countries: Formulas and Applications*, IMF WP 06/229. [DOI](https://doi.org/10.5089/9781451864892.001). Working-paper precursor; the 2026 study cites the 2011 framework. Journal-version bibliographic reconciliation remains open.
- **R14.** IMF (2026), *Reserve Adequacy in Georgia: How Much is Enough?*, Selected Issues Paper 26/051; also Georgia CR 26/134 chapter. [DOI](https://doi.org/10.5089/9798229051323.018.A001); [chapter](https://www.elibrary.imf.org/view/journals/002/2026/134/article-A002-en.xml). Abstract and selected text inspected; full model audit pending.
- **R15.** IMF (2016), *Guidance Note on the Assessment of Reserve Adequacy and Related Considerations*, June. [PDF](https://www.imf.org/external/np/pp/eng/2016/060316.pdf); [ARA April 2026 metadata](https://www.imf.org/external/datamapper/datasets/ARA).
- **R16.** Hofmann, Boris; Hyun Song Shin; Mauricio Villamizar-Villegas (2019, revised 2021), *FX intervention and domestic credit: evidence from high-frequency micro data*, BIS WP 774. [PDF](https://www.bis.org/publ/work774.pdf).
- **R17.** Auclert, Adrien (2019), *Monetary Policy and the Redistribution Channel*, AER 109(6), 2333–2367. [DOI](https://doi.org/10.1257/aer.20160137); [working-paper record](https://www.nber.org/papers/w23451).
- **R18.** Jaravel, Xavier (2021), *Inflation Inequality: Measurement, Causes, and Policy Implications*, Annual Review of Economics. [DOI](https://doi.org/10.1146/annurev-economics-091520-082042).
- **R19.** Jaravel, Xavier (2024), *Distributional Consumer Price Indices*, CEPR DP19802. [Publication](https://cepr.org/publications/dp19802).
- **D1.** Geostat, [Household survey downloads 2009–2025](https://www.geostat.ge/en/modules/categories/128/databases-of-2009-2016-integrated-household-survey-and-2017-households-income-and-expenditure-survey); [2025 archive](https://www.geostat.ge/media/79814/2025.zip).
- **D2.** Geostat, [Household database variable descriptions](https://geostat.ge/media/62847/Description-of-IHS-database-variables---Eng.pdf).
- **D3.** NBG, [Statement on FX intervention instruments and publication](https://nbg.gov.ge/en/media/news/statement-of-the-national-bank-of-geor-26).
- **D4.** NBG, [Statistics](https://nbg.gov.ge/en/page/statistics), [data page](https://nbg.gov.ge/en/statistics/statistics-data).
- **D5.** Geostat, [Detailed CPI downloads](https://www.geostat.ge/en/modules/categories/293/consumer-price-detail-indices).
- **D6.** Geostat, [CPI aggregate/category portal](https://www.geostat.ge/en/modules/categories/26/cpi-inflation).
- **D7.** Geostat, [Price statistics metadata](https://www.geostat.ge/en/modules/categories/537/metadata-price-indices).
- **D8.** NBG, [Foreign exchange auctions](https://nbg.gov.ge/en/page/foreign-exchange-auctions).
- **D9.** NBG, [Foreign exchange rate mechanism](https://nbg.gov.ge/en/page/foreign-exchange-market).
