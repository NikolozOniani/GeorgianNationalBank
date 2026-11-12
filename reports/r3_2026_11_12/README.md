# Can public evidence identify the lari path without NBG purchases?

**Design decision, 12 November 2026.** For January 2025 through September 2026, withhold the estimated no-purchases GEL/USD path, an empirical range, the average and terminal policy effects, and the associated reserve and liquidity paths. G2 remains unsatisfied. The registered estimand is the percentage by which the actual GEL/USD quote exceeded the quote under removal of discretionary purchases. A positive value would mean that purchases weakened the lari. The evidence permits zero and either sign. The sign of the immediate mechanical demand impulse under fixed market conditions is a narrower question.

## What is measured

| Observation | Result for the registered window |
|---|---:|
| Official GEL per USD, opening to closing | 2.8068 to 2.6051 |
| Observed change in the GEL price of a dollar | −7.19% |
| Net market purchases | USD 5,803.15 million |
| Minimum gross purchases / minimum gross sales | USD 5,819.35 million / USD 16.20 million |
| Months reporting both nonauction gross directions | 0 of 21 |
| Instrument-month fields with a trade date and execution price | 0 of 105 |

The lari appreciated while NBG bought FX. Whether it would have appreciated further is the missing comparison. The annual report describes purchases in its account of 2025 accumulation and elsewhere explicitly gives the cumulative **net** amount. The gross lower bound sums separately observed auction amounts and the positive nonauction net amounts. One can add the same nonnegative amount to both nonauction sides in any month and preserve the disclosed net. March 2026 includes net sales. Treating all positive monthly net amounts as exact purchases requires an additional one-way-trading assumption.

We inspected the NBG FX workbook as a possible upper bound. Its USD bank-buy sheet carries nonauction NBG activity **net** (cells D5, K6 and Q6 identify the convention). The bank-sell sheet reports auction, option and swap categories separately, without a matching gross nonauction sales-to-NBG column. Moreover, eligible BMatch participants extend beyond resident banks. Applying resident-bank turnover as an episode-wide cap requires evidence on counterparty coverage, instrument and non-netted reporting. February 2026 also has a quarantined bank aggregate. A verified total for all in-scope trades counted once could cap gross purchases. It would still leave their price response undetermined. [Workbook provenance](../r1_2026_11_10/sources.json) · [NBG fixing and market participation](https://nbg.gov.ge/en/page/foreign-exchange-market)

## Public evidence for impact and persistence

| Source and locator | Relevant result | Applicability to this episode |
|---|---|---|
| Aslanidi, CERGE-EI WP 344, §IV and Table 12 | Actual Georgian daily interventions in 1996–2007. The lagged intervention term in the exchange-rate equation supports appreciation following FX sales. Structural breaks occur within that historical sample. | A historical relationship worth testing. Its daily coefficient is sensitive to regime, market size, trade direction and simultaneity. Persistence in conditional **variance** does not measure persistence in the price **level**. [Study](https://www.cerge-ei.cz/pdf/wp/Wp344.pdf) |
| Gavashelishvili, proceedings, p. 269 | Georgian daily auction analysis reports bidirectional predictive relationships and slow error correction during a depreciation episode. | Lagged predictability alone supplies neither an excluded instrument nor a bound on the effect of reserve purchases on BMatch. [Study](https://www.ibav.org/yayinlar/UOM2ENG.pdf) |
| Arevadze and coauthors, Monetary Economics 1(2), pp. 30–31, figs. 5–9 | Their 2024 no-intervention simulation produces **2.3 percentage points** more short-term depreciation in the **real bilateral exchange-rate gap**, on average. The paper also records the subsequent resumption of purchases. | The stress episode, outcome, direction of trades and horizon differ. Reversing the sign or scaling by dollars sold does not recover nominal appreciation from removing an anticipated purchase program. [Study](https://nbg.gov.ge/fm/პუბლიკაციები/კვლევითი_ნაშრომები/მონეტარული_ეკონომიკა/2025/n2/monetaryeconomics-eng-n2.pdf) |
| IMF 2025 Selected Issues, §§7–8, 28–31, figs. 18–20 | The QIPF model attributes a short-run stabilizing role to USD sales during the pandemic and the 2024 election shock. Its historical FXI input includes a proxy. The authors discuss uncertainty about shock persistence. | Evidence for a possible short-run benefit. An estimated risk shock, its offset and an intervention price elasticity are different quantities. The paper supplies no validated 2025–26 BMatch purchase impulse with a transferable monthly decay schedule. [Report](https://www.imf.org/-/media/files/publications/cr/2025/english/1geoea2025002-source-pdf.pdf) |
| IMF 2026 Article IV informational annex, Exchange Rate Arrangements; NBG August 2025 release | BMatch results are disclosed with a lag. NBG reports accumulating when market conditions permit. Spot fixings average trades across a business-day window. | A disclosure date is unsuitable for locating execution impact. The trading rule responds to market conditions that themselves move the lari. [Annex](https://www.elibrary.imf.org/view/journals/002/2026/133/article-A002-en.xml) · [Dated release](https://nbg.gov.ge/en/media/news/nbg-boosts-international-reserves-by-usd-1-3-billion-since-start-of-2025) |
| TBC Capital, Georgian Economy 2025–2026, net FX inflows analysis | Its trade, transfers and tourism composite suggests increased FX supply in 2025. | This gives a concrete competing explanation for simultaneous appreciation and reserve buying. The composite omits order flow and portfolio substitution. It cannot isolate intervention by subtraction. [Analysis](https://tbccapital.ge/static/file/202601221958-georgian-economy-2025-2026.pdf) |

## Why even a range fails

Consider the illustrative equation for monthly log GEL/USD, y(t) = u(t) + b × P(t), where P is gross purchases and u includes private demand, external shocks and other policy responses. Even granting exact P, for any candidate b the sequence u(t) = y(t) − b × P(t) fits the observed series exactly. The problem survives allowing a distributed lag. An assignment mechanism independent of u, or credible joint restrictions on u and the response coefficients, would distinguish these explanations. A long pre-period or accurate forecasts do not establish that the fitted relationship survives removal of the purchase rule. This argument shows insufficiency of the observed restrictions. It makes no assertion that all imaginable paths are economically equally likely.

**Inverse sensitivity check.** How large would a price response have to be to produce a *stipulated* 1% September 2026 gap? For this diagnostic alone, take gross purchases at their monthly floors, use one constant log-price impact per USD 100 million, assume a zero opening gap, and suppress all endogenous policy, private-flow and expectations offsets. Let the previous month's log gap retain fraction r. The required impact is 10,000 × log(1.01) divided by the sum of purchases in USD 100 million weighted by r to the number of months before September 2026.

| Assumed monthly retention | Required immediate log-price impact per USD 100m |
|---|---:|
| 0% | 40.04 basis points |
| 50% | 12.76 basis points |
| 100% through the endpoint | 1.71 basis points |

These are coefficients **required** to generate the same arbitrary test gap. None was estimated. Choosing only the duration of impact changes the required coefficient by more than twentyfold. Additional unobserved two-way trading changes the exposure again. With policy feedback restored, the conversion can change sign. This calculation supplies no numerical prediction, plausible interval or probability for the registered effect. [Calculations and input hashes](diagnostics.json)

## Decision by method and conditions for reopening

| Method | Decision on the current vintage | Public evidence or test that could change it |
|---|---|---|
| Event, IV or threshold | Reject for the episode. The monthly ledger has no paired execution times/prices. The documented matching algorithm orders bids and offers but supplies no exogenous assignment. | Dated gross fills, pre-order quotes and trigger inputs, a rule/version or surprise with a defensible exclusion. Check manipulation, news, anticipation, first-stage strength and support before extrapolating to program removal. |
| Structural simulation | No calibrated episode path. Gross purchases, net private flow response, horizon-specific price response and expectations are jointly unresolved. R2 ratios supply a balance-sheet starting point only. | Verify a public calibration against Georgia's purchase-side market depth, same-unit impact, decay and regime. Register the information assumption before fitting. Validate on withheld comparable periods and match FX, reserve and GEL balance sheets. |
| Partial identification | Only purchase-volume floors verified. The public restrictions yield no informative endpoint or average FX bound. | Establish defensible ranges for quantities, shock confounding, impact, persistence and policy feedback jointly. Include zero and sign reversals unless independent evidence rules them out. |
| Forecast / cross-country donor | Diagnostic only. No validated untreated comparator shares Georgia's inflow and currency-demand shocks. | Document donor interventions and exposures, hold out pre-episode observations and assess breaks, placebos and leakage. Even a successful forecast needs a causal invariance argument. |

**Policy responses required for a future simulation.** Start both paths from the same December 2024 balance sheet and remove only discretionary market purchases. Let emergency sales respond to conditions under their retained rule. Let refinancing, remunerated balances and sterilization adjust to GEL liquidity demand and the policy-rate rule. Carry fiscal financing and external shocks across paths while allowing conversions, valuations and private portfolios to respond consistently. Separate an unexpected suspension from a publicly anticipated change. Neither information assumption has adequate episode evidence to select it. Fixing realized emergency sales, refinancing and private flows across both paths would instead impose the answer on part of the system. No balance-sheet path is released under that shortcut.

**Consequence for the study.** R4 can advance measured reserve income and funding accounts and conditional marginal-cost schedules. Household consequences can be stated per stipulated exchange-rate change. An episode-attributed household effect, incremental reserve path or net welfare verdict still requires additional identification. Reopen R3 only when public evidence materially narrows one of the missing restrictions above. No correspondence is part of this design.

[Registration](../../research/R0_REGISTRATION.md) · [Roadmap](../../research/ROADMAP.md) · [R1 account](../r1_2026_11_10/README.md) · [R2 results](../r2_2026_11_11/README.md). Reproduce the arithmetic from the repository root with `python src/r3_design.py --check`.
