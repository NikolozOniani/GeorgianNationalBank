# Research protocol

**Study:** The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author:** Nikoloz Oniani

**Fixed research question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

**Fixed scope:** One intervention episode, one economic counterfactual, and its consequences.

This protocol supersedes every earlier study direction, manuscript plan and research handoff. It does not announce empirical findings. Definitions below specify what the eventual findings must measure.

## 1. Episode and population of transactions

The acquisition window is January 2025–December 2026, covering the recent reserve-accumulation purchase episode. The end date is an acquisition target, not a claim that all 2026 observations exist. At the 8 November 2026 source-review cutoff, use only observations already executed and disclosed. Retain earlier data for estimation, diagnostics and comparison, not as additional intervention episodes to be evaluated.

Before estimating outcomes, register the episode's first executed purchase, terminal observation, any policy-rule changes, and whether the accumulation program continued at the cutoff. Choose boundaries from dated transactions and documented policy, never from a favorable exchange-rate outcome. A month of net sales does not automatically split the episode or justify dropping that month. Do not identify the beginning from the first positive reserve-stock change.

Treatment is NBG's executed gross foreign-currency purchases from the market through BMatch and auctions during the episode. Record gross sales separately, alongside purchase currency, amount, price, instrument, trade date, settlement date and disclosure date. Government FX conversions and transactions that only reallocate an existing reserve portfolio are separate accounting categories. Check whether options, forwards or swaps were used before deciding their treatment; do not assume these are zero.

The existing annual intervention benchmark uses **net sales positive**. The active acquisition convention will be **purchases positive**, with nonnegative gross purchases and gross sales and signed net purchases equal to purchases minus sales. Preserve the archived convention and convert it explicitly in any future join.

## 2. One economic counterfactual

The counterfactual removes the episode's discretionary market purchases. It starts from the same pre-episode reserve stock, external obligations and information. Exogenous global and domestic shocks are the same. Government financing and FX transactions that do not result from the purchase decision are the same. Private capital flows, expectations, prices and monetary liquidity respond through the specified economic model; holding all of them at their observed values would suppress part of the effect being studied.

Retain the same nonpurchase policy rules and institutional constraints, including the policy-rate reaction rule, liquidity-management objective and emergency-sales rule. Recompute their outcomes where they respond endogenously; do not assume that the observed refinancing path, every observed sale and the observed exchange rate can all remain feasible after purchases are removed. An interpretation conditional on the observed interest-rate path must be labeled as such and its feasibility checked. Parameter sensitivity tests apply to this same counterfactual; they do not introduce a collection of alternative policy proposals.

For the exchange rate, let E be GEL per USD. The effect is 100 × (E observed / E without purchases − 1), with positive values indicating a weaker lari than in the counterfactual. Reduced appreciation can coexist with observed appreciation. Report the endpoint and the time profile, uncertainty and the distinction between immediate price impact and persistent effects. Report NEER as a secondary robustness outcome after verifying its direction and weights.

For reserves and costs, compare the complete observed and counterfactual balance-sheet paths, not only the terminal difference in gross reserves. Preserve valuation, currency composition, accrued income, settlement timing and contractual obligations in both paths.

## 3. Identification requirements

Purchases can respond to appreciation pressure, private inflows and NBG information. A positive association between purchases and appreciation can therefore have the opposite sign from the policy's causal effect. Neither stable observed exchange rates nor reserve growth establishes prevented appreciation.

The preferred empirical evidence combines dated executions, pre-execution quotes/order flow and a documented source of purchase variation that is independent of concurrent exchange-rate shocks. A rules-based intervention is not automatically exogenous: a trigger based on the exchange rate or order flow is endogenous. A credible design must document the assignment mechanism, anticipation, manipulation risk, exclusion restriction and common support. No such instrument is currently verified.

Intraday event analysis can measure local market responses only if announcement, order and execution times are distinguished and concurrent news and intervention expectations are addressed. It cannot by itself justify summing local responses into a persistent two-year counterfactual. Monthly public aggregates support episode accounting; a short 2025–2026 sample does not support an unrestricted causal VAR. A longer pre-period must address changes in trading arrangements, market depth and policy rules.

If quasi-experimental variation is unavailable, estimate the same counterfactual only within a disclosed structural framework with independently estimated or externally justified elasticities, a policy reaction function, expectations and capital flows. Report identification sets or sensitivity ranges when parameters are weakly identified. Predictions must be tested on held-out periods and placebo dates, and against observed market volumes and feasible reserve paths. A synthetic comparison country is admissible only after ruling out its own relevant interventions, common-shock differences and contamination; no automatic donor country is designated.

## 4. Economic cost and benefit accounts

Maintain three connected accounts: central-bank financial income/cost; the consolidated public-sector account; and domestic economic welfare. A payment between domestic residents can be a transfer rather than a net national resource loss. Exchange-rate valuation of public or private assets is not automatically a welfare cost. State the numeraire, price base, horizon and discounting before aggregation.

Measured reserve interest, fees and operation expenses are inputs. Incremental reserve financing may take the form of additional remunerated liabilities, lower outstanding refinancing assets and foregone lending income, or changes in nonremunerated base money. Use currency- and duration-matched average balances and rates. Policy rate multiplied by the reserve stock is not a measured financing cost. Domestic opportunity costs require a feasible alternative use of the resources and its risk-adjusted return.

Benefits to evaluate are the marginal reduction in external liquidity shortfalls and crisis losses, market-disruption risk and external financing costs attributable to the additional usable reserves. Deduct encumbrances and predetermined drains; do not assume all gross reserves can be spent. Calibrate private-bank FX buffers separately and test their accessibility in stress. ARA is a risk benchmark, not an estimated welfare optimum. An increase in ARA coverage cannot alone establish that the purchases were economically justified.

Consequences of the counterfactual exchange-rate path can include changes in external purchasing capacity, export and import margins, currency-mismatched external balance sheets and income from abroad. Quantify only the channels for which exposures and behavioral responses can be defended. Do not sum importer gains and exporter losses into national welfare without an internally consistent valuation and incidence framework. This is not a separate household-credit or general-inflation study.

Prevent double counting between crisis insurance, lower sovereign spreads and an FX liquidity buffer. A spread decrease is not a benefit caused by reserves until competing fiscal, global-rate and country-risk explanations have been assessed. The absence of a crisis does not measure insurance benefits.

## 5. Cangul and Abel benchmark

Use the authors' specific version, parameters, data vintages, normalization, objective, constraints, simulation horizon and replication materials. Preserve the existing algebraic audit as a limited supporting result. The printed derivative concern is not proof of an error in unpublished code; the isolated loss-channel calculation is not a replication of total utility or of the recommended reserve target.

Evaluate the benchmark's crisis probability, loss severity, reserve-return assumptions, sovereign-spread mechanism, dollarization mechanism and FX-buffer overlap against the episode data. Reproduce the reported optimum before changing parameters. Failure to reproduce must be reported as an unresolved replication gap, not as proof that the recommendation is false. Benefits and costs must refer to the same horizon and resource constraint. The target level is relevant only insofar as it helps evaluate the extra reserves accumulated in the one episode.

## 6. Evidence gates and final argument

| Gate | Required evidence | Conclusion permitted |
|---|---|---|
| G1: episode accounting | Purchases/sales by instrument reconciled to monthly/annual totals; execution/settlement/disclosure separated; explicit unknowns | How much was purchased and how gross reserves changed |
| G2: counterfactual exchange rate | Valid identifying variation or an explicit, testable structural model; concurrent flows and policy response addressed | Estimated prevented appreciation, with appropriate uncertainty or conditional bounds |
| G3: incremental costs | Reserve returns and funding changes matched across both paths; stock-flow bridge and exposures reconciled | Measured components and separately labeled conditional incremental costs |
| G4: reserve benefits | Usable reserves, drains, external risks, model replication/sensitivity and no double counting | Conditional insurance/financing benefits and break-even conditions |
| G5: joint assessment | G1–G4 on one horizon and numeraire, distribution/transfers handled, uncertainty propagated | Whether the episode's costs were justified within the identified assumptions |

If G2 fails, the paper cannot answer the first clause with a precise causal number. If G3 or G4 fails, it cannot claim a net welfare verdict. Report which parts are identified and which depend on assumptions. A zero effect, net benefit, net cost or inconclusive result is acceptable. Gates govern claim strength, not the choice of a preferred conclusion.

The [authoritative completion roadmap](ROADMAP.md) sequences the evidence gates, dependencies and deliverables under this protocol. The [requirements assessment](DATA_REQUIREMENTS.md), [source register](SOURCES.md) and [request specification](NBG_REQUEST_SPECIFICATION.md) supply its implementation specifications. The [manuscript structure](../manuscript/STRUCTURE.md) is the only active manuscript outline.
