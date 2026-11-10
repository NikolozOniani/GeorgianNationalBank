# R1: episode transactions and balance-sheet accounting

**Checkpoint:** 10 November 2026. **Parent:** `92f05d27ab980c2f471e9ca24ab64c2884283860`.

**Status: public-data accounting work completed for this checkpoint; R1/G1 remains partial.** The registered January 2025–September 2026 window is unchanged. No execution-level treatment, prevented-appreciation estimate or marginal reserve-cost estimate has been produced. The findings below are measurements and accounting calculations, not causal effects.

## 1. Net purchases are measured; gross purchases remain unidentified

The monthly source supports the following [totals](episode_totals.csv), in **USD million**:

| Period | Net market purchases | Lower bound on gross purchases | Lower bound on gross sales |
|---|---:|---:|---:|
| 2025 | 2,432.50 | 2,432.50 | 0.00 |
| January–September 2026 | 3,370.65 | 3,386.85 | 16.20 |
| Registered window | 5,803.15 | 5,819.35 | 16.20 |

Source: NBG `fx_market`, sheet/row references in the [transaction ledger](episode_transaction_ledger.csv), original URL and SHA-256 in [sources.json](sources.json). The 2025 net total reconciles to the annual report, PDF p47, and the dated February 2026 disclosure. The ledger contains **105 monthly instrument-field records, not 105 intervention events**. It preserves auctions, non-auction net purchases, options and swaps separately. Actual order, execution, settlement, first-disclosure dates and execution prices remain null when unobserved.

For non-auction activity, let purchases be P, sales S and disclosed net purchases N. From P − S = N and nonnegative gross flows, P ≥ max(N, 0) and S ≥ max(−N, 0). Add separately observed auction gross flows and sum the monthly lower bounds. March 2026's net sale of USD 16.20 million explains why the gross-purchase lower bound exceeds cumulative net purchases. Equal additional purchases and sales can leave N unchanged, so **neither gross direction has a finite upper bound from these observations alone**. These are accounting bounds, not bounds on causal price effects. Net-zero January–February 2025 does not prove no gross trading.

The 2025 annual report places the reported accumulation phase from March through December; the August 25, 2025 release reports the earlier monthly net purchases. Neither establishes the first execution day or the complete governing rule. The registered start remains an administrative boundary, not an invented first trade.

## 2. A more informative, still incomplete 2025 reserve bridge

The [annual bridge](annual_2025_refined_bridge.csv) retains full source precision; this table rounds **USD million** for exposition:

| Component | Amount | Evidence and interpretation |
|---|---:|---|
| Change in statistical reserve stock | +1,710.724 | December 2025 less December 2024, `reserve_assets` |
| BOP reserve-asset transactions | +1,207.767 | `bop_bpm6`, annual 2025 row 39 |
| Net market purchases | +2,432.500 | Monthly `fx_market`, annual-report reconciliation |
| Government foreign loans/grants deposited at NBG | approximately +329.3 | Annual report p48; narrative, not a matched conversion ledger |
| Government debt service and other FX expenditure | approximately −1,600 | Annual report p48; limited reported precision |
| Remaining transactions after the preceding market/government entries | approximately +46 | Conditional arithmetic residual; income, omitted flows, coverage and revisions unresolved |
| Stock change less BOP transactions | +502.957 | Composite of valuation, other volume changes and revisions; not intervention |

The approximate transaction residual is 1,207.766951 − 2,432.50 − 329.3 + 1,600. Its displayed computational digits are not economic precision. The annual narrative does not demonstrate complete coverage or exact alignment with the BOP definition. Therefore this is a **conditional reconciliation using approximate government entries**, not a measured reserve-income flow or a fully balanced source account. There is no source-supported statistical confidence interval for the approximation.

The audited gold note (annual report PDF p262, note 8) provides unchanged reported year-end holdings of **229,478 troy ounces** in 2024 and 2025 and USD prices of **2,610.85** and **4,367.80** per ounce. Audited USD holding values rise from **599.133 million** to **1,002.314 million**, a **403.181 million** increase. Holding the reported quantity fixed, quantity times the price difference gives USD 403.181372 million, consistent within table rounding. This is an endpoint price bridge: unchanged endpoints do not prove an absence of intrayear transactions.

The [gold concordance](gold_source_concordance.csv) finds a material source mismatch: the statistical end-2024 value is **USD 598.731050 million**, about **USD 0.401950 million below** the audited value. End-2025 values agree within rounding. Both versions are preserved. The statistical gold component rises USD 403.582959 million; subtracting it from the total nontransaction residual leaves USD 99.374132 million. This remainder is conditional on treating that component change as valuation, which is not yet established. Using audited gold instead leaves USD 99.776090 million but mixes definitions. **Neither number is a verified estimate of other currency valuation.** The audited GEL 1,019.691 million unrealized gold gain is also retained in its original currency; it is not substituted into the USD flow account.

The [quarterly bridge](reserve_flow_bridge.csv) covers six observed quarters, 2025Q1–2026Q2, at the BOP's native frequency. The [monthly bridge](monthly_reserve_bridge.csv) covers 21 months but leaves monthly BOP, government and valuation entries blank. No quarterly flow is spread over months and no missing flow is set to zero.

## 3. Liquidity counterparts: assets, liabilities and reduced refinancing

New extraction of the existing central-bank workbook produces **22 month-end observations** including December 2024's opening balance. Selected [levels](liquidity_counterparts.csv), **GEL million**:

| Position | Dec 2024 | Dec 2025 | Sep 2026 |
|---|---:|---:|---:|
| Monetary base | 13,700.179 | 15,058.963 | 14,151.726 |
| Net foreign assets | 10,172.601 | 14,431.555 | 19,293.701 |
| Claims on banks | 7,006.097 | 6,170.561 | 290.410 |
| Refinancing loans | 4,456.310 | 4,160.913 | 250.400 |
| One-month operations | 752.305 | 2,006.165 | 0.000 |
| Overnight loans | 1,794.962 | 0.000 | 40.010 |
| Government deposits | 1,448.253 | 2,090.210 | 1,030.832 |
| FX required reserves, GEL equivalent | 6,369.707 | 5,863.318 | 4,729.703 |
| GEL bank correspondent accounts | 436.629 | 914.501 | 1,708.551 |

Source: `central_bank`, CBS and Positions sheets; [cell-level extraction](central_bank_positions.csv). The complete signed identity is monetary base = net foreign assets + claims on banks + net claims on government + other claims − nonbase liabilities − equity − other items net. The [monthly changes](liquidity_changes.csv) retain all these components and rounding residuals.

These balances show why a one-for-one claim that purchases permanently increased money in circulation is unsupported. Bank claims fell substantially while foreign assets rose; government deposits, equity and other counterparts also changed. **The identity does not establish that purchases caused the decline in refinancing.** It includes FX revaluation and accruals; the reported monetary base itself includes FX required reserves converted to GEL. Stock changes are not transaction financing allocations or measured marginal sterilization costs.

The [audited NBG debt-security bridge](cd_financing_reconciliation.csv), annual report PDF p275, separately reconciles opening stock, issuance, redemptions, interest paid and accrued interest. For 2025: 59.384 − 4.245 + 255.195 − 255.756 + 4.772 = **59.350 GEL million**. The GEL 4.772 million accrual relates to this liability category; it is not total monetary-operation expense or the reserve episode's financing bill. The 2024 comparative also reconciles exactly at published precision.

The [depository survey](depository_survey.csv) adds 770 cell-level observations across 22 months; source notes record a September 2022 sector reclassification and inclusion of microbanks from January 2025. A population change must not be interpreted as a private capital flow. The [Treasury table](treasury_operations.csv) adds 126 native records within the registered window. It retains **value dates**, distinguishes bill discount rates from note yields, and separates primary purchases, noncompetitive allocations and switch issuance where reported. These are government financing records, not NBG sterilization; blank supplementary fields remain blank.

## 4. Timing, rules and discrepancies

The [information timeline](information_timeline.csv) distinguishes reference periods, observed article dates, operational descriptions and the retrieval vintage. Historical official documents establish a qualitative BMatch trigger and auction timing conventions, but **do not provide a confirmed 2025–2026 numerical rule, caps or exceptions**. The option exercise rule is a different instrument and is not assigned to BMatch. Official valid-date exchange rates are not pre-intervention quotes. See the [rule register](rule_and_definition_register.csv).

The [discrepancy register](discrepancy_register.json) carries forward the 2023 annual USD 0.55 million difference, four historical auction month-boundary differences, February 2026 bank-FX total anomaly, July 2026 security-total anomaly and transfer-source differences. A documented next-business-day auction settlement convention is consistent with the month-boundary pattern, but actual settlement dates remain unverified and no records are reassigned. The newly detected end-2024 gold difference is added. Quarantined totals are not silently replaced with reconstructed values. These qualifications do not invalidate unrelated reconciled observations.

## 5. Verification and next dependency

The [catalogue](catalogue.json) describes and hashes **17 CSV outputs**. [Input locks](inputs.lock.json) and [source records](sources.json) preserve URLs, retrieved-file hashes and source locations. Three additional official documents were acquired into a separate vintage; older sources and outputs were reused. [Replication instructions](../../replication/R1.md) distinguish source extraction from output-only checks. [Computational validation](validation.json) passes **124 checks** while explicitly retaining source qualifications and an open G1. The [repository check](repository_validation.json) records 26 current and 32 legacy tests, with all 120 archived files preserved.

**Remaining dependency:** obtain gross executed BMatch directions, actual rule versions and pre-order information, a matched government/reserve-flow bridge, and the missing daily liquidity/market observations. The [requirement status](../../research/R1_STATUS.md), [public-access log](../../research/R1_PUBLIC_ACCESS.md) and [specific records follow-up](../../research/R1_RECORDS_REQUEST.md) identify what each gap prevents. No correspondence was sent. A gross-purchase counterfactual cannot yet be recovered from the net series; an exchange-rate effect or welfare number would exceed the present evidence.
