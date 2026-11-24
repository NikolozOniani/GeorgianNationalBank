# Authoritative research-completion roadmap

**Study:** The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author:** Nikoloz Oniani

**Fixed research question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

**Scope:** One intervention episode, one economic counterfactual, and its consequences.

## Current work order · 24 November 2026

The primary output is a calibrated evaluation of the same episode and no-purchases counterfactual. The [protocol, sections 2 and 6](PROTOCOL.md) defines the conservative, central and aggressive cases and the acceptance criteria. The prior rejection of the R3 candidate stands. The earlier general pause on R7 is lifted for the conditional analysis. R7 depends on the relevant scenario outputs below. R8 follows the synthesis. Causal identification, access to private records and exact reproduction of the IMF optimum are separate claims with their own evidence requirements.

| Order | Work and dependencies | Deliverable and completion criterion |
|---|---|---|
| 1. Compute the new R3 scenarios | Start from the [registered window](R0_REGISTRATION.md), [R1 flows](../reports/r1_2026_11_10/README.md), published impulses and the protocol's parameter grid. Reuse existing series and assumptions with their original qualifications. | One parameter table and one runnable calculation for the monthly observed and three conditional GEL/USD paths, policy rates, inflation and reserve flows. Record common shocks, timing, sales and funding rules before evaluating the episode. Verify the baseline, unit impulses, identical-policy case and resource constraint. Publish a reason for each infeasible case. |
| 2. Apply the historical reserve stresses (R2/R6) | Start alongside R3 from the completed [historical tests](../reports/buffer_validation/README.md). Use [steps 5 and 6 below](#7-reserve-adequacy-from-georgian-funding-shocks) and existing month-end exposures. For episode-attributable differences, use the corresponding R3 balance sheet. | At each month-end identify the binding payment or discretionary sale, usable resources, first shortfall and replacement-cost or break-even threshold. Compare the IMF benchmark on a comparable date and denominator. Separate dollars of coverage from economic value. |
| 3. Transmit the feasible paths into R4 and R5 | Use the [funding accounts](../reports/r4_2026_11_12/README.md) and [corrected household exposures](../reports/r5_2026_11_13/README.md). | Financial carry by funding alternative and partial basket/transfer effects by group for the same scenario and dates. Distinguish accounting transfers, distribution and national costs. Show uncovered spending and valuation gaps in their own units. |
| 4. Integrate at R7 | Join the feasible results above by scenario and horizon. Complete supported channels even if a separate valuation is missing. | One comparison table for the two questions. Show monthly and terminal FX gaps, the cost of the marginal reserve tranche, protection purchased, and assumptions under which the judgment reverses. Cross low/high intervention effects with low/high reserve benefits. Show a break-even threshold where the sign cannot be determined. Reproduce the released numbers from the cited data and parameters. |
| 5. Prepare R8 | Use the completed R7 exhibits and the existing academic outline. | Answer each clause at its supported strength. Include favorable, adverse and negligible effects where the evidence permits. |

**Fixed-rate R3 result, 24 November 2026.** The [monthly paths, chart and endpoint comparisons](../reports/r3_fixed_rate/README.md) complete the direct FX calculation in step 1 at common observed policy rates. Conditional September 2026 quotes are 2.5367, 2.3481 and 2.0169 GEL/USD. The zero-impact case returns 2.6051 observed. Monetary feedback and inflation remain outstanding for the joint scenarios.

**Completion discipline.** A new series, identification design or replication exercise belongs on the critical path only if it would change a stated output or resolve an ambiguity that materially changes the conclusion. Use existing diagnostics once. Keep the rejected model and holdout results as comparisons. Resolve missing quantities with explicit assumptions, thresholds or a narrower conclusion. Do not choose coefficients to match an endpoint already seen.

## Earlier stage decisions and evidence

Sections 1–6 below preserve the original evidence inventories, designs and dated decisions. Their work orders and release restrictions applied to those experiments. The table above and the current protocol govern future work. Section 7 supplies the historical reserve-stress method used in current step 2.

<details>
<summary>November 9–18 roadmap and historical stage decisions</summary>

**Review date:** 9 November 2026. **Reviewed main-branch commit:** `b8f6d0f97ce716336e318d592d80f4f39731c155`.

**Execution update, 10 November 2026:** R0 is complete as a design/access and local-reproduction checkpoint. See the [registration](R0_REGISTRATION.md) and [verification record](../reports/r0_2026_11_10/README.md). Exact program/execution boundaries and G1–G5 remain open; the R0 checkpoint does not certify causal identification or permanent remote access to old raw vintages. The assessment below retains its original review context.

**R1 execution update, 10 November 2026:** the [accounting report](../reports/r1_2026_11_10/README.md) commits the public-data ledger checkpoint, including gross-flow lower bounds, native-frequency reserve/liquidity bridges, additional audited observations and quantified discrepancies. [R1 status](R1_STATUS.md) records D01–D10 progress and remaining records. Full G1 is **partial**, not passed; missing gross executions and complete accounting components still constrain the counterfactual. Three source documents were acquired; no causal estimation or manuscript drafting was performed.

**R3 reopening update, 17 November 2026:** following the author's instruction to revisit R3 before R7, the [registered model experiment](R3_REOPEN_DESIGN_2026_11_16.md) has been [executed and independently checked](../reports/r3_reopen_2026_11_16/README.md). It adds externally calibrated dynamics, estimated Georgian policy feedback, 24 conditional holdout predictions and 199 block resamples. The primary fails the declared robustness gate (149/199 admissible versus 90% required). No preferred path or empirical range is released; G2 remains unsatisfied. **R7 and manuscript drafting are paused.** This supersedes earlier instructions below to proceed directly to R7.

This is the authoritative sequence for completing the research. The [protocol](PROTOCOL.md) continues to govern definitions and admissible claims; this roadmap governs stages, dependencies and acceptance. The [18 data requirements](data_requirements.json), [acquisition status](ACQUISITION_STATUS.md), [source register](SOURCES.md) and [request specification](NBG_REQUEST_SPECIFICATION.md) are subordinate implementation records. Older assessments remain historical evidence, not competing work plans. The [manuscript structure](../manuscript/STRUCTURE.md) remains the eventual presentation outline.

The original 9 November review committed planning documents only. Execution updates above describe subsequent work; the review assessment below retains its original evidence vintage. Future stages are requirements, not claims of completion or authorization to contact data holders.

## 1. Independent assessment

**The repository supports a substantial descriptive and accounting foundation. It does not yet support a numerical answer to either causal prevented appreciation or the episode's net economic welfare.** More observations alone will not solve the identification problem. The main contribution must connect one defensible no-purchases exchange-rate path to incremental reserve accounts and economic incidence; a collection of institutional explanations, expense totals and hypothetical shocks is insufficient.

The review covered the tracked project inventory, active protocol and specifications, current extraction/validation logic and tests, acquisition outputs and qualifications, historical reserve accounts and ARA calculations, model-channel code and readiness audit, household pilot, and the relevance of the archived credit, accountability and Phase 1 material. The locally available pinned Cangul–Abel PDF, including Annex I, was inspected. No claim is made to have independently audited NBG's underlying bank submissions or repeated every raw-data extraction in this planning task.

The offline repository check passed **17 current and 32 retained legacy tests** and verified **120 unchanged archived files**. These tests establish preservation and selected arithmetic/definition checks, not causal identification or journal readiness. The stored acquisition validation has **25 passing and three qualified checks out of 28**, plus other explicitly recorded discrepancies; its qualified-success flag must not be reported as complete source reconciliation.

### Evidence that survives review

The figures below are existing outputs, not estimates made for this roadmap. Source hashes and locators are available through the linked reports and [manifest](../data/source_manifest.json).

| Existing evidence | Supported conclusion | Boundary on interpretation |
|---|---|---|
| [Episode acquisition report](../reports/acquisition_2026_11_09/README.md): 81 monthly intervention observations, January 2020–September 2026 | Net market purchases were USD 2,432.50 million in 2025 and USD 3,370.65 million in January–September 2026; 2025 reconciles to annual reporting | Non-auction gross purchases and gross sales remain unknown. Net purchases cannot define removal of gross purchases. The 56 dated auction observations end in October 2024 and do not supply episode BMatch executions |
| [Monthly panel](../reports/acquisition_2026_11_09/monthly_policy_panel.csv) and [catalogue](../data/derived/episode_2026_11_09/catalogue.json) | Official FX, reserves, rates, selected operations and external-flow context are available; 36 derived tables have recorded definitions and hashes | Official valid-date FX rates are not pre-execution quotes; calendar days are not independent trades; quarterly data are not monthly observations. October 2026 interventions are absent in this vintage |
| [Reserve bridge](../reports/acquisition_2026_11_09/annual_reserve_bridge.csv) | In 2025 gross reserves rose USD 1,710.724 million; BOP reserve transactions were USD 1,207.767 million | The USD 502.957 million difference combines valuation/other-volume/revision effects. Transactions less net market purchases are another unresolved residual, not measured government conversions |
| [Audited interest accounts](../data/derived/episode_2026_11_09/annual_interest_accounts.csv) and [historical findings](../archive/legacy/reports/reserve_foundations/Findings.md) | Historical 2020–2024 categories and 2025 audited observations are available. In 2025 reserve interest was GEL 401.870 million and monetary-operation interest expense GEL 129.331 million | Neither their difference nor total monetary-operation net income measures marginal reserve carry. Average holdings, financing allocation, fees, currency and duration remain necessary |
| [Historical ARA reconstruction](../archive/legacy/reports/reserve_foundations/ara_reconstruction.csv) and [current inputs](../reports/acquisition_2026_11_09/ara_component_inputs.csv) | Published 2022–2023 conventional ARA arithmetic is reproduced. For 2025, IMF's published ratio is 94.8533%, while NBG reports 104.8% | The older reconstruction uses IMF component estimates, not independent national inputs. Residual-maturity debt and adjustment definitions remain missing for the current reconstruction. A ratio discrepancy is not proof of error or reserve inadequacy |
| [Model-channel code](../archive/legacy/src/paper_analysis.py), [readiness assessment](../archive/legacy/reports/reserve_readiness/Assessment_and_Design.md) and [pinned source register](../archive/legacy/reports/paper/sources.json) | Selected derivative, unit and frozen-denominator calculations are reproducible; published equations raise questions worth resolving | The baseline and extended utility optima have not been reproduced. An isolated loss channel, a sign concern or a wording error cannot reject the complete IMF recommendation |
| [2017 household pilot](../archive/legacy/reports/Pilot2017_Methods_and_Results.md) | Validated expenditure identities and weights provide reusable methods; six category mappings cover 40.92% of weighted consumption | 59.08% is unmatched; direct mappings alone cover 24.35%. These are historical partial contributions, not current household inflation, exchange-rate pass-through or welfare |
| [2025 IMF benchmark review](../archive/legacy/reports/NBG_Policy_Dataset_and_IMF_Benchmark.md) | A model-based case for short-run stabilization benefits is documented | Its 2020–2024 no-intervention exercise is neither a causal estimate for 2025–2026 nor the same policy intervention as removing this episode's purchases |

### Required corrections in how the project is interpreted

- **A large purchase amount is not an economic loss.** NBG acquires an asset. Evaluate its return, financing, risks, liquidity service and the market consequences relative to the same alternative path.
- **An appreciated lari is not evidence that purchases had no effect; a stable lari is not evidence that they prevented appreciation.** The unobserved path is the object of research.
- **Reserve adequacy and optimality are different.** ARA reconstruction is a measurement prerequisite, not a welfare model. A desirable target level does not establish that the actual purchase timing or financing was optimal.
- **The IMF criticism is presently narrower than a refutation.** Resolve objective/first-order-condition equivalence, normalization and implementation before describing an independent calculation as a corrected replication. Preserve favorable IMF evidence and plausible insurance benefits.
- **A scenario grid is not an identified bound.** Bounds require justified restrictions; regression uncertainty does not cover arbitrary structural assumptions. Do not impose that purchases weaken GEL as an identifying restriction and then claim to have tested that proposition.
- **Household consequences belong inside this episode's counterfactual.** Reuse relevant archived methods without reviving a separate credit or general inflation study. Existing loan simulations are not estimates of costs caused by reserve purchases.

## 2. Completion architecture and dependencies

Stages are complete only when their acceptance evidence is committed and independently checked. “Blocked” is an acceptable status; it does not silently become “complete with assumptions.” Record whether an output is measured, an accounting identity, empirically identified, structurally conditional, or unmeasured.

| Stage | Purpose and principal deliverable | Dependencies | Current position / protocol gate |
|---|---|---|---|
| R0 | Freeze definitions, review findings, provenance and analysis design | This roadmap and existing protocol | Complete: registered design and open-decision gates; 57-source local audit and isolated-checkout reproduction; independent external reproduction remains R7 |
| R1 | Reconcile episode transactions, stocks, government flows and operating regime | R0; D01–D10 | Public accounting checkpoint committed: 17 tables, rule/timing and discrepancy records; full G1 partial, see R1 status |
| R2 | Reconstruct ARA/usable liquidity and reproduce the IMF benchmark | R0; D13–D15, D18; R1 reserve definitions | [Public component reconstruction and model audit](../reports/r2_2026_11_11/README.md) complete at documented precision. Official component match and target replication remain open |
| R3 | Identify or constrain the no-purchases exchange-rate and balance-sheet paths | R1; D01–D07, D09–D10; registered design | [Reopened model experiment complete](../reports/r3_reopen_2026_11_16/README.md); primary rejected under pre-fit gates. G2 unsatisfied for both a preferred path and an empirical range |
| R4 | Match marginal reserve income, financing and exposures across paths | R1; D08–D12; R3 for the realized counterfactual comparison | [R4 accounting and conditional carry complete](../reports/r4_2026_11_12/README.md). G3 remains unsatisfied for the episode-wide marginal cost |
| R5 | Measure household and sector consequences of that same FX path | R0 exposure design; R3; D17 and the specific incidence inputs below | [R5 household exposures validated for 2024 and 2025](../reports/r5_2026_11_13/README.md). Partial conditional channels only. Episode incidence unresolved |
| R6 | Value marginal reserve insurance/financing services and break-even benefits | R1–R2; D14–D16, D18; R3–R4 paths/costs | [R6 conditional benefit checkpoint](../reports/r6_2026_11_15/README.md): joint liquidity, insurance thresholds and verified bond-pricing test complete. G4 partial; achieved episode benefit and optimum unidentified |
| R7 | Integrate uncertainty, test competing explanations and obtain independent replication | R3–R6, with all claim limits retained | G5 open; paused while R3 remains unresolved; no accepted path currently available |
| R8 | Prepare the academic paper and replication release | R7 acceptance and subsequent writing authorization | Not started; explicitly outside this task |

**Critical path:** R0 → R1 → R3 → R5/R7. R2 and collection of R4 inputs should proceed alongside R1 because model access and balance-sheet definitions can be slow. Exposure validation for R5 can begin before R3, but policy-attributed household results cannot. R6 can produce transparent break-even requirements while causal benefits remain unidentified. No stage should delay usable accounting work solely because model code or transaction data have not arrived.

## 3. Stage specifications

### R0 — Freeze the economic experiment and make the evidence auditable

**Work.** Register the episode start, cutoff, information set and continuation rule from dated policy/execution evidence, not favorable outcomes. The initial proposed window is January 2025 to the last jointly supportable observation; September 2026 is the last acquired intervention month, not necessarily the last fully matched accounting month. Full-year 2026 is a future update, not a completed sample. Preserve 2020–2024 as a pre-period for calibration and diagnostics, not another policy episode to evaluate.

Keep the protocol's single counterfactual: remove discretionary market purchases while retaining the same exogenous shocks and nonpurchase policy **rules**, allowing private flows, expectations, liquidity and policy outcomes to adjust. Register anticipation, initial balance sheets, terminal conditions, horizon, discounting, price base, welfare boundary and numeraire. Costs of reserves still held at the observation cutoff and their terminal asset value cannot simply disappear at that date. Distinguish the protocol's percentage FX gap from the percentage fall in the GEL/USD quote; their denominators differ.

Specify an economic causal diagram/information timeline separating predetermined shocks from policy responses and mediators. Do not mechanically control for realized imports, remittances, rates or capital flows if the counterfactual changes them. Fix sample exclusions, candidate methods, admissible calibration ranges, minimum detectable effects and claim rules before outcome estimation.

**Issues identified at review, now addressed in R0:** the 1 MB download limit was replaced with a bounded ordinary-file acquisition limit, handoff dispositions corrected, both larger outputs made mandatory, and historical source prose labeled by vintage. Raw sources remain outside Git with per-source recovery instructions and rights/access limitations; a supplied-cache extraction check passes. Future remote vintage availability has not been established. Preserve original source pins and lawful access. Do not call output-only tests full source replication.

**Deliverables:** a dated analysis-registration record, coverage/definition concordance, economic channel map, updated access/replication checklist and evidence-to-claim register. The register must carry source, units, date/frequency, formula, classification, uncertainty, dependencies and permitted wording.

**Acceptance:** the treatment, comparison, timing, horizons and accounts are unambiguous; every active source has a recoverable provenance/access route; fresh-environment checks distinguish absent raw evidence from verified evidence; all historical evidence remains intact. R0 does not require pretending that remaining economic unknowns are resolved.

### R1 — Establish what NBG actually did and how the balance sheet changed

**Execution evidence:** [R1 numerical report](../reports/r1_2026_11_10/README.md), [requirement status](R1_STATUS.md), [public-access checks](R1_PUBLIC_ACCESS.md) and [unsent follow-up records](R1_RECORDS_REQUEST.md). The original acceptance conditions below are unchanged.

**Work.** Complete D01–D10 in priority order. Link executed gross purchases and sales by instrument/currency to order, trade, settlement and disclosure times; preserve options/swaps separately. Obtain rule versions, thresholds, caps, overrides and the information available before orders. Match government conversions, debt settlements, private FX flows, quotations and market depth on appropriate clocks. Latest revised vintages can serve retrospective accounting but cannot represent real-time expectations without release evidence.

Reconcile monthly/annual flow totals and build a stock-flow ledger separating market transactions, government transactions, investment income, valuation, other volume changes and revisions. Trace the GEL liquidity counterpart through base money, government deposits, refinancing and absorption operations. Purchases creating settlement balances do not establish a lasting broad-money increase or a unique sterilization bill.

Resolve or quarantine the existing 2023 annual USD 0.55 million discrepancy, auction month-boundary differences, February 2026 bank-FX total anomaly, July 2026 securities-total anomaly and transfer-source differences. These historical or isolated problems should not block unrelated valid observations; exclusions and their consequences must be explicit. Blank reserve-template cells are not zero drains.

**Deliverables:** `episode_transaction_ledger`, `information_timeline`, `reserve_flow_bridge`, `liquidity_counterparts` and a discrepancy register with raw/clean status. Deliver at native frequencies before making a monthly analytical view.

**Acceptance (G1):** totals reconcile to published precision or each residual has a documented, quantified treatment; gross and net, event and publication, and stock and flow are never substituted. Specify treatment uncertainty if gross flows cannot be recovered. Net monthly aggregates alone do not pass the gross-purchases gate. Missing daily information bars a high-frequency design, not the descriptive ledger.

### R2 — Reconstruct reserve need and audit the IMF justification

**Work, measurement.** Reconstruct current realized ARA using original national series and the exact IMF vintage/regime weights: exports of goods and services, the applicable broad-money definition/conversion, residual-maturity short-term external debt and other liabilities without double counting. Reconcile M2 versus M3 terminology, original versus residual maturity, bank-buffer adjustments, GDP normalization, and the 2025 IMF/NBG ratio difference. Never back-solve a denominator from a ratio and label it independent. Preserve 2024–2028 projections in the older archive as projections.

Build an explicitly separate usable-liquidity schedule with asset currency, maturity, liquidity haircut, encumbrance, predetermined/contingent drains and stress access to private-bank buffers. Reconcile common reporting dates and overlapping maturity buckets. Subsequent exchange-rate changes can change the USD value of domestic-money components: calculate consistent denominator paths where needed rather than freezing ARA mechanically.

**Work, model.** Obtain the exact Cangul–Abel model version, equations, full calibration, solver and QIPF inputs/draws, or document precise unsuccessful access. Maintain separate implementations of (i) the reported specification, (ii) necessary interpretations, and (iii) any independently proposed model. Reproduce the reported baseline near 130% ARA and the combined 145–150% recommendation before calling differences a replication critique. Reconcile the printed CRRA objective with later marginal-loss expressions, units, derivative signs, parameter domain and crisis-probability horizon. Check global optima, corners, multiple roots and positive consumption, not just a solver's first-order-condition root.

The archived isolated dollarization calculation is a useful unit test, not the total welfare comparison. The IMF's working-liquidity allowance already acknowledges overlap; test its adjustment rather than accusing it of ignoring overlap. Investigate whether exchange-rate market pressure is temporary disruption or a response to fundamentals; a desirable buffer level does not by itself validate a particular accumulation rule.

**Deliverables:** `ara_vintage_concordance`, independently reconstructed component/ratio tables, usable-liquidity schedules, a parameter provenance table, and a benchmark reproduction report separating replicated results from unresolved inputs.

**Acceptance:** conventional and adjusted ratios reconcile within source precision or remaining definition differences are explicitly unresolved. Published model results match reported precision under disclosed inputs, or are labeled nonreplicated with exact reasons. An independent model can continue if code is unavailable, but must not be presented as recovered IMF code or a proven correction to its numerical results.

### R3 — Estimate or constrain the no-purchases lari path

**Execution result, 17 November 2026:** the [quantitative report](../reports/r3_reopen_2026_11_16/README.md) records a failed conditional-model attempt, not an accepted estimate. Point fits satisfy the limited forecast/stability/reserve checks, but only 74.87% of coefficient resamples are admissible. Similar holdout errors under sharply different direct-effect assumptions do not identify the sign. Preserve all rejected outputs; a subsequent attempt must justify changes in economic closure or evidence before fitting, rather than lower the acceptance threshold after the result.

**Method choice must precede estimation.** The ranking below is conditional on the evidence, not a menu from which to choose the largest effect.

| Route | What would make it credible | What it can deliver / failure rule |
|---|---|---|
| Execution-level event design, IV or local threshold design | Time-stamped gross flows, pre-order prices and expectations; documented assignment variation independent of concurrent FX shocks, adequate support and a defensible exclusion restriction | Local causal price impact if anticipation, manipulation, simultaneous news and weak-instrument tests pass. A price-triggered rule, announcement surprise or reaction-function residual is not automatically exogenous |
| Dynamic structural market/balance-sheet model | Independently justified demand/portfolio elasticities, policy reaction rules, capital-flow and expectations channels, stock-flow consistency and a parameter-identification audit | Conditional episode FX/reserve/liquidity paths. Estimate/calibrate only parsimonious identifiable components; report sensitivity and set-valued results when identification is weak |
| Partial identification | Explicit empirically justified bounds on confounding, gross flows, elasticities and persistence, with a valid mapping to outcomes | An identified set, including an uninformative set if that is what restrictions imply. Arbitrary low/central/high assumptions produce scenarios, not bounds |
| Forecasting or cross-country comparison | Pre-period fit, holdouts, stable regime/measurement and documented donor exposure to their own interventions and common shocks | Diagnostics and robustness. A forecast residual or good synthetic fit alone does not identify the no-purchases outcome |

Do not use contemporaneous FX/purchase regressions, a short unrestricted monthly VAR, summed intraday effects, or unexplained donor currencies as the core causal answer. The existing 2025–2026 monthly sample cannot separately identify a rich reaction function, private FX demand and persistence without strong restrictions.

Model both the flow impact of orders and persistent portfolio/expectations effects; allow anticipation and liquidity offsets. Removing purchases while mechanically retaining observed net sales and refinancing may violate the protocol's policy rules. State the link between local estimates and removal of an entire anticipated purchase program. If event support covers only small trades or a different regime, disclose extrapolation and test its economic magnitude against turnover and market depth.

**Deliverables:** design acceptance/rejection memorandum; no-purchases daily or monthly GEL/USD path at the justified frequency; endpoint, average and persistence measures; corresponding reserve and liquidity paths; parameter/identification uncertainty; validation against external flows and feasible balance sheets. NEER is secondary robustness, not a second treatment.

**Acceptance (G2):** assumptions survive pretrend/anticipation, placebo, concurrent-news, regime-break and weak-identification checks as applicable; out-of-sample diagnostics use genuinely withheld observations; zero, opposite-sign and persistent versus transitory effects remain admissible unless evidence rules them out. Statistical intervals, calibrated ranges and identification sets are labeled separately. If no credible route survives, do not publish a precise prevented-appreciation number. Conditional illustrations may continue but cannot answer the causal clause as fact.

### R4 — Measure the incremental cost of the additional reserve path

**Work.** Use D08–D12 to reconcile interest, fees, gains/valuation and daily/monthly average holdings by currency/instrument/duration. Build observed and no-purchases funding paths: remunerated bank balances, CDs/facilities, IMF/SDR liabilities where relevant, nonremunerated balances and displaced refinancing or other earning assets. Allocate only the marginal differences supported by operations and the policy closure. Domestic policy rates times gross reserves, closing-stock yields and all NBG interest expense are inadmissible shortcuts.

Separate measured annual category income/expense, estimated portfolio returns, conditional financing attribution and national resource costs. Match currencies and risk, or model open currency risk explicitly. Account for reserve duration, gold's lack of interest yield, transaction costs, terminal asset value and discounting. A hypothetical sovereign borrowing spread is not the observed financing cost of GEL-financed purchases. A reserve purchase is an asset exchange, not a loss of the full purchase principal.

**Deliverables:** matched reserve-return and funding ledgers; observed/counterfactual average-balance schedules; incremental financial carry by mechanism and horizon; consolidated-public-sector reconciliation; assumptions and sensitivity table.

**Acceptance (G3):** balance-sheet and accrual totals reconcile; measured amounts are separate from allocated/assumed costs; marginal cost is computed over the same reserve path as R3. If attribution cannot be identified, provide evidence-anchored cost envelopes and show which funding assumptions change the conclusion. Domestic transfers are not counted as national losses without a demonstrated distortion or resource cost.

### R5 — Quantify household consequences without overstating welfare

**Work.** Use the same R3 exchange-rate path, not an arbitrary appreciation selected to produce a striking household gain. Validate the latest usable survey exposure data against published aggregates, with 2024 as a candidate pre-episode baseline and 2025 as a composition sensitivity if semantically validated. Existing release integrity is not household-variable validation. Do not describe independent annual samples as a panel. Preserve the 2017 pilot as a historical methods check; its partial coverage and age bar its use as a representative 2025–2026 welfare estimate.

Prioritize consumption by detailed COICOP category, cash/noncash and own production, household weights/PSUs/strata, income sources and employment sectors, transfers from abroad, and available FX asset/debt currency exposures. Do not silently merge different surveys or assign national bank exposures to individual households. If joint exposures cannot be observed, report group/aggregate incidence or explicitly constrained joint-distribution scenarios.

Estimate or justify import-to-retail exchange-rate pass-through by category and lag using pre-episode price/import data and a defensible design, controlling appropriately for foreign prices, freight, taxes, administered prices and common shocks. A regression of CPI on the exchange rate does not automatically identify the response to NBG purchases. Check appreciation/depreciation asymmetry, currency of invoicing, imported-input content and external validity of any external-shock identification. Conditional external elasticities are permissible if their provenance and uncertainty are explicit. Do not assume full or immediate pass-through.

Translate category price changes into fixed-basket expenditure effects with weights at a common price date. Separately examine FX remittance/income conversion, exporter-linked wages/profits, import-input benefits, debt service and net financial exposures. Appreciation can lower import costs and FX debt burdens while reducing GEL receipts from foreign income; domestic income/employment responses can offset basket gains. Distinguish flow income from stock revaluation and avoid counting debt principal revaluation plus the same principal's repayment saving twice.

**Deliverables:** exposure/crosswalk validation and weighted unmatched shares overall and by group; category pass-through assumptions/results; household-group price and net-income effects conditional on R3; uncertainty decomposition and omitted-channel table. Use quintiles, urban/rural and pension/remittance/sector groups only where validated variables and sample sizes support them.

**Acceptance:** report partial effects when coverage is incomplete. No arbitrary coverage percentage makes full welfare valid: evaluate the size and direction of omitted channels and whether defensible bounds change group rankings or the sign. Fixed-basket effects are not compensating variation; use that welfare label only after specifying preferences, substitution, income and the relevant price paths. Design-based uncertainty requires actual survey design; otherwise disclose approximations. Sampling, pass-through and FX identification uncertainty must all survive into results. Inadequate joint exposure data bars precise population welfare, not clearly labeled channel estimates.

### R6 — Value reserve benefits and test the IMF recommendation economically

**Execution update, 16 November 2026:** [R6 findings](../reports/r6_2026_11_15/README.md) and [replication](../replication/R6.md) implement the conditional branch permitted below. They add two pinned MoF sources, original-issue terms, maturity-matched pricing, single-use liquidity service and cost-equivalent insurance requirements. The R3 paths remain unidentified; no actual marginal episode benefit or optimal target is claimed. The later R3 reopening update above pauses progression to R7, with the G1–G4 limitations retained.

**Work.** On the R3 reserve paths, use R2 usable assets and D14–D18 to quantify stress liquidity by maturity/currency and feasible alternative access to FX. Distinguish reduced crisis probability, lower crisis severity, ordinary market-functioning services and financing costs. A single reserve dollar cannot meet independently summed simultaneous drains. Private-bank buffers count only to the extent they are accessible under the same stress.

Use a long enough and economically comparable evidence base for crisis likelihood/loss; a short Georgian sample cannot estimate rare-event probabilities precisely. Separate externally calibrated hazards from Georgian estimates, specify annual versus multi-year probability and avoid judging an ex-ante decision only by the realized absence of crisis. Compare the information available when purchases were chosen with later realized accounting outcomes.

For spread benefits, use actual issue/refinancing exposures, maturity-matched benchmark yields, fees and a defensible reserve–spread response; not total debt times an unexplained spread change. Test fiscal, global-risk and political-news explanations. Do not add spread savings to crisis-loss benefits if both already enter the same utility/resource constraint. Distinguish the return on a foreign reserve asset from its insurance service.

**Deliverables:** joint liquidity stress tables; marginal-benefit curves/ranges; break-even reductions in crisis probability/severity or financing cost needed to offset R4 and relevant R5 resource effects; replicated-benchmark sensitivities to composition, financing, dollarization, overlap and FX persistence. Show whether the episode's incremental reserves lie on a flat or steep part of the benefit schedule. Any optimal range must use an explicit objective/domain and consistent denominator, not assert that crossing an ARA threshold proves optimality.

**Acceptance (G4):** benefits and costs share horizon, numeraire, policy closure and terminal values; stress assumptions and alternatives are evidence-anchored; overlapping channels are consolidated. A required break-even probability reduction is not an estimated achieved reduction. If the benefit response remains unidentified, report the threshold and which evidence could discriminate, not a manufactured net benefit.

### R7 — Integrate findings, challenge them and verify reproducibility

**Work.** Compare observed versus no-purchases outcomes in separate NBG, consolidated public-sector and national/household accounts. Report distribution alongside aggregates and make any welfare weights explicit. Connect the macro model to measured micro exposures rather than appending household gains to a representative-agent welfare number that already includes them. Reserve carry, remittance conversion, producer margins and asset revaluation cannot be summed without a common resource/ownership account.

Propagate source uncertainty, sampling error, weak identification, model parameters and calibration ambiguity without treating arbitrary scenarios as equally likely draws. Evaluate economically coherent joint parameter combinations; independently taking every worst-case endpoint can generate impossible states. Report sign reversals, economically small differences and uncertainty about persistence as prominently as preferred estimates.

**Deliverables:** a joint results/claim ledger, contribution and novelty matrix, no-double-counting reconciliation, break-even/robustness exhibits, independent replication record and a hostile-review response memorandum. A later focused literature check must distinguish the new episode measurement, counterfactual and incidence contribution from existing work; do not claim novelty merely because code is new.

**Acceptance (G5):** an independent reader can trace every result from original permitted inputs to output; raw access limitations are documented; numerical results survive an independent implementation of central equations; source revisions and exclusions are tested; the best reasonable alternative explanation is confronted. The review must specifically test the cases of fundamental inflows, temporary overshooting, endogenous NBG selection, low marginal funding costs and substantial insurance benefits. Neither a positive nor a negative verdict is required. Unsupported precision and aggregate welfare claims are removed rather than cosmetically qualified.

### R8 — Write only after results determine the claims

Prepare the paper in the existing structure after R7. Keep the fixed title, author and question. Present measured facts, identification, results, economic interpretation and limitations; put software, acquisition instructions and project administration in the replication material. Academic appendices should contain derivations, data definitions and robustness relevant to inference. Do not assemble superseded manuscripts into a new draft.

**Acceptance:** all substantial claims have evidence classifications and reproducible exhibits; abstract and conclusion match the strength of identification; household effects are not equated with total national welfare; the IMF benchmark is represented fairly; a skeptical economics reader can reproduce and challenge the results. These criteria are necessary for a serious paper, not a guarantee of journal acceptance.

## 4. Required original quantitative contributions

| Finding to produce | Status now | Minimum defensible result and what it must not become |
|---|---|---|
| Episode transaction/reserve/liquidity decomposition | Substantial net data; incomplete gross and valuation/government detail | Reconciled measured amounts with residuals and timing uncertainty, not stock growth renamed intervention |
| No-purchases FX path and persistence | Missing | Identified estimate or explicitly conditional structural range; local price impact alone is insufficient for the whole episode |
| Household distribution of purchasing-power consequences | Historical partial pilot only | Same-counterfactual basket and income/exposure effects with coverage and uncertainty; not total welfare from imported-goods prices alone |
| Marginal reserve return/funding account | Annual categories available | Matched incremental carry or an evidence-anchored envelope; not all NBG expenses assigned to reserves |
| Independent ARA and usable-liquidity comparison | Historical conventional arithmetic; current gaps | Vintage-reconciled national-input reconstruction and stress liquidity; neither alone is an optimum |
| Marginal insurance/financing benefit and break-even assessment | Missing; model arithmetic only | Reproduced/independent model with calibrated assumptions and transparent thresholds; no invented causal crisis or spread effect |
| Integrated evaluation of this purchase episode | Missing | Common-path cost/benefit comparison with distribution and sign-changing assumptions; no subtraction of incompatible scenario totals |

The empirical contribution must be economic, not just an inventory or an algebra correction. A credible conditional result can be original; its conditional status must survive the title-to-conclusion narrative. The fixed title does not authorize an optimal-reserve point estimate when the welfare surface is unidentified or flat.

## 5. Missing evidence, priorities and exact next work

Existing D/S/R identifiers below refer to the linked requirements, sources and request specification. “Request candidate” is an access route, not proof of nonpublication or confidentiality. The November 2026 public-evidence amendment supersedes earlier access routes throughout this plan. Request specifications identify missing fields for public-source review. Correspondence and private records are outside the active design.

| Priority / requirement | Remaining variables, frequency and period | Existing source route / access status | First deliverable and decision unlocked |
|---|---|---|---|
| Critical: D01–D04 | Gross executed purchases/sales, currency/price, order/trade/value/disclosure times; rule versions, caps, trigger inputs and exceptions; tick/event or daily, Jan 2025–latest episode observation; usable pre-period | NBG/BMatch/auction records, S01/S05–S07; request candidates R1–R2. Quotes/depth via platform/provider, licensing unresolved | Treatment and identification audit. If only monthly net flows are obtainable, reject execution-level causal claims and quantify treatment ambiguity |
| Critical: D05–D07 | Government conversions and FX cash settlements; private order flow/nonresident deposits; global/news timing, daily/monthly 2025–2026 with comparable pre-period | NBG and MoF S09/S14/S23–S24; public detail investigation plus R3; existing global series S25–S27 | Information-set/competing-flow ledger; identify confounding, mediators and timestamp limits |
| High, begin alongside critical: D08–D12 | Reserve transaction/valuation decomposition; average currency/duration assets and returns; 2025 daily liquidity history, operation remuneration, displaced assets; opening Dec 2024 and episode months/quarters, annual audits | Existing NBG workbooks and audited notes S09–S16 first; R3–R5 for missing aggregates | Reserve/liquidity bridge and matched marginal-cost inputs. Do not reacquire completed 2025 interest categories |
| High: D13–D15 | Realized ARA vectors, residual-maturity debt, other liabilities/bank adjustment, usability/drains; 2024–2026 vintages; exact model/calibration/solver and simulation draws | IMF/NBG S16–S20, R5–R6; model authors/IMF request candidate distinct from NBG | Independent denominator and benchmark replication; resolve whether ratio and model disagreements are substantive |
| High for household claim: D17 incidence supplement | Household detailed expenditure/own-production and income/exposure variables, identifiers/weights/design: 2024 pre-episode and 2025 sensitivity; monthly category CPI/import prices, invoicing and input-output content; preferably 2010–2024 calibration where definitions permit, through observed 2026 for validation | Existing GEOSTAT release and pilot first; Geostat household/CPI/trade/supply-use records; NBG protected exposure aggregates. Survey-variable/design and joint-exposure availability require investigation | Validated crosswalk, missing shares and pass-through design. This is an episode consequence dependency, promoted above optional descriptive extensions |
| High for benefit claim: D14/D16/D18 | Maturity-specific drains and contingent access; actual Eurobond/other issuance fees/yields and daily matched spreads; crisis-loss/hazard evidence and alternative financing terms | Existing R1/debt schedule plus S16/S18–S20/S23–S27; public primary issue terms before licensed prices; some inputs need research/calibration rather than acquisition | Usable liquidity and benefit/break-even calibration with overlap accounting |
| Necessary before release: reproducibility | Stable raw vintage access, source rights, qualified tests and corrected status metadata; all used periods | Existing manifests/code/replication instructions | Independent source-to-result reproduction; no empirical claims upgraded merely because software passes |

**Immediate work order for the next authorized research phase:**

1. Finish R0 registration and a field-level availability decision for gross BMatch/rule/quote inputs using the existing cache first. Assemble precise unsent request packages and record who holds each missing field. Do not postpone the identification decision while collecting low-value extra series.
2. Complete R1's achievable public accounting and extraction from already acquired files, including outstanding depository/Treasury/annual-note detail. Mark request-dependent remainder and release valid measured components.
3. Using the public evidence, finish the national ARA component bridge and IMF replication specification, and validate episode-relevant household exposures. No causal coefficient is required to complete these measurement tasks.
4. Hold a written R3 design gate: select a defensible route or record why none identifies the effect. Only then estimate the policy counterfactual. Build R4/R6 accounts concurrently, without presuming its sign.
5. Feed that same path into R5 and R7; quantify which uncertainty determines the result before expanding methods or adding data. Finish independent checks before R8 writing.

There is no credible fixed calendar deadline for access-dependent records. Track stage completion against evidence, not elapsed time or the number of files downloaded. Each update should state completed artifact, gate status, residual blocker, responsible source/custodian and next action.

## 6. Decision rules for the final research claim

- **G1 only:** publishable-quality episode/accounting evidence can be prepared, but it does not complete the intended causal/welfare paper.
- **G2 conditional, with adequate G3–G4:** an independently reproducible structural assessment is possible. Present the lari and household results as conditional; document how plausible assumptions reverse or preserve conclusions.
- **Credible G2 with incomplete G3/G4:** report exchange-rate and supported distributional effects, but leave the net justification question unresolved. A measured appreciation effect alone does not establish excessive reserve accumulation.
- **G3/G4 available but G2 fails:** original cost and insurance break-even results remain useful, but they cannot establish the exchange-rate/household part of the fixed question. Do not quietly replace the question with a different reserve paper.
- **G1–G5 supported:** answer both clauses at their demonstrated precision, including a finding of benefits, costs, economically negligible effects or an unresolved ranking. Evidence determines the conclusion.

The completion standard is a coherent chain from transactions to a defensible counterfactual to matched economic consequences—not a predetermined indictment, a predetermined defense, or a precise-looking welfare number built from incompatible assumptions.

**R3 interest-rate update, 17 November 2026.** A [standalone forward-looking MPC rule](../reports/r3_rate_rule/README.md) was tested on 16 held-out decisions. Its inflation response changes sign across samples. The revised equation does not qualify for use in the episode counterfactual.

**R3 purchase impact and persistence, 18 November 2026.** The [Georgian evidence test](../reports/r3_fx_response/README.md) extends the cash-auction record to 2009, matches official FX movements, measures monthly associations and quantifies the selection assumption required for the imported elasticity. Neither a causal impact nor an episode half-life passes G2. The [step 2 audit](../reports/r3_fx_response/AUDIT.md) reproduces the estimators, tests quote timing and matching overlap, and reconciles the auction month offsets under next-weekday settlement.

</details>

## 7. Reserve adequacy from Georgian funding shocks

**Plan adopted 19 November 2026.** This work extends R2 and R6 under the existing protocol. Its decision question is how much usable FX Georgia needed at the opening of, and during, the registered purchase episode to meet specified obligations under historically grounded stress. The main output will be a minimum opening buffer in USD by policy objective, a comparison with observed reserves, and a record of what a smaller buffer would have failed to cover. The exchange-rate counterfactual remains under R3. The following steps are prospective.

### 1. Reconstruct Georgia’s largest historical FX funding shocks

Begin with the August 2008 conflict and subsequent financing stress. Screen the accessible history from 2008 through December 2024 for other large episodes, including 2014–15, 2020 and 2022 as candidates. Before ranking, freeze a selection rule using observable financing pressure (external debt rollover, bank FX deposit withdrawals and interruption of external receipts), normalizing each channel by its pre-shock exposure. Record the ranking on each channel, missing coverage, episode boundaries and the rule for merging overlapping windows. Include quiet comparison windows. Reserve sales alone cannot select the stress sample because they depend on the exchange-rate policy. Preserve candidate events that turn out to have limited funding pressure.

Build an episode-by-month ledger in USD from NBG reserve templates, external and banking statistics, Ministry of Finance debt service and disbursements, and contemporary IMF program reviews. Reuse pinned files first. Separate contractual payments, lost rollover, private flows, bank own liquidity, official support committed before stress, emergency assistance subsequently obtained, and discretionary FX sales. Identify the ultimate payer, currency, due date, release date, source cell and any overlaps. Private outflows become a claim on public reserves only under an explicit support policy. Retain quarterly flows at source frequency and bound the unknown timing where possible.

**Deliver and verify:** an episode catalogue, dated cash-flow ledger, financing chronology and residual reconciliation to the observed reserve bridge. Flag exchange-rate valuation separately. An episode can inform the channel history even when its funding gap can only be bounded. Publish which intervals and channels the screen could miss.

### 2. Define what the reserve buffer must protect

Using the step 1 ledger, freeze policy cases before estimating buffers. The primary case covers documented public FX obligations under a floating exchange rate, net of accessible Treasury resources, and any documented binding central-bank commitments. Additional cases specify bank liquidity support after banks use their own eligible FX assets, and discretionary market stabilization with an explicit sales budget. Record whether maintaining a given exchange rate was a historical policy choice. A tape of observed sales can cost a historical defense scenario but cannot establish the required cost of defending the same quote in 2025–26.

Build a companion inventory of cash, securities, gold, SDRs, encumbrances and committed facilities, by currency, holder and time to mobilize. Distinguish gross assets, usable opening assets and later inflows. Specify an operating floor, including a zero-floor comparison, and document any haircut or access restriction.

**Deliver and verify:** a policy-by-obligation matrix and a gross-to-usable reconciliation using the [R2 reserve schedules](../reports/r2_2026_11_11/README.md). Every cash call and funding source must appear only once. Show emergency assistance both on its actual arrival date and in a case excluding uncommitted rescue funding.

### 3. Compute the minimum buffer and identify what binds

For each episode and policy, let D(t) be eligible cash due in month t less accessible nonreserve FX receipts in that month, in USD millions. For a floor F(t), the minimum immediately usable opening balance through horizon H is the maximum of zero and F(t) plus cumulative D through t, taken over t = 0,…,H. The opening cumulative gap is zero. This calculation follows the cash balance month by month, so a late disbursement cannot pay an earlier bill. Compute 1-, 3- and 12-month results separately. Report intra-month timing uncertainty if payment order can alter the peak. Check currency-specific constraints before aggregating; model documented conversion or asset mobilization with its delay and cost.

**Deliver and verify:** balance paths, peak month, binding obligation, minimum buffer and shortfalls for lower opening stocks. Reconcile the formula to a forward cash simulation. Test late receipts, duplicate claims, an unchanged floor and a fully covered shock. Where several obligations bind simultaneously, report the joint gap unless a payment priority is documented.

### 4. Validate the stress model on historical episodes

Separate retrospective reconstruction from forecasting. Use rolling historical origins where vintages permit. Freeze decisions on haircuts, available official credit, rollover, bank support and severity using only information available at each origin. Predict funding gaps and peak timing before exposing the model to the evaluation window. Replaying realized cash flows checks accounting; only forecasts made from the earlier information set test predictive performance. Label hindcasts honestly where the historical outcome was already known.

**Deliver and verify:** one row per eligible holdout showing predicted and reconstructed gap, timing error, uncovered payments, emergency financing and excess buffer. Compare with a simple cash/debt-service rule and the contemporaneously available ARA benchmark on the same obligations, opening resources and horizon. Report both missed shortfalls and the carrying cost of excess buffers. Check how rankings change when 2008 or any other dominant episode is omitted. Set forecast scoring and model-selection rules before fitting. If vintage coverage or holdout count is inadequate, retain historical stress replays and withhold claims of predictive superiority.

### 5. Apply validated shocks to the purchase episode and compare targets

Start at December 2024 and repeat at observed month-ends through September 2026. Scale rollover shocks to current debt maturing, deposit withdrawals to exposed FX deposits, and receipts shocks to the corresponding contemporary flow. Preserve historically observed joint timing; separately label deliberately more severe scenarios. Keep historical shocks, contemporary exposures and assumed policy responses in separate columns. Use information available at each evaluation date and identify any retrospective reconstruction.

**Deliver and verify:** for each date, a common-basis comparison of observed usable resources, the model’s required buffer, conventional ARA and Cangul and Abel’s 145–150% ARA recommendation. Show both R2 domestic-money definitions and translate gross targets into usable resources under the same asset-composition assumptions. For hypothetical reductions in USD 100 million tranches, report the first failure date, obligation and amount, alongside the smallest buffer that passes every designated stress. Repeat with alternative financing access, gold liquidity and policy objectives. Treat the [R1 net purchases](../reports/r1_2026_11_10/README.md) as a flow; attributing usable stock to purchases requires a separate supported bridge.

### 6. Price marginal protection and issue the adequacy verdict

For each tranche, compare the extra shortfall it covers with financial carry under [R4 financing alternatives](../reports/r4_2026_11_12/README.md). Where evidence permits, value its service using the cost and timing of a feasible replacement loan, delayed payment or forced adjustment. Preserve the distinction between dollars of liquidity, fiscal expense and national welfare loss. Report the crisis frequency or severity needed for protection to pay for itself under the [R6 break-even framework](../reports/r6_2026_11_15/README.md). Avoid assigning an annual crisis probability from a sample selected for severe shocks.

**Final deliverable:** a reproducible table and short decision memo stating the required usable USD amount or interval, as-of date, horizon, policy objective, binding shock, observed usable amount and difference. If even the upper plausible usable stock falls below the lower required buffer, classify a shortfall. If the lower usable stock covers the upper required buffer, classify coverage and quantify the margin. Overlap leaves the ranking unresolved. Apply these rules within each scenario before comparing across scenarios. State the unobserved shock or financing failure that would overturn a finding of coverage. An excess over the tested liquidity requirement establishes an economic surplus only if the marginal carrying cost also exceeds defensibly valued additional services. Report an optimum only if those costs, services and risk weights can be supported.

**Completion order:** steps 1–3 produce an auditable historical requirement. Step 4 sets the strength of the claims step 5 can make for the registered episode. Step 6 delivers the reserve-adequacy judgment even if the economic optimum remains unidentified. Preserve the public-source restriction, machine-readable inputs and assumptions, checksums, tests and independently reproducible outputs throughout.

**Step 1 checkpoint, 19 November 2026.** The [historical screen and 2008 reconstruction](../reports/historical_fx_shocks/README.md) cover three funding-pressure indicators over 68 quarters and distinguish policy sales, emergency financing and reserve-stock changes. Detailed public cash obligations and subsequent episode ledgers remain open.

**Step 1 case extension.** [2009H1 and 2020 ledgers](../reports/historical_fx_shocks/cases/README.md) now distinguish actual IMF principal payments, bank repayments, imports offsetting export losses and policy sales across venues. Public due-date coverage remains partial.

**Step 1 payment-calendar checkpoint.** The [2009Q1 and 2020Q2 payment calendars](../reports/historical_fx_shocks/payment_calendar/README.md) reconcile scheduled IMF principal to dated repayments, separate committed financing from cash arrivals, and compare the 2020 opening maturity schedule with realized service. Proceed to step 2 policy definitions. Treasury cash access and incomplete settlement dates still prevent identification of the peak unavoidable public reserve draw.

**Step 2 policy freeze, 20 November 2026.** The [payment eligibility rules, funding cases and gross-to-usable reconciliation](../reports/reserve_buffer_policy/README.md) distinguish a funded Treasury bill from an external reserve delivery. Step 3 may proceed with conditional, currency-matched public-payment paths and separate sales budgets. Retain unresolved timing, encumbrances and bank-level eligibility explicitly.

**Step 3, 22 November 2026.** The [historical minimum-buffer calculations](../reports/minimum_reserve_buffer/README.md) identify binding payments, alternative funding routes, timing sensitivity and shortfalls at smaller openings. The 2020 twelve-month scheduled-drain and market-sales cases have full horizon coverage. Other cases carry their own currency and coverage restrictions. Proceed to step 4 historical validation with preregistered holdout rules; a nationwide optimal reserve stock remains unresolved.

**Step 4, 22 November 2026.** The [frozen holdout design](HISTORICAL_BUFFER_VALIDATION.md) preceded [seven historical-origin tests](../reports/buffer_validation/README.md). The cash-path and gross-service rules tied. Dated public contract terms passed a sovereign maturity check, retrospective IMF schedules reconciled to gross principal, and matched national reserve-draw outturns remained unidentified. Proceed to step 5 as a conditional exposure and stress comparison; predictive superiority and a national optimum remain unsupported.
