# How much do NBG currency purchases move GEL/USD, and for how long?

**18 November 2026.** The lari was already appreciating on average before matched Georgian purchase auctions. The historical seven-day comparison is sensitive to which trades and dates enter each pair. At twelve months the monthly association changes sign when the starting year changes. The [independent audit](AUDIT.md) reproduces the calculations, reconciles three month-end auction entries under an explicit timing assumption and shows why the 2025–26 price response remains unidentified. [Registered design](../../research/R3_FX_RESPONSE_DESIGN.md) · [Numerical decision record](validation.json)

## What happens around a Georgian purchase auction?

The NBG cash-auction workbook records 346 executed auctions, March 2009–October 2024. Of these, 159 were purchases and 187 sales. A purchase had a median size of USD 15m and a maximum of USD 40m. Only four purchases took place from 2020 onwards, all in 2022, and three occurred within ten days in August. The official exchange-rate observations are valid-date quotes in GEL per USD. An increase indicates depreciation. Execution prices, intraday surprises and private orders are absent from these workbooks. [Dated auction records](../../data/derived/r3_fx_response/auctions.csv) · [NBG exchange-rate convention](https://nbg.gov.ge/en/page/foreign-exchange-market)

For each purchase we compare the cumulative movement of the quote with that after an earlier same-weekday date in the same year. Matching uses the preceding seven- and 28-day returns. On average, in the week **before** the 155 one-day matched purchases the lari had already appreciated by 0.59 log percentage points, versus 0.28 at controls. The older pretrend from day −28 to day −7 differs by only 0.006 points, but those returns are linear combinations of the matching variables. This comparison supplies little independent evidence for parallel trends.

| Calendar days after purchase | Matched purchases | Purchase less comparison return, mean log pp | Pairs with no later listed auction through either valid-date endpoint | Mean difference for those pairs, log pp |
|---:|---:|---:|---:|---:|
| 1 | 155 | −0.010 | 131 | +0.002 |
| 7 | 155 | +0.160 | 26 | −0.128 |
| 28 | 150 | +0.754 | 8 | +2.937 |
| 84 | 121 | +3.432 | 0 | unavailable |

At seven days both groups appreciated on average (−0.029 after purchases and −0.189 after comparison dates). The positive difference means *less appreciation relative to the match*. It does not establish that the purchase caused a depreciation. The table counts later auctions on the valid date of the endpoint quote. Dropping such endpoint-day trades from the exclusion gives −0.024 across 39 seven-day pairs. Rematching with the comparison outcome outside the pretrend used for matching gives +0.078 across 150 pairs before auction exclusions. Removing overlapping auctions also selects on future market conditions. Either sample can be biased. At 84 days the matching design permits only the date 91 days earlier on the same weekday. Every surviving pair overlaps at least one other auction and the mean pre-match distance rises to 2.38 points, from 0.88 at one day. Inferring a three-month response from the +3.432 figure would assign later trading and changing macroeconomic conditions to the original purchase. These are per-event averages across trades of different sizes. Dividing by the median auction size would invent a marginal price elasticity. [Every event, control and unmatched observation](auction_pairs.csv) · [Full results by era and horizon](auction_comparison.csv)

One matched March 2009 purchase uses a comparison date before the auction instrument existed. The NBG initially offered auctions twice a week while the interbank exchange still determined the fixing. Subsequent changes in auction frequency, price formation and trading are further limits on historical comparability. A predetermined opportunity to hold an auction does not establish predetermined purchase direction, amount or take-up. [NBG launch notice](https://nbg.gov.ge/en/media/news/the-national-bank-of-georgia-launched-a-new-monetary-policy-instrument-the-currency-auct) · [NBG change of frequency](https://nbg.gov.ge/en/media/news/the-frequency-of-currency-auctions-will-decrease-by-the-decision-of-national-bank-of-georg)

## How do monthly purchases relate to subsequent changes in GEL/USD?

The monthly workbook covers November 2015–December 2024 (110 pre-episode observations). The sale and purchase regressors are the negative and positive parts of **net market intervention**, both entered as positive magnitudes. Options and swaps stay outside the spot ledger. Opposite gross flows within one month can cancel. At horizon h the outcome is the cumulative log change from the end of t−1 through the end of t+h. Thus h=0 is the purchase month, h=1 includes the next month, and h=12 covers 13 months of price movements. Each coefficient below is in log percentage points per additional USD 100m of positive monthly net purchases. The full specification controls for prior return, prior net flow and the separate net-sale regressor. Parentheses contain autocorrelation-robust standard errors for this **association**.

| Horizon | Full pre-episode history | From January 2020 | From 2020 with broad dollar and VIX |
|---|---:|---:|---:|
| Previous month's return (placebo) | −0.87 (0.50) | −0.28 (0.46) | −0.24 (0.49) |
| Purchase month | −0.59 (0.52) | −0.37 (0.54) | −0.07 (0.60) |
| One month later | −0.05 (0.69) | +0.02 (0.72) | +0.17 (0.64) |
| Three months later | −0.74 (1.08) | +0.37 (0.98) | +0.67 (0.76) |
| Six months later | −0.87 (1.11) | +0.98 (1.17) | +0.76 (1.03) |
| Twelve months later | −1.43 (2.05) | +1.97 (2.49) | +1.98 (1.67) |
| Eighteen months later | −2.16 (3.05) | +4.09 (3.07) | +4.26 (1.93) |

For the purchase month, the first column uses 108 months, including 46 positive-net months. The long-horizon full regression uses 90 months, including 35 positive-net months. Current global controls are available from February 2020, giving 59 to 41 usable months as the horizon increases. Long-horizon returns overlap and include later policy responses. Newey–West errors account for sample dependence under their assumptions. They do not correct for selection, model changes or multiple horizon comparisons. The recent positive eighteen-month coefficient cannot establish a causal response or its half-life. There is no validated single impact relative to which a half-life could be measured. [All projections, standard errors, controls by specification and observation counts](monthly_projections.csv)

The previous month's return precedes current-month purchases. Its negative full-sample association is consistent with buying after appreciation. It is imprecise and expectation effects could precede trades. The contemporaneous association can also arise when private inflows strengthen the lari and induce the NBG to buy USD. A linear omitted-variable diagnostic asks how strongly one omitted factor would need to relate to both flow and price to explain the fitted association entirely. At h=0 those equal partial R-squared values are 9.7% in the full sample and 1.5% with recent global controls. These quantities neither measure private order flow nor place an upper bound on its strength. The formula sets the absolute bias equal to the estimated slope: for residualized positive flow x, full-model residual e and equal partial R-squared R, solve R/sqrt(1−R) = |slope| × norm(x)/norm(e).

## What assumption makes the external calibration fit Georgia?

The earlier R3 model imposed an immediate effect of +1.913 log percentage points on GEL per USD for purchases equal to 1% of annual GDP, with persistent dynamics. We measured the partial correlation between signed intervention and the FX-market shock that this price equation requires in the 57 Georgian pre-episode months. After accounting for the registered controls, that correlation is **−0.486**. A large purchase is paired with a shock that, acting alone, would strengthen GEL. This is economically consistent with buying into appreciation pressure. The observations do not independently tell us how strong that selection was. A zero direct kernel requires −0.246, reversing the direct kernel requires +0.050, and the short-lived specification requires −0.449. The latter alters the persistence of the exchange-rate level as well as the intervention impulse, so this is a joint specification comparison. No correlation here is an externally observed shock. [Kernel calculations](kernel_diagnostics.csv) · [External calibration and source units](../../research/R3_REOPEN_DESIGN_2026_11_16.md)

An algebraic extension of the registered correlation test shows the magnitude of that ambiguity. Keep the published autoregression and lag coefficients fixed. After partialling out the controls, let Q be current flow and Y the price after subtracting those fixed terms. For an imposed current impact b the implied shock is Y−bQ. Invert its sample correlation with Q to obtain the current impact compatible with any assumed correlation. This is a finite-sample identity conditional on these restrictions.

| Assumed correlation between flow and the unobserved FX shock | Implied current impact, log pp per 1% of annual GDP |
|---:|---:|
| −0.50 | +2.05 |
| −0.25 | +0.05 |
| 0 | −1.57 |
| +0.25 | −3.19 |

The sign changes near **−0.243** under these fixed lag coefficients. Even assuming purchases lean against appreciation pressure leaves both a negligible and a large positive impact compatible with this history. The table uses illustrative correlation values with no assigned probabilities. The shock includes omitted variables, timing error and any misspecification of the price equation. Treating −0.50 and −0.25 as empirical bounds would manufacture a price-impact range. [Exact sensitivity calculation](selection_sensitivity.csv)

## Treatment, timing and scale

- The largest monthly net purchase in the 110-month pre-episode workbook was **USD 322.40m**. In January 2025–September 2026 the maximum was **USD 632.85m**. Eight of 21 episode months exceeded the historical maximum in nominal USD. Exchange-market size and GDP can change over time. The dollar comparison establishes extrapolation in the regression's units. It does not establish that market depth stayed fixed.
- Monthly auction purchase and sale legs reconcile with the dated workbook except for three adjacent-month offsets: USD 10m of purchases in September/October 2018, USD 60m of sales in September/October 2021, and USD 32.305m of sales in August/September 2022. The direction-specific totals cancel over the comparison period. Assigning each auction to the following weekday reproduces both legs in all 110 months, consistent with the published next-business-day settlement rule. Individual value dates remain unverified. [Timing audit](AUDIT.md) Using the dated auction months in an additional sensitivity moves the full purchase-month slope from −0.59 to −0.68. All historical source amounts are preserved. [Discrepancies](auction_reconciliation.csv)
- The 2019 option design had a public price trigger tied to the previous 20 working days. The planned auction size could change with liquidity. Eligibility and exercise are separate decisions. The option sheet has 11 dated schedule rows, five with positive volumes sold and two with explicit positive exercised amounts, GEL 50m and GEL 86m. The other exercise cells are blank. The USD market workbook records USD 51.322m exercised in February 2019. The records do not identify daily exercise dates, prices and amounts on either side of the threshold. They cannot verify a discontinuity in executed purchase volumes. Even a validated 2019 threshold response would concern that instrument and the local threshold. [Option rows](../../data/derived/r3_fx_response/options.csv) · [NBG option terms](https://nbg.gov.ge/en/media/news/the-nbg-will-use-a-new-instrument-fx-options-to-replenish-the-international-reserves)
- The NBG distinguishes discretionary auctions from rules-based BMatch operations. In the registered episode the public ledger discloses monthly net amounts, with no matched execution-time quotes or gross BMatch legs. A nonauction comparison date can contain other official or private FX trading. Repeated official weekend and holiday quotes are accepted as published values. [NBG statement](https://nbg.gov.ge/en/media/news/statement-of-the-national-bank-of-geor-26) · [R1 accounting](../r1_2026_11_10/README.md)

**Decision.** Historical comparisons quantify selection, poor overlap at long horizons, and extrapolation in trade size. These findings narrow the claims the study can make. They leave the Georgian causal purchase coefficient and its persistence unresolved. Calibrating the episode requires an independent source of purchase variation or credible restrictions on the correlation with private appreciation pressure, plus evidence linking local impacts to sustained BMatch purchases. The reserve and household accounts cannot use these associations as causal inputs.

## Reproduce the tables

The [design](../../research/R3_FX_RESPONSE_DESIGN.md) was committed before event matching or slope estimation. The calendar-reconciliation sensitivity and inversion of the correlation diagnostic are labeled additions. The [locked NBG source manifest](../../data/source_manifest.json) contains URLs and SHA-256 for fx_auctions, fx_market and fx_daily_history. The [extracts](../../data/derived/r3_fx_response) retain native units and source rows. The option schedule uses GEL, the auction sheet uses USD, and the monthly workbook uses USD millions. The original R3 modeling panel supplies the previously verified global controls, policy rate and historical GDP scaling. No episode price observations enter the historical fits.

From the repository root, run the commands below with NumPy 2.3.5 and openpyxl 3.1.5. The first two commands use committed data offline. The third verifies the three vintage files and reproduces the extracts. Add `--acquire` to that third command to fetch missing raw files from their pinned official URLs. Providers can replace historical URLs with new vintages. The original lock must still match.

```sh
python src/r3_fx_response.py --check
python -m unittest discover -s tests -p test_r3_fx_response.py -v
python src/r3_fx_inputs.py --check
python replication/check_repository.py --replicate
```

The focal tests recompute each matched quote ratio and count later auctions, check all overlapping monthly auction legs, independently reproduce the full-history purchase slopes and Bartlett HAC errors via scalar partial regression, and verify the selection inversion. Bytewise checks reproduce all tables in the tested environment. [Validation record](validation.json)
