# Historical validation of Georgia’s reserve-buffer calculation

**Decision, 22 November 2026.** The cash-path rule reproduced documented contractual bills. It did **not** improve on holding the gross scheduled debt service in the registered holdouts. No selected origin had a verified future receipt that met all three forecast conditions: approval, eligibility for the payer and a cash date documented before the cutoff. With nonnegative scheduled bills and no admissible credits, the two rules give the same recommendation mathematically. The national minimum still cannot be scored against an observed reserve draw. Proceed to Step 5 for conditional stress comparisons only. The result supplies no validated national reserve target and no evidence of superiority over IMF ARA.

[Design committed before scoring](../../research/HISTORICAL_BUFFER_VALIDATION.md) · [Design commit f7c8381](https://github.com/NikolozOniani/GeorgianNationalBank/commit/f7c8381003b5128b17831150f8c7e632352f3c1a)

## IMF principal: seven origins, one informative timing miss

Amounts are SDR million. The primary horizon is three months. Each recommendation starts from zero nonreserve cash in the IMF member account. The realized peak assumes incoming IMF drawings are available for subsequent principal at face value. Its alternative gives no credit for those drawings. This is a creditor-specific cash requirement. No observation here establishes an actual missed debt payment.

| Episode | Both rules recommended | Principal paid | Incoming drawings | Realized peak with draws usable | First positive peak: forecast / realized |
|---|---:|---:|---:|---:|---|
| 2010Q1 | 4.0500 | 4.0500 | 144.6 | 3.1500 | March / January |
| 2012Q1 | 25.2625 | 25.2625 | 0 | 25.2625 | March / March |
| 2013Q1 | 53.4125 | 53.4125 | 0 | 53.4125 | March / March |
| 2014Q1 | 57.5250 | 57.5250 | 0 | 57.5250 | March / March |
| 2018Q3, comparison | 10.0000 | 10.0000 | 0 | 10.0000 | September / September |
| 2021Q2 | 0 | 0 | 78.0 | 0 | No positive peak |
| 2022Q1 | 0 | 0 | 0 | 0 | No positive peak |

The January 2010 timing error is identifiable. Principal repayments of SDR 0.90m on 22 January and 2.25m on 25 January preceded a 47.3m draw on 28 January. The next principal payment, SDR 0.90m on 22 March, came after that draw. At the December cutoff, the IMF had already authorized the 47.3m purchase. It had not fixed 28 January as the cash date in the public decision. The forecast therefore credited zero. With no access to later receipts the opening requirement is 4.05m. With full access to the observed drawings it is 3.15m. Immediate drawability and a dated cash receipt are economically distinct: adding a rule for discretionary drawdown would change the question tested here. [December approval](https://www.imf.org/en/news/articles/2015/09/14/01/49/pr09456) · [Dated IMF events](imf_events.csv) · [Approvals versus receipts](drawing_evidence.csv)

Across seven primary observations both rules had **zero uncovered principal** and **SDR 0.90m total excess** relative to the usable-draw case. Holding that excess for three months at the design’s illustrative annual cost of 1% costs **SDR 2,250**; at a zero spread it costs zero. This is a sensitivity calculation, not a measured Georgian spread. Omitting 2010 removes all primary excess. Omitting any other single episode preserves the tie. The already studied 2008, 2009 and 2020 development windows are outside the scoring sample throughout. The sole median-ranked comparison, 2018Q3, offered no reduction in recommended reserves.

All **21** opening schedules matched the subsequent gross principal total at one, three and twelve months. These are nested, retrospectively selected observations, not 21 independent forecasts. At twelve months, assuming access to realized draws, recommended openings exceeded the realized IMF-account peak by SDR 10.95m for 2010, 38.95m for 2014, 30m for the 2018 comparison and 2.5m for 2021. Forecast and realized positive peaks were eleven, three and nine months apart in the first three of those cases, respectively; the 2021 realized peak was zero. Netting all annual draws against annual bills would have erased the January 2010 need. [All horizons, timing errors and carrying-cost sensitivities](imf_scores.csv) · [Paired three-month and leave-one-episode-out scores](leave_one_out.csv)

**Information grade.** For each origin, the official IMF obligations-basis query returned a no-data message. Its expectations-basis counterpart returned dated principal and other obligations with schedule coverage beyond twelve months. Only projected principal is admitted. The annual actual-transaction tables reconcile to the IMF's separately reported annual column totals. The IMF website labels the projections as of the historical origin; we could not establish when these exact versions first became public. Gross repayment agreement therefore validates an as-of reconstruction. It cannot establish live forecast performance. [Schedule coverage and choice of basis](schedule_coverage.csv) · [Exact URLs and byte hashes](source_locks.json)

## A contract that was public before the shock

The 2011 issue carried a 6.875% annual coupon, semiannual payments, USD 500m principal and a 12 April 2021 maturity. Its original issue was independently documented in the June 2011 IMF review. Georgia’s MoF bulletin no. 8 identified the USD 500m 2021 bond years before both the 2018 comparison and the 2021 maturity. We carry the published issue balance forward as a contractual forecast; the origin-date MoF stock pages corroborate it retrospectively. The December 2020 IMF review documented plans for a new issue conditional on market access. Neither an intended refinancing nor an IMF review completed in April supplies a dated pre-cutoff receipt. [Original offering circular, cover and conditions 5–6](https://www.rns-pdf.londonstockexchange.com/rns/6239E_-2011-4-8.pdf) · [Contemporaneous issuance report](https://www.imf.org/external/pubs/ft/scr/2011/cr11146.pdf) · [MoF bulletin no. 8](https://www.mof.ge/files/download/PublicSectorDebtStatisticalBulletinN8ENG.pdf/9b2af885-6a97-47e7-b251-2e9fdea8dd85) · [December 2020 IMF review, MEFP ¶16](https://www.imf.org/-/media/files/publications/cr/2020/english/1geoea2020006.pdf)

- **2021Q2.** Both rules predicted **USD 517.1875m** for the retiring bond: USD 500m principal and USD 17.1875m coupon. MoF table 6 reports **USD 517.2m** in the quarter, comprising USD 500.0m principal and USD 17.2m interest. The forecast lies in the reporting interval of USD 517.15m–517.25m. Principal redemption in April was independently reported. The exact cash date of the final coupon is unverified, so April alone receives a wider outcome interval. The new bond’s issue date was 22 April and its first coupon fell in October. Its flows belong to a different cohort. [MoF bulletin no. 16, table 6](https://www.mof.ge/files/download/N16ENG.pdf/3da0b167-26e2-4921-8e98-a3e2b8a6a383) · [Finance minister’s statement reported 15 April](https://civil.ge/archives/413361) · [Replacement offering circular](https://www.mof.ge/images/File/2021/evrobondi/20-04-21/Argo%20-%20Final%20OC.pdf)
- **2018Q3.** Both rules called for zero on this bond through September. MoF reports USD 0.0m at one decimal. We retain an interval from zero to USD 0.05m. The twelve-month contractual amount of USD 34.375m lies within the interval from the four separately rounded quarterly outturns. The 2012 and 2013 opening debt-stock tables include the other USD 64.75m issue. Annual creditor totals combining the two issues cannot verify this bond alone. For 2014, the annual and quarterly tables bound the first-quarter payment; a printed dash alone does not certify zero. Coverage and missing cases are explicit. [Outcome intervals and derivations](bond_outcomes.csv) · [Bond scores](bond_scores.csv) · [Opening stock corroboration](bond_stocks.csv)
- **Settlement matters.** TBC Capital reported that the retired bond had been paid using state-budget liquidity. It did not identify the location, currency and restrictions of the Treasury account at the forecast origin. A funded fiscal payment can still use NBG reserves if the government draws its FX deposit at NBG. For this instrument the quarterly gross service amount is observable, while the reserve delivery attributable to it could range from zero up to the gross amount under the Step 2 settlement routes. That interval does not bound the entire national buffer. [TBC Capital, 6 May 2021, sovereign Eurobond section](https://static.tbccapital.ge/uploads/files/TBCCapital_FixedIncomeRegionalMarketWatch_06.05.2021_ENG.pdf) · [Settlement rules](../reserve_buffer_policy/README.md)

## The wider public sector: a cross-check with different coverage

We also reconstructed NBG’s official FX liquidity template, section II.1, at all seven openings and matched available gross public external debt-service outturns in MoF table 6. USD million, three-month horizon:

| Origin quarter under test | Scheduled NBG-template net FX drains | MoF gross principal plus interest paid | Schedule less outturn |
|---|---:|---:|---:|
| 2010Q1 | 34.90 | unavailable | — |
| 2012Q1 | 73.08 | unavailable | — |
| 2013Q1 | 45.03 | 102.00 | −56.97 |
| 2014Q1 | 111.51 | 119.13 | −7.62 |
| 2018Q3 | 105.94 | 93.80 | +12.14 |
| 2021Q2 | 601.12 | 600.40 | +0.72 |
| 2022Q1 | 99.76 | 100.60 | −0.84 |

The 2021 maturity quarter shows close aggregate agreement. The 2013 difference goes the other way and exceeds half of reported quarterly service. These are **reconciliation differences**. NBG reports net drains on loans, securities and deposits for its template sectors. MoF reports realized gross external debt service. Coverage, valuation, timing and vintage can differ. The bond coupon and principal already appear inside the relevant aggregates and must not be added again. Neither source identifies accessible Treasury balances and funding by settlement date. Scoring their difference as a national forecast error would reward or penalize an accounting mismatch. No national peak, peak month, uncovered payment or excess-stock cost is identified for these seven origins. This also prevents a validated bank backstop or a forecast of discretionary market sales. [One-, three- and twelve-month national evidence and missingness](wider_public_account.csv)

**ARA comparison.** The pre-cutoff records include end-2016 gross reserves of 87% of ARA in the 2017 review, a December 2020 projection of 105% for end-2020, and the subsequent 2021 Article IV estimate of 108% for end-2020. Only the earlier projection was available to the March 2021 forecast among those two end-2020 figures. These are national coverage ratios across multiple risks. There is no published allocation to the IMF principal or the 2021 bond. The earlier holdouts lack a verified like-for-like contemporaneous benchmark here. A formal ARA score requires both a comparable obligation set and an observable national outturn. [Origin-by-origin information audit](origins.csv) · [IMF 17/361](https://www.imf.org/-/media/files/publications/cr/2017/cr17361.pdf) · [IMF 20/322](https://www.imf.org/-/media/files/publications/cr/2020/english/1geoea2020006.pdf) · [IMF 21/215](https://www.elibrary.imf.org/view/journals/002/2021/215/article-A001-en.xml)

## Replication and decision

Run from the repository root:

```sh
python src/validate_historical_buffer.py --check
python src/validate_historical_buffer.py --from-raw --check
python -m unittest discover -s tests -p test_historical_buffer_validation.py
```

The first command reproduces scores from the tracked IMF and bond extracts. The second also verifies input hashes, reconciles IMF annual transaction totals, verifies schedule identity and coverage, checks MoF opening USD stocks, and rebuilds the wider public-sector table from its NBG workbook and official MoF PDFs. Use `--acquire --check` for missing locked source files. Dependencies include lxml, openpyxl and Poppler's pdftotext. The bond outturn interval register is a reviewed transcription with rounding arithmetic. Original and replacement offering terms, IMF program decisions and additional contextual documents are cited separately; the source locks cover files actually downloaded for the validation. All monetary amounts in the score tables are millions of the named currency. The cost columns use the same units. Blank timing scores denote a zero peak or insufficient timing evidence. Signs on timing errors are predicted minus realized, in calendar months.

For Step 5, apply the Georgian shock amounts to the exposure actually present at each 2025–26 origin, distinguish settlement accounts and currencies, and show results with and without new support and market sales. The holdouts warrant using the method for that conditional exercise. They do not warrant selecting it over gross debt service to lower Georgia’s recommended reserves. To test an improvement empirically would require pre-cutoff records of usable **dated** funding that differentiate the two forecasts, and debtor-level post-shock cash records that can discriminate between them.
