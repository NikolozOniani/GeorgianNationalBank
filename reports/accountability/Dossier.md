# რატომ და როგორ გვაღარიბებს ეროვნული ბანკი?

## Evidence-based political investigation — first public version

**Finding:** Georgian evidence documents a substantial increase in national consumer prices, large changes in the policy rate, and sizeable FX transactions. It does **not** establish the NBG's net contribution to household impoverishment. The defensible critical case concerns the distribution of policy burdens, the justification of choices, and the ability to reconstruct those choices from public records. The title is an investigative question, not an established verdict.

Historical evidence: 2017 household pilot and 2020–2024 policy panel. Current institutional/disclosure check: **8 November 2026**. Starting main commit: `43c00d543485d47069b5ddb9755e9363b733c512`. All prior research is preserved. This edition reuses it without re-running acquisition or expanding causal regressions.

Use the [speech](Speech_ka.md), [claim briefing](Fact_check.md), [scoreboard](Scoreboard.md), [reforms](Reforms.md), [illustrations](Illustrations.md), [numeric ledger](evidence_ledger.csv), and [source register](sources.md) together. Source IDs below resolve to exact primary URLs, source hashes and page/field locators in that register. Every number used publicly has either a ledger ID or a directly identified legal/document locator. Evidence classes: **A** directly documented observation or institutional fact; **B** accounting identity or conditional arithmetic; **C** defensible descriptive estimate; **D** model-dependent counterfactual; **E** plausible unverified empirical hypothesis. Recommendations and normative judgments are marked as such, not disguised as A–E evidence.

## 1. Control, influence and responsibility

The current Georgian Organic Law identifies price stability as the main task; financial stability, transparency and sustainable growth are also relevant within that hierarchy. The NBG conducts monetary/FX policy, supervises finance, manages reserves and acts as government banker/fiscal agent. Independence and annual parliamentary accountability coexist. Current law provides monthly balance-sheet and annual reporting obligations. See LAW Articles 3–4, 60–61; CONSTITUTION Article 68. These are current institutional rules, not a retrospective legal opinion on every 2020–2024 transaction.

| Decision | NBG's direct power | Limits on attribution |
|---|---|---|
| Policy rate and liquidity operations | Sets its instrument rate and supplies/absorbs central-bank liquidity; collateral and eligibility matter | Retail loan prices also reflect funding, risk, maturity, operating costs and competition; a policy-rate change is not an identical change in every loan |
| Refinancing | Collateralized central-bank lending supports rate implementation and liquidity | A loan asset with collateral and repayment is not a grant or evidence of a bank subsidy; subsidy claims require terms versus risk-adjusted alternatives |
| FX auctions/BMatch | Executes purchases/sales and chooses intervention arrangements | Market demand, trade, tourism, remittances, capital flows and expectations also determine the exchange rate; official fix is not a guaranteed retail conversion price |
| Reserves | Portfolio allocation and intervention affect the buffer | Government FX flows, bank reserve balances, asset returns and valuation also affect stocks |
| Reserve requirements and prudential rules | Currency-specific funding requirements and supervision affect incentives | Rules can constrain credit while reducing currency/maturity risk; bank lending and customer choices are distinct decisions |
| Fiscal transfers, taxes, pensions, public debt | Acts as fiscal agent, not the general fiscal policymaker | Distributional compensation and budget choices belong primarily to government/Parliament; NBG cannot manufacture external goods or remove foreign supply shocks |

Sources: TRANSMISSION, LIQUIDITY, OPERATIONS, REQUIREMENTS, LAW. We do not infer that NBG controls all foreign-currency borrowing costs: its GEL policy rate and currency-specific regulatory tools are different channels.

## 2. Prices, GEL income and savings

The verified national CPI relatives compound to **31.1304%** from December 2019 to December 2024 (C, N01). Twelve-month chains are 2.4046%, 13.9397%, 9.8473%, 0.4372% and 1.8651% for 2020 through 2024 (Y2020–Y2024). These use the downloaded index vintage and source precision; present rounded values, not spurious precision.

Conditional arithmetic: spending indexed to the national CPI rises from an illustrative **GEL 1,000 to GEL 1,311.30**; unchanged GEL 1,000 has **GEL 762.60** of initial purchasing power, a **23.74%** reduction (B, N02–N04). Price growth and the reciprocal decline in purchasing power are different percentages. This is not a claim that Georgian household incomes were unchanged, that all prices rose equally, or that the annually reweighted CPI is one family's fixed physical basket.

For an unremunerated GEL balance the same deflator describes lost purchasing power. For savings earning interest, use `(1 + net nominal return)/price_factor - 1`; without actual account returns, taxes and holding periods no aggregate depositor loss is estimated. Inflation can reduce the real burden of fixed nominal debt while harming a lender's real return, but floating rates and changing incomes can offset that benefit.

**NBG's strongest response:** imported food/energy and external disruptions can raise prices; tighter policy can limit persistence and currency pass-through. Successful disinflation reduces the *rate of price increase* and need not reverse the price level. **Our defensible response:** that explanation defeats blanket blame, but does not replace an assessment of whether the policy path minimized avoidable burdens. Compare feasible alternatives under the information available then, including the cost of doing less. A causal share of the 31.13% cannot be assigned from this panel.

## 3. Who bears price pressure? What the household pilot establishes

The retained pilot validates **11,590 household-quarter records**; weighted mean total monthly expenditure is **GEL 1,092.21**, close to Geostat's published GEL 1,093 comparator (N11–N12; PILOT). The survey is a 2017 historical baseline, not a current poverty profile. Repeated DiaryID observations are not an annual longitudinal panel. Borrowing/dissaving is not earned income.

Four direct category matches cover a survey-weighted mean **24.35%** of consumption and yield a **0.251 percentage-point partial contribution** to a frozen baseline basket through December 2018. Including two approximate mappings raises coverage to **40.92%**, with a **0.659-point partial contribution**; **59.08% remains unmatched** (P01–P05). These are means of household expenditure shares, not the ratio of national spending aggregates. Food/beverages/tobacco mix categories and cannot be allocated silently. Noncash consumption is also unresolved. The annual survey basket is treated as an illustrative December baseline, not literally observed December quantities.

| Group | Expanded matched share | Partial contribution, Dec 2017–Dec 2018 |
|---|---:|---:|
| Lowest equivalized-consumption quintile | 36.17% | 0.676 pp |
| Highest quintile | 48.89% | 0.722 pp |
| Rural | 36.24% | 0.596 pp |
| Urban | 44.19% | 0.704 pp |
| At least one pension-age member | 41.73% | 0.777 pp |
| No pension-age member | 40.12% | 0.541 pp |

Source: existing `pilot2017_exposure.csv`, 2018 rows (ledger G_*). Pension age does not establish pension receipt or dependence. The omitted shares differ by group; **none of these comparisons ranks total household inflation or establishes a policy-induced distributional loss**. Existing DiaryID bootstrap intervals omit verified PSU/strata information, CPI uncertainty and mapping uncertainty; no new significance claim is made.

**Critical implication:** policy communication should show differential exposure and its limits. **Counterargument:** an incomplete research crosswalk is not evidence that Geostat or NBG concealed information. **Response:** agreed; the reform is to publish a validated bridge between household expenditure categories and CPI, with missing shares, not to accuse an institution because this project's bridge is incomplete.

## 4. Interest costs, refinancing and bank incentives

The monthly effective policy rate was **9% in January 2020**, reached **11% in March 2022**, and was **8% in December 2024** (A, N05–N07). These historical observations are not today's rate. TIBR data document interbank rates, not household loan APRs or sterilization expenses.

A two-percentage-point repricing of an unchanged **GEL 10,000** loan balance adds **GEL 200/year**, or about **GEL 16.67/month**, at full pass-through. At half pass-through the increment is GEL 100/year; at none it is zero (B, S_RATE_*). A fixed-rate contract that does not reset has no immediate mechanical repricing. Amortization, fees, refinancing, defaults and timing change actual costs. No national bill can be calculated by multiplying this example by an unverified borrower count.

Higher funding/loan rates can constrain business investment and employment; tighter policy can also prevent persistent inflation and improve savers' returns. Those indirect income effects are **E** here. A bank's net interest margin can rise or fall depending on repricing on both sides, credit losses and funding structure. “Banks profit whenever NBG raises rates” is unsupported. Collateralized refinancing can stabilize payments and lending; preferential transfers would require evidence on collateral haircuts, risk, pricing and participation, which this dataset does not supply.

The demanding question is whether burdens on repricing borrowers were proportionate to inflation/stability benefits and whether alternatives were assessed. Answering it requires anonymized balances by currency, fixed/floating status, benchmark, reset date, maturity, income and arrears—not borrower names.

## 5. Exchange rates: opposing exposures

Foreign-currency sales can support the GEL relative to a no-sale counterfactual; purchases can restrain appreciation or replenish reserves. Signs are conditional on market circumstances, expectations and sterilization. Neither action's causal exchange-rate magnitude is identified here.

Using the verified December 2024 reference **2.8068 GEL/USD**, a hypothetical **10% increase in GEL per USD** adds **GEL 28.07** to a fixed USD 100 monthly obligation and **GEL 84.20** to a fixed USD 300 monthly remittance (B, S_FX_*). Import prices need not rise one-for-one: margins, inventories, invoice currency, taxes and foreign prices matter. Net household currency exposure is debt **minus** dollar assets/income, not debt alone. A stronger GEL can favor import consumers and unhedged FX debtors while reducing GEL receipts for remittance recipients/exporters; it can also change jobs and domestic prices. These offsetting channels prevent a universal winner/loser claim.

NBG annual reports document **net purchases USD 1,278.7m in 2023** and **net sales USD 434.75m in 2024**. The components are in F2023*/F2024*. This establishes a change in net operations, not deliberate impoverishment or an estimate of how far the exchange rate moved because of policy. Gross sales in a subperiod cannot be compared directly with annual net intervention.

## 6. Reserves and sterilization: accounting before accusation

For 2024, reserves declined **USD 561.05m**. Net intervention, purchases positive, was **−USD 434.75m**. The **−USD 126.30m** difference is an **unreconciled composite**, not an identified loss or missing money (B, N08–N09).

`Closing stock − opening stock = net reserve-asset transactions + valuation + other volume/reclassification changes.`

NBG FX intervention is only a subset of transactions. Government FX, reserve income and banking-system balances can enter the reconciliation; settlement dates and accounting perimeters must match. A central bank selling dollars receives another asset or extinguishes liabilities; the gross sale is not equivalent to a fiscal expense. The policy panel contains five component fields summing to the reserve total; previous prose calling these “six components” counts the headline total as well. No data change is required.

Reserve accumulation can require domestic liquidity absorption. A defensible carry calculation would match actual interest-bearing liabilities, maturity, currency/hedging, asset returns and valuation. Multiplying all reserves by the policy rate is invalid. The illustration of a USD 100m-equivalent matched position and financing-minus-return spread of −1/0/+1 percentage point yields −1/0/+1m annual net financing cost (B, S_CARRY_*). It is a sensitivity example, **not an NBG cost estimate**. Reserve insurance can justify a financial carrying cost; low-cost reserves can still be insufficient in a crisis. Net accounting income is not social welfare.

Exact missing records: matched stock-flow bridge; government FX settlements; currency/gold valuation attribution; instrument-level outstanding and average balances, accrued interest expense, reserve investment income, FX conversions and profit-transfer rules. No claim of an existing legal breach follows from their absence in this project's panel.

## 7. Dissenting evidence and tests that could defeat the thesis

The IMF's 2025 QIPF exercise finds short-run benefits from FX intervention: its no-intervention counterfactual has peak core inflation **1.5 points** and policy interest **2.4 points** higher (D, M01–M04; IMF paragraph 29). This is serious counterevidence to a universal impoverishment claim, not household-level proof. Shock classification, omitted news shocks and reserve-buffer costs qualify the model result (paragraphs 30–39). It does not establish net welfare for each household group.

Our falsification commitments:

- Withdraw a net-harm claim if credible comparisons show inflation, employment and crisis-protection benefits exceed debt/carry/distributional costs under defensible household welfare weights.
- Withdraw a transparency-gap claim if NBG supplies a stable, complete, dated public dataset that answers it; record when it was already available and correct our retrieval failure.
- Treat similar movements in nonintervention periods, global commodity prices, foreign interest rates, fiscal shocks or country-risk news as competing explanations, not inconvenient exclusions.
- A transaction-timing event study must separate policy response to stress from policy surprise; this panel does not provide a valid instrument. No causal regression has been run for this edition.
- Structural replication should vary news versus sentiment shocks, reserve insurance, intervention persistence and household currency positions. A sign that changes under plausible restrictions must be reported as model-dependent.

## 8. Public verdict and publication limits

**Defensible now:** purchasing-power pressure under the national CPI; conditional borrower/currency exposures; verified annual FX facts; unresolved reconciliation in this research file; the case for accessible retrospective accounting and distributional reporting. **Not defensible now:** an NBG-caused aggregate household loss, a ranking of complete household inflation from the partial pilot, illicit favoritism, deliberate concealment, or a finding that a particular rate/intervention choice was welfare-inferior.

The justified political demand is to make policy choices contestable: state objectives, document tradeoffs, publish usable records with appropriate delay, and submit methods to independent challenge. Independence protects policy from short-term political orders; it does not make distributional consequences irrelevant. The [reform agenda](Reforms.md) strengthens that distinction rather than proposing parliamentary approval of individual trades or interest-rate decisions.
