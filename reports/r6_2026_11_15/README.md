# Reserve insurance and financing: what benefit would justify the cost?

**R6 checkpoint, completed 16 November 2026.** Public evidence supports liquidity accounting and conditional financial/insurance thresholds. It does not identify the benefit achieved by the registered purchases, the no-purchases reserve path, or an optimal reserve stock. G4 is **partially satisfied**. The calculations below supply falsifiable requirements for a justification; they do not settle the episode's net welfare effect. The dated folder identifies the start of this work.

## Results that change the assessment

- Under R4's constant-rate, unchanged-FX, CD-funded scenario, USD 100 million of additional reserves has a **USD 4.22 million one-year financial cost**. If an avoided crisis loss were 10% of the rounded 2025 GDP, an annual probability reduction of **0.111 percentage point** would equal that amount. This is a cost-equivalent requirement, not an achieved reduction or a measured national cost.
- The public end-2025 schedule leaves **USD 1.644–4.821 billion** after the particular combinations of disclosed drains, contingent calls and unavailable gold examined here. These are four assumptions, not a confidence interval or a bound on all possible usable reserves. Extra reserves cover a shortfall only once that assumed buffer is exhausted; market-functioning and probability effects could arise earlier and remain unvalued.
- For a hypothetical USD 100 million increment above observed end-2025 reserves, the printed IMF log-spread slope implies a **1.298 basis-point** spread reduction. Applied to the actual USD 500 million January 2026 issue, it increases modeled issuance proceeds by **USD 0.279 million**. Five years of the CD-funded reserve cost have a present value of **USD 18.047 million** under the specified discount convention. Financing proceeds alone require **82.058 basis points** of yield reduction to offset that scenario. This tests one issue and one financing channel; it does not reproduce or reject the IMF's total insurance recommendation.
- Translating 145–150% ARA through the two independently reconstructed end-2025 denominators implies **USD 3.077–4.029 billion** above the observed stock. Holding denominators, funding rates and FX fixed gives annual CD-funded costs of **USD 129.85–170.04 million**. Neither the increment nor its cost is an estimate of what the episode actually caused.

[Conditional exhibits](conditional_benefits.svg) · [Machine-readable assumptions](../../research/r6_assumptions.json) · [Replication](../../replication/R6.md)

## 1. Financial cost and the insurance hurdle

The starting financial calculation is R4's USD 100 million asset, USD return proxy of 3.87%, GEL funding at 8.09% and GEL/USD of 2.6951. These are end-2025 anchors; constant rates, rollover capacity and full CD funding are assumptions. SOFR is a return proxy, not the reserve portfolio's realized return. Both asset and funding principal are included at the terminal date. For terminal proportional FX change x, USD cost is

`C = 100 × [(1 + f)/(1 + x) − (1 + u)]`.

At unchanged FX, C = 4.22. At R4's chosen −5% and +5% quote changes, the financial sign can change. Non-interest-bearing financing earns positive carry at unchanged FX. R4's funding-mix threshold remains 47.8% CD financing. There is no evidence that all additional reserves were CD-funded, or that these rates would remain fixed as the position grew. [R4 cost account](../r4_2026_11_12/README.md)

The one-year insurance equations are `required Δp = max(αC, 0)/L` and, at fixed probability p, `required ΔL = max(C, 0)/p`. L is the loss in a crisis, not an annual loss in every state. A reduction from 10% to 9.889% is 0.111 percentage point, not 11.1 percentage points. With a loss of USD 3,810 million (10% of rounded USD 38,100 million GDP), the CD scenario needs Δp = 0.00110761. At chosen annual probabilities of 5%, 10% and 20%, the equivalent severity reductions are USD 84.4, 42.2 and 21.1 million. These probabilities are scenarios, not estimates from Georgia's short sample or verified annual versions of the IMF calibration. No multi-year probability is silently treated as annual.

| Assumed conditional crisis loss | Probability reduction equal to USD 4.22m | Unit |
|---|---:|---|
| 5% of GDP | 0.222 | annual percentage point |
| 10% of GDP | 0.111 | annual percentage point |
| 20% of GDP | 0.055 | annual percentage point |

The financial hurdle is not a national welfare account. Domestic CD interest is also recipients' income; asset revaluation is not automatically a resource loss. The output varies α over 0, 0.5 and 1 as an expressly hypothetical conversion from the positive financial hurdle to a resource-cost hurdle. No value of α is estimated or asserted to bound the true resource cost; omitted costs can lie outside this grid. The severity output separately shows a convention in which cost is incurred only in the normal state: `(1−p)C/p`. That convention must not be mixed with the all-state financial cost. A true comparison needs state-dependent funding, FX, asset returns, consumption and terminal values. R5 partial household effects are not added to this hurdle.

[135 hazard sensitivities](hazard_thresholds.csv) · [45 severity sensitivities](severity_thresholds.csv)

## 2. Liquidity service, timing and overlapping claims

The R2 source template supplies 22 month-ends and three cumulative horizons (1, 3 and 12 months). Each of four combinations at each horizon is preserved separately: 264 observations. Signed predetermined drains are section II.1; calls on section III.1 are additional only under the stated assumption that claims are disjoint. Available assets are at reported face/statistical value, with gold alternatively excluded. There is no verified currency-by-maturity matching, additional credit line, or right to draw private-bank assets. These missing quantities remain missing.

| End-2025, next 12 months | Conditional remaining buffer, USDm |
|---|---:|
| Predetermined drains only | 4,821.389 |
| Predetermined drains; gold unavailable | 3,819.075 |
| Predetermined drains; full contingent calls | 2,646.168 |
| Predetermined drains; full calls; gold unavailable | 1,643.854 |

For buffer B, additional liquid assets A and an additional **disjoint** FX need D, the shortfall avoided is `max(D−B,0) − max(D−B−A,0)`. No dollar is used twice. Three cumulative maturity horizons must never be summed. Private external debt, QEDS amortization, bank runs and historical sales are not appended to the template as if they were automatically separate calls on NBG. Undrawn alternatives are not assumed available. The 0.5 and 1.0 liquid-share choices affect only the hypothetical increment.

For example, under the fourth scenario an additional disjoint USD 1.7 billion need would leave a USD 56.146 million shortfall before the increment. A fully liquid USD 100 million addition covers it; a USD 50 million usable addition covers only USD 50 million. At a USD 2 billion need, the full addition covers USD 100 million but still leaves USD 256.146 million uncovered. These are liquidity quantities, not GDP losses averted. Without a distribution of disjoint calls, a depletion rule and a loss function, neither their expected value nor the episode's position on the marginal-benefit schedule is known.

For scale only, the complete 2020–2024 public intervention windows have maximum net sales of USD **591.100 million in one month**, **656.600 million in three months**, and **1,039.332 million in twelve months**. Purchases offset sales inside each window. These policy transactions are not gross private outflows, an external financing gap, or an upper bound on a future crisis. Their timing, the later buffers and the template drains differ. No stress probability is inferred from them. The source's annual-definition discrepancies remain in R1.

[Joint schedule](joint_liquidity.csv) · [Conditional service curves](liquidity_service_curves.csv) · [Historical windows](historical_sales_scale.csv) · [R2 underlying definitions](../r2_2026_11_11/README.md)

## 3. An actual financing exposure and a maturity-matched test

The Ministry of Finance's February 2026 debt report gives original issuance terms, not a modeled sovereign borrowing rate. Its January issue has USD 500 million face value, 22 January pricing, 28 January settlement and 28 January 2031 maturity. Coupon is 5.125%, price 98.917 per 100, and re-offer yield 5.375%. The matched benchmark is the 3.625% US instrument due 31 December 2030, yielding 3.856%; the reported spread is 151.9 basis points. The offering document confirms semiannual coupons. Fees are unavailable.

The price/yield calculation reproduces 98.916516 per 100, which rounds to the reported price. Gross reported proceeds are USD 494.585 million; the pricing calculation differs by USD 0.002421 million, within price rounding. Face value is not issue proceeds. [Original terms and exact source links](../../research/r6_bond_terms.json) · [Downloaded PDF hashes and dates](../../data/r6_source_manifest.json)

The same report's 2021 issue had a 2.875% yield and a 0.801% benchmark yield. Across the two pricing dates, the borrowing yield rose **250 basis points**, decomposed into **305.5 basis points higher benchmark yield** and **55.5 basis points lower spread**. The lower spread is evidence against describing the higher coupon as proof that Georgia's country risk increased. It does not identify reserves as the cause of reduced spread. Fiscal conditions, global risk appetite, political developments, demand, issuance structure and maturity differences remain competing explanations. These two observations cannot estimate their separate effects. [Issuance comparison](issuance_comparison.csv)

For the financing sensitivity, anchor the baseline yield to that issue and reserves/GDP to the end-2025 R2 stock. For increment A, the printed Annex slope k = 0.0575 implies `Δs = k log(1 + A/(GDP+R))`. This is a locally anchored diagnostic using the published slope, not a reproduced Georgian calibration or causal estimate. The hypothetical higher-reserve yield is baseline yield minus Δs. Holding face value and coupons fixed, the financial service is the increase in issue proceeds. It is not a payment received each year on all outstanding debt.

Hold the additional USD 100 million stock for five years, retain the reserve principal as a terminal asset against repayment of its funding principal, and assume unchanged FX and R4 rates throughout. The positive annual cost is paid at each year-end. Discount at the actual issue yield's effective annual counterpart, 5.4472266%. The five-year cost is USD 18.046709 million. Pricing the ten semiannual bond payments at the reduced yield gives USD 0.279492 million extra proceeds under the Annex slope. Offsetting the cost requires an 82.057773 basis-point yield reduction. Eliminating the entire 151.9 basis-point sovereign spread would raise modeled proceeds by USD 34.022323 million; this is a conditional ceiling with the benchmark held fixed, not an achievable policy effect.

The comparison assumes equal incremental issuance fees, unchanged credit/default treatment and no change in issue volume. It combines a December rate anchor with January issue terms as a hypothetical calibration, not a claim about the information available before every purchase. The discount rate is a financing convention, not an estimated social discount rate. Changing funding, FX, persistence, price-risk treatment or the borrowers who benefit can change the result. The issue-level channel cannot be scaled to all debt without identifying new exposures and their terms.

The p. 15 dollarization formula gives an isolated crisis-loss reduction of **USD 0.429933 million** for the same USD 100 million increment. At the separately chosen 10% annual hazard, expected loss reduction is **USD 0.042993 million**. This finite difference matches the existing R2 function. It is not the total benefit of reserves, and it is not added to financing, liquidity service or other crisis losses. [All financing and model-channel calculations](financing_and_model_channels.csv)

## 4. Economic scale of the IMF target

| Fixed end-2025 denominator | ARA target | Additional reserves, USDm | Annual CD-funded cost, USDm | Cost-equivalent probability reduction, pp* |
|---|---:|---:|---:|---:|
| M2 construction | 145% | 3,076.931 | 129.846 | 3.408 |
| M2 construction | 150% | 3,395.420 | 143.287 | 3.761 |
| M3 construction | 145% | 3,689.680 | 155.704 | 4.087 |
| M3 construction | 150% | 4,029.299 | 170.036 | 4.463 |

*Assumed crisis loss 10% of rounded 2025 GDP; full financial cost used solely as the cost-equivalent hurdle. The larger probability reductions are requirements, not outcomes. Starting from a chosen 10% annual hazard, they would require about one-third to nearly one-half of that risk to disappear if the only service were probability reduction.

These translate a published ratio through independently reconstructed denominators. The official component vector, private-buffer adjustments and the reported optimum remain unreproduced. Purchases can alter money, liabilities, exchange rates and the denominator itself; funding capacity and rates need not be linear at this scale. The table therefore supplies neither a required purchase program nor a cost bound. [Target sensitivity](target_sensitivity.csv)

## 5. What is established, and what R7 must preserve

| Requirement | Completed evidence | Remaining limitation |
|---|---|---|
| D14: usable liquidity | Reconciled scenario arithmetic and maturity-specific service schedules | Currency matching, collateral/encumbrances and overlapping calls; no verified additional facility |
| D15: IMF model | Finite-difference spread and loss channels; scale of target under two denominators | Full calibration, implemented constraints, joint simulations and optimal target still unreproduced |
| D16: financing | Two original issue comparisons; 2026 price, yield, benchmark, amount, settlement and maturity; source hashes | Fees, daily event controls, other eligible new financing and causal reserve–spread response |
| D18: insurance | Explicit annual hazard/severity requirements, historical scale checks, single-use liquidity accounting | Joint stress distribution, likelihood, loss duration, depletion/alternative-access policy and reserve-dependent response |
| G4: benefits | Reproducible conditional requirements and an issue-specific financing test | Actual episode benefit, optimal reserve stock and net national welfare remain unidentified |

The strongest favorable case is still material: a sufficiently large insurance service or cheap funding can justify reserve accumulation, and annual probability reductions small in absolute points can be valuable when losses are large. The strongest adverse result here is narrower: the printed spread channel, applied only to the verified issue, is far below the five-year CD-funded financial hurdle. Neither establishes the sign of the whole episode.

R7 should now consolidate the R1–R6 claim ledger, economic boundaries and uncertainty, and independently verify the central equations. It must not turn these scenarios into an empirical confidence band, add R5 transfer/price effects to an overlapping macro loss, or present the unidentified no-purchases lari path as estimated. Only public evidence may narrow those gaps. No manuscript is written at this stage.

**Validation:** 49 active tests and 32 preserved numerical tests pass. All 120 archived files retain their hashes. Four historical generators reproduce 41 numerical files, with only the two previously documented line-ending differences. R6 source extraction, all numerical outputs and the figure pass their separate exact checks. [Verification record](repository_validation.json)
