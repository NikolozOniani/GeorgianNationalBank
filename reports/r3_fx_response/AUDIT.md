# Independent audit of R3 step 2

**Decision, 18 November 2026.** The historical auction and monthly calculations reproduce. They are sufficient to document how GEL/USD moved around purchases and why the price effect remains unidentified. They do not supply a Georgian purchase elasticity, a half-life or a defensible range for the January 2025–September 2026 exchange rate without NBG purchases. Both a material effect and a negligible effect remain compatible with the records. [Audited commit](https://github.com/NikolozOniani/GeorgianNationalBank/commit/fb62e1e0050ec76f6ec0fac5d2dcb53aeabdf5c2) · [Registered design](../../research/R3_FX_RESPONSE_DESIGN.md)

## What reproduced

- The three cached NBG workbooks passed their original SHA-256 checks and regenerated the four historical extracts byte for byte. The annual sheets independently agree with the consolidated sheet for all 6,210 calendar-day GEL/USD quotes. This is internal workbook consistency. Carried quotes add dates without adding transactions. [Source manifest](../../data/source_manifest.json)
- An independent enumeration reproduced the chosen control or absence of one for all 636 purchase–horizon combinations, including the nearest-date tiebreaker. All 24 auction summary rows reproduced. Positive differences denote greater depreciation or less appreciation than the comparison date. [Pair records](auction_pairs.csv) · [Summary](auction_comparison.csv)
- Independent partial regressions reproduced both directional coefficients, both Bartlett HAC standard errors and the omitted-factor tipping points for all 28 monthly specifications and horizons. The kernel diagnostics reproduced in the original 57 pre-episode months. With the published persistence and lag coefficients fixed, a current impact of zero implies a partial flow–shock correlation of −0.2433. This calculation conditions on the contemporaneous policy rate and imposes persistence. Neither the shock nor the persistence of a Georgian purchase is independently observed. [Monthly fits](monthly_projections.csv) · [Kernel comparisons](kernel_diagnostics.csv) · [External calibration, Table A11](https://www.imf.org/external/pubs/ft/wp/2015/wp15130.pdf)

## What changes the interpretation

**The auction clock matters.** The published NBG convention fixes the business-day USD quote using trades through 16:30 and makes it effective the next day. The original exclusion includes other auctions on the valid date of the endpoint quote. Under this convention such a trade occurs after the quote was formed. We preserved that calendar calculation and tested excluding only other auction dates strictly between the start and end. This alternative cannot resolve intraday timing, holiday carries, advance announcements or historical changes in the fixing. [NBG quote methodology](https://nbg.gov.ge/en/page/foreign-exchange-market) · [NBG description of the original 2009 fixing](https://nbg.gov.ge/en/media/news/the-national-bank-of-georgia-launched-a-new-monetary-policy-instrument-the-currency-auct)

| Seven-day comparison | Pairs | Mean purchase minus comparison return, log percentage points |
|---|---:|---:|
| Original matched sample | 155 | +0.160 |
| Original sample excluding later listed auctions through the valid-date endpoint | 26 | −0.128 |
| Same matches, excluding later listed auctions strictly before the endpoint | 39 | −0.024 |
| Rematch with the comparison return completed by the start of the event's 28-day pretrend, before auction exclusions | 150 | +0.078 |

**The comparison outcome can enter match selection.** In 68 of the 155 original seven-day pairs the comparison return overlaps the event's 28-day matching window. The final row removes shared return increments by changing eligibility before choosing the best match. That change can also alter the sample. At 84 days every original comparison has overlap and the registered 91-day lookback allows zero disjoint pairs. The reported day −28 to −7 placebo is the difference between the two matching returns, so agreement on it supplies no independent pretrend test. None of these post hoc checks selects a preferred effect. [Diagnostics at all four horizons](audit_diagnostics.json)

**Three monthly discrepancies reconcile under the settlement convention.** Moving auction amounts from trade date to the following weekday moves a USD 10m purchase on 28 September 2018, a USD 60m sale on 30 September 2021 and a USD 32.305m sale on 31 August 2022 into the next month. On that assignment, both directional totals agree with the bank workbook in all 110 months. This extends the earlier R1 timing observation. The calculation uses weekdays as a proxy for business days. It establishes month-level consistency and leaves individual value dates unverified. Both the trade-month and bank-workbook specifications remain available. [Six original differences](auction_reconciliation.csv) · [R1 reconciliation](../r1_2026_11_10/README.md) · [NBG settlement convention](https://nbg.gov.ge/en/page/foreign-exchange-auctions)

**Some execution-price information is public.** NBG auction-result notices confirm all four post-2019 historical purchases and publish weighted bid rates. The workbook gives amounts and dates. The notices add the following prices, in GEL per USD.

| 2022 auction | USD million purchased | Weighted bid rate | NBG result |
|---|---:|---:|---|
| 24 May | 10 | 2.8689 | [24 May](https://nbg.gov.ge/en/media/news/the-result-of-the-foreign-exchange-auct-27) |
| 1 August | 10 | 2.7514 | [1 August](https://nbg.gov.ge/en/media/news/the-result-of-the-foreign-exchange-auct-28) |
| 5 August | 20 | 2.7186 | [5 August](https://nbg.gov.ge/en/media/news/the-result-of-the-foreign-exchange-auct-29) |
| 10 August | 40 | 2.7096 | [10 August](https://nbg.gov.ge/en/media/news/the-result-of-the-foreign-exchange-auct-30) |

These are prices conditional on an auction taking place. They do not recover the market price in its absence. For the separate 2019 option instrument, the NBG annual report's USD 51.3m purchased agrees at reported precision with the workbook's USD 51.322m. The right to exercise and the official pricing rule are public. The verified records give no daily first stage linking threshold eligibility to executed volumes. [NBG 2019 Annual Report, section 2.3](https://nbg.gov.ge/fm/პუბლიკაციები/ანგარიშები/წლიური_ანგარიში/2019/annual-report-eng-7cea657a.pdf?v=8ca4x) · [Option terms](https://nbg.gov.ge/en/media/news/the-nbg-will-use-a-new-instrument-fx-options-to-replenish-the-international-reserves)

**One apparent signal survives its influence check.** The 18-month association in the recent specification with dollar and VIX controls remains positive when each origin year is omitted in turn. It ranges from +2.24 to +4.81 log percentage points per USD 100m across those refits, versus +4.26 across all 41 origins. The full-history estimate is −2.16. The deletions keep the original calendar for lagged variables and outcomes. A return can cross an omitted origin year. The range measures influence on the fitted association and has no counterfactual coverage interpretation. Eight of the 21 episode months exceed the historical maximum nominal monthly net purchase of USD 322.40m. [Influence and size diagnostics](audit_diagnostics.json)

## Sufficiency for the episode

Monthly net flows can arise from different combinations of gross purchases and sales. A policy of eliminating purchases while allowing sales therefore has an ambiguous treatment size. Purchases can also respond to the same private dollar inflows that appreciate the lari. Controlling for the broad dollar and VIX leaves that local pressure unmeasured. A historical discretionary cash-auction comparison supplies no verified response to repeated BMatch purchases at episode scale. [R1 gross-flow bounds](../r1_2026_11_10/README.md) · [Research decision](README.md)

To reopen the price estimate, the study needs a public source of variation in executed purchases independent of contemporaneous private pressure, or independently justified bounds on that pressure and on gross flows. A candidate rule requires a documented rule vintage, dated realizations on both sides of its threshold, a measurable jump in executed volumes and evidence against other simultaneous price determinants. Either route also requires evidence on persistence and relevance to the episode. Without those conditions the data cannot narrow the no-purchases path to a defensible interval. The 1.8503 GEL/USD scenario retains its rejected status.

## Verification

The original two check commands used Python assertions for output integrity. Under optimized Python those comparisons could disappear. They now raise explicit exceptions on discrepancies. A regression test corrupts a temporary output and requires the optimized checker to fail. The audit supplement uses independent matching, scalar QR partial regressions and a moving-sum implementation of Bartlett variance. The numerical audit reads the pinned data and compares results to the committed diagnostics. Run from the project root with the recorded NumPy and openpyxl versions. [Independent audit code](../../replication/audit_r3_fx_response.py) · [Source checks and acquisition instructions](README.md#reproduce-the-tables)

```sh
python src/r3_fx_inputs.py --check
python src/r3_fx_response.py --check
python replication/audit_r3_fx_response.py
python -m unittest discover -s tests -p test_r3_fx_response.py -v
python replication/check_repository.py --replicate
```

Verification on the audit checkout passed 64 current tests and 32 archive tests. Replication reproduced the numerical content of all 41 checked archive outputs. Two archive CSVs differed only in line endings.
