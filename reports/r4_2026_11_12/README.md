# What can the reserve purchases be shown to have cost?

**R4 decision, 12 November 2026.** The annual accounts identify the income NBG earned on its entire reserve portfolio and the expenses it incurred across monetary operations. Public auction records also identify the contractual cost of its certificates of deposit (CDs) through September 2026. The share caused by FX purchases remains unknown. R3 could not establish the no-purchases reserve or funding path. G3 therefore permits measured components and conditional costs, but no episode-wide marginal cost or national welfare total.

## Interest, fees and valuation

| NBG accrual, GEL million | 2024 | 2025 | Change |
|---|---:|---:|---:|
| Reserve interest | 439.181 | 401.870 | −37.311 |
| Interest on loans to financial institutions | 334.180 | 536.318 | +202.138 |
| Interest expense on amounts due to resident financial institutions | 90.237 | 124.559 | +34.322 |
| CD interest expense | 5.124 | 4.772 | −0.352 |
| IMF interest expense | 101.102 | 73.248 | −27.854 |
| Net interest income, entire NBG | 755.933 | 871.763 | +115.830 |

The decline in reserve interest came principally from securities measured at fair value through other comprehensive income (−26.945 million). Reserve-management revenue reported separately on p. 48 was GEL 421.9 million, about 20.0 million above audited reserve interest. NBG cites bond capital gains. The narrative does not allocate the difference by instrument. Note 4 records GEL 1.776 million in external-manager fees, 1.386 million for custody and settlement, and 0.170 million in cash-operation fees in 2025. The three reconcile to 3.332 million. Applying these entire fee pools to new purchases would require marginal pricing and a custody allocation. FX revaluation of +879.333 million includes the +1,019.691 million gold revaluation. Counting both as separate profits would duplicate the gold gain. Gold pays no contractual interest. [Annual income bridge](annual_accounts.csv) · [Audited note observations](../../research/r4_notes.csv) · [Source and PDF hash](../r1_2026_11_10/sources.json)

## Financing reconstructed from individual operations

For each CD the settlement price is the cash NBG received, face value is the repayment, and maturity fixes the accrual period. We accrue each issue's discount at its constant effective rate between those dates. The 2025 money raised, GEL 255.194606 million, and interest, GEL 4.772389 million, both round to their audited counterparts. Contractual redemptions of GEL 260.000 million compare with 260.001 million in the two rounded audited cash outflow lines. The reconstructed closing carrying amount exceeds the audited balance by **GEL 0.011041 million**. Moving the cutoff back one accrual day gives 59.348117 million versus audited 59.350 million. Accrual timing and rounding are possible explanations. The small balance discrepancy remains open. This reconciliation supports using the contract schedule for expense measurement. It cannot establish what prompted each issue. [CD reconciliation](cd_reconciliation.csv)

| Contract-based measure | Full 2025 | Jan–Sep 2026 | Sep 2026 alone |
|---|---:|---:|---:|
| Daily average CD face outstanding, GEL million | 64.93 | 113.05 | 460.57 |
| CD effective interest over the stated period, GEL million | 4.772 | 6.748 | 3.080 |
| Daily average principal of listed refinancing loans, GEL million | 4,294.76 | 1,366.32 | 340.83 |

**September alone accounts for 45.7% of the reconstructed January–September 2026 CD interest.** A new mix of short issues and larger allocations from late August lifted the amount outstanding. Roughly opposite movements in refinancing and CD balances illustrate two distinct margins: the banking system can borrow less from NBG and it can hold more NBG paper. Neither observed change identifies what would have occurred without purchases. The GEL 6.748 million is contractual accrual on listed issues, pending reconciliation to full-year 2026 accounts. [Monthly schedules](monthly_exposures.csv)

The schedule counts calendar days from issue inclusive to maturity exclusive and includes contracts already outstanding at the opening. The refinancing series counts principal alone. No listed loan spans 14–20 May 2026. Those seven days contribute zero **listed principal**, with total facility usage unresolved. The remaining stock fields use means of adjacent month-end observations. For example, the day-weighted mean of these reserve-stock proxies was USD 4,932.96 million in 2025 and USD 6,970.30 million in January–September 2026. These approximate exposures include gold. They do not support dividing interest by that total to obtain an investable USD yield. Daily positions for all remunerated accounts, their rates by currency and matched incremental acquisition lots are still missing. Counterfactual average balances remain blank.

## What changes the sign of carry?

Consider a hypothetical USD 100 million cash-equivalent position for one year starting at the end-2025 official quote of 2.6951 GEL/USD. Assume it earns the 31 December 2025 USD SOFR fixing of 3.87% for one year, as a simple annual return. SOFR is a secured overnight market benchmark. The reserve portfolio has different instruments and durations. Maintain each quoted GEL funding or displaced-loan rate for the year. The last 2025 CD auction rate was 8.09%. Audited year-end rates were 8% on GEL obligatory reserves and 8.00–8.05% on refinancing exposures to the three banks described in note 9. Rollovers at the same rate and availability of the full amount are scenario assumptions. This standardized comparison does not describe the timing or composition of actual purchases. [Rate observations and source register](../../data/source_manifest.json) · [SOFR definition](https://www.newyorkfed.org/markets/reference-rates/sofr)

| Marginal counterpart assumed for the whole position | One-year net carry at unchanged FX, GEL million | GEL/USD quote change that breaks even |
|---|---:|---:|
| Non-interest-bearing GEL balances | +10.430 | −3.73% |
| Remunerated GEL balances at 8% | −11.131 | +3.98% |
| Foregone refinancing income at 8.00–8.05% | −11.131 to −11.266 | +3.98% to +4.02% |
| Rolling CDs at 8.09% | −11.373 | +4.06% |

With unchanged FX and a mixture of unremunerated balances and CDs, carry changes sign when the CD-financed share reaches **47.8%** (= 3.87/8.09). The actual share is unidentified. Displaced refinancing is foregone income and must not also be charged as CD interest on the same principal. Actual FX reserve requirements carry separate USD/EUR rates (3.25%/1.5% at end-2025, note 19). IMF/SDR obligations also have their own currency, interest and principal schedules. The ledger contains no evidence that new IMF borrowing financed these purchases.

For opening GEL value V, USD return u, funding rate f and terminal proportional change x in GEL/USD, terminal net gain is V × [(1+u)(1+x) − (1+f)]. This includes the value of principal on both sides. At the CD rate, assumed −5% and +5% quote changes give **−25.370 and +2.624 million GEL**. Those exchange-rate shocks are sensitivity choices. Fixed charges, credit losses, insurance services and inflation are excluded. These are nominal one-year terminal amounts. No five-year present value in December 2024 purchasing power is identified. A common positive discount factor preserves the one-year sign but cannot resolve missing continuation values. [All 15 assumptions and outcomes](conditional_carry.csv)

Duration also matters. In the 2025 annual report's pp. 290–291 stress tables, a one-percentage-point rise in market yields reduces the USD investment tranche's equity value by USD 29.267 million and the USD liquidity tranche's by USD 12.494 million. The corresponding falls in yields raise them by 30.169 and 12.852 million. These are whole-tranche repricing sensitivities at year-end. Adding them to historical interest as realized losses or allocating them proportionally to new purchases would require evidence on security holdings, trades and duration at purchase. The p. 292 currency table gives net FX assets of GEL 8,154.955 million at end-2025, up from 3,348.369 million at end-2024. Currency exposures include both assets and obligations.

## Treasury consolidation and the limit on national costs

NBG recorded GEL 137.465 million of interest income from the Georgian government in 2025. That flow cancels against the counterpart Treasury expense on consolidation, subject to matching Treasury recognition dates. At year-end, eliminate GEL 1,496.259 million in government securities held by NBG against the Treasury obligation, GEL 2,073.057 million of Treasury deposits against its claims on NBG, and GEL 571.507 million of declared profit payable against the Treasury receivable. The GEL 670.146 million paid during 2025 settled the opening payable. Counting both the distribution and the same year's NBG earnings as new national income would double count. Securities should be matched by instrument and valuation basis in any full Treasury balance sheet. These are NBG-side eliminations with the counterpart identified. A complete independently matched Treasury ledger is outstanding. [Consolidation entries for both years](public_sector_eliminations.csv)

Interest paid to resident private banks remains a public-sector expense and is also recipients' income. Its national resource cost requires evidence on ownership, taxation, distortions and alternative uses. External reserve earnings and IMF payments cross a different boundary. Neither a sovereign borrowing spread nor the total increase in reserve principal measures the episode's cost. A causal aggregate needs an identified incremental reserve path, the corresponding financing mix, currency and duration, matched accruals and terminal valuations. R4 supplies separately testable accounts until those conditions hold.

**Replication.** Run `python src/r4_carry.py --check` from the repository root. Add `--verify-pdf` with the pinned 2025 annual report and Poppler installed to recheck the supplemental note extracts. Run `python replication/check_repository.py` for the wider suite. The [validation record](validation.json) provides input and output hashes. R1–R3 vintages and the registered evaluation window are preserved.
