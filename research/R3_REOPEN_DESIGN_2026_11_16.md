# R3 reopening: registered conditional-model experiment, 16 November 2026

This is a dated amendment under R0, before fitting or simulating the candidate below. Parent: `30ebe6519f72114f03f11b2d35a408b888d5a3b7`. The fixed study question, January 2025–September 2026 window, December 2024 opening, public-evidence restriction and original R3 findings remain unchanged. Historical outcomes have already been inspected. This is not outcome-blind preregistration. R7 and manuscript drafting are paused.

## Why reopen and which approach

Newly retrieved primary evidence is Adler, Lisack and Mano, IMF WP/15/130, Table A11 (physical PDF p41): monthly nominal bilateral exchange-rate responses with three intervention lags. This supplies an external magnitude AND decay specification, which the earlier inverse-duration illustration lacked. The main candidate uses column 4 (excluding de jure pegs, parsimonious controls). Columns 1, 7 and 10 are predefined calibration sensitivities. None includes a verified modern Georgian purchase-rule coefficient. The study normalizes a balance-sheet FXI proxy by HP-filtered trend USD GDP, whereas we have transaction data. Transportability is an assumption, not an estimated fact.

The Georgian QIPF application is economically broader, but the accessible IMF 2025 report and NBG article do not provide the complete Georgian executable system, parameter vector and shock decomposition. The generic Chen et al. model does not establish that calibration. No claim is made that no public code exists anywhere. Event/IV/threshold identification still lacks exogenous executed-order variation. A large unrestricted VAR on 60 pre-episode months would not cure that defect.

The executable candidate is a small simultaneous-policy model: an externally calibrated exchange-rate equation, a lagged Georgian interest-rate rule, and an endogenous FX-intervention rule. It is a conditional structural simulation, not an IV causal estimate. Private flow/portfolio adjustment is represented by the price equation and innovations, not by holding observed remittances or trade fixed. There is no full welfare model.

## Variables, calibration and fitting

Monthly y = 100 log(GEL/USD); i = end-month NBG policy rate in percentage points; q = net NBG market purchases as a percentage of an annual USD GDP normalization. Larger y means depreciation. Negate ALL four published FXI coefficients, but not the autoregressive coefficient, to convert the paper's appreciation convention. The contemporaneous coefficient is not multiplied by twelve. Use source nominal columns only; no mixing real or effective exchange rates.

Pre-period: January 2020–December 2024; three intervention lags imply fitting begins April 2020. GDP denominators: World Bank annual nominal USD GDP for pre-period years; freeze observed 2024 GDP throughout the evaluation window. A second normalization uses the repository's rounded 2025 USD 38.1bn for both evaluation years. This is a scale sensitivity, not monthly GDP interpolation or a no-purchases GDP forecast. Unlike the source paper this is not an HP trend; that mismatch must remain explicit.

Exogenous regressors: same-month broad-dollar log change and VIX level from the existing daily series aggregated over available observations. No missing daily observation is invented. These are externally observed shocks/conditions, not instruments. Policy and fiscal news not captured remain in the recovered innovations.

Equations:

1. `i[t] = Xi[t] ai + ui[t]`, with Xi = intercept, lagged i, lagged monthly change in y, lagged q, dollar change and VIX. No same-month FX response in this equation: the contemporaneous interest innovation is assumed predetermined relative to the FX-market innovation.
2. `y[t] = rho*y[t-1] + sum(b[j]*q[t-j], j=0..3) + Zy[t] ay + uy[t]`, with Zy = intercept, current i, lagged i, dollar change, VIX. rho and all four b's are external; the nuisance coefficients are OLS estimates conditional on their validity and interest-innovation exogeneity.
3. `q[t] = Xq[t] aq + theta*(y[t]-y[t-1]) + uq[t]`, with Xq = Xi plus current i. Identify theta from the orthogonality of uy and uq: residualize q, monthly y change and uy on Xq; theta is Cov(uy_res,q_res)/Cov(uy_res,dy_res). Fit aq to q−theta*dy. This restriction is part of the model, not an independently justified excluded instrument. No sign is imposed on theta, rate feedback, or the final FX gap.

Same latent innovations and external regressors in both worlds; policy rules respond to counterfactual lags. Baseline reconstruction with recovered innovations is an algebra check, not validation. No 2025–2026 observations enter fitting. Zero and opposite-sign FXI kernels, with primary rho, are diagnostic challengers, NOT literature-supported parameter bounds. Better predictive performance cannot select a causal sign.

## Intervention, information and accounting closure

Adopt a disclosed minimum-gross/one-way-month convention: positive observed net market intervention is purchases, negative is sales. Actual gross purchases remain unknown. This is a conditional treatment definition and does not establish that missing two-way flows were zero.

Initialize observed histories through December 2024. In the counterfactual, solve the simultaneous equations with the purchase restriction q<=0. If the unconstrained rule calls for a purchase, set q=0 and recompute y; if it calls for a sale, retain the rule and its recovered innovation and solve jointly. Do not fix March 2026 sales to their actual amount. Require 1−b0*theta>0 for a unique correctly oriented constrained solution.

The suspension is unexpected at the start. Agents follow the estimated adaptive propagation; there is no independently modeled forward-looking announcement or reserve-confidence premium. This is a restrictive information assumption. Changes in interest rates follow the same rule. Liquidity provision/sterilization is assumed elastic at that rate; no scarce collateral or funding limit is invented. The FX financing cash difference is reported separately; it is not an estimated funding cost. These assumptions do not identify a general-equilibrium path under other expectations or reserve-risk responses.

For a diagnostic reserve bridge, treat the changed intervention positions as USD assets earning the monthly observed SOFR proxy, with common other reserve transactions/valuation shocks. Carry the incremental reserve stock recursively, never substitute stock changes for intervention. Preserve actual gold and SDR holdings. Reject the candidate if counterfactual gross reserves or the non-gold/non-SDR residual becomes negative. Other encumbrances remain unknown. This bridge is conditional, not a complete usable-reserve account.

## Validation and release decision, fixed before fitting

1. Source extraction, units, lag initialization, no-purchase constraint, contemporaneous clearing, baseline reconstruction, zero-treatment recovery and reserve arithmetic must pass numerical tests.
2. Pre-episode pseudo-out-of-sample validation: expanding fits through December 2022, then 24 one-step predictions for January 2023–December 2024. Use the actual external conditions for that month but predict intervention and interest jointly, with innovations zero. This is a conditional hindcast, not a real-time forecast. Compare exchange-rate log RMSE with a no-change random walk. Primary RMSE must be no more than 1.20 times random walk. The 20% tolerance is a declared practical falsification threshold, not a statistical critical value. Show all other specifications; do not switch the primary after outcomes are known.
3. Report full-sample residual lag-one correlations and policy-rule support. Reject release if same-month clearing is singular/misoriented or the free-regime deterministic state transition has a root >=1 in modulus. Report extrapolation beyond pre-period policy rates and sales; do not conceal it by clipping them.
4. Use moving-block pairs resampling of pre-period equation rows (block length six, 199 replicates, seed 20261116) to assess conditional coefficient instability. Hold external calibration fixed; record failed/unstable draws rather than deleting them without counts. Percentiles, if computed, are conditional sampling summaries, not causal confidence bounds or probabilities on calibration choices. If fewer than 90% of draws produce numerically admissible, stable, reserve-feasible paths, withhold a preferred path.
5. Even passed numerical/forecast tests do not establish transportability, shock independence, gross treatment or expectations invariance. A conditional path can be released only with those assumptions visibly attached. If the primary fails, preserve candidate outputs as rejected diagnostics and withhold a preferred estimate and an empirical range. Do not relabel an arbitrary path as an answer to the fixed question.

Outputs: source/calibration register, monthly modeling panel, external impulse-response reproduction, coefficients, pre-period validation predictions, all candidate paths/terminal gaps, endogenous sales/rates and conditional reserve bridge, resampling diagnostics, tests, figure, and a direct decision report. Monthly and terminal gap = 100*(E_actual/E_candidate−1); average = unweighted monthly average. Also report the distinct quote-decline percentage. No manuscript or R7 work in this experiment.
