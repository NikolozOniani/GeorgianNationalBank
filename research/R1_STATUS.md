# R1 completion evidence and unresolved requirements

**Date:** 10 November 2026. **Baseline:** `92f05d27ab980c2f471e9ca24ab64c2884283860`.

R0 remains complete. This R1 checkpoint implements the [roadmap](ROADMAP.md) using the frozen January 2025–September 2026 evaluation window. **R1/G1 is partial**, not passed. The [numerical report](../reports/r1_2026_11_10/README.md) and [catalogue](../reports/r1_2026_11_10/catalogue.json) are the acceptance evidence for the independently verifiable portion.

| Requirement | Work completed or verified | Remaining evidence / consequence |
|---|---|---|
| D01, P0: executed interventions | 105 native monthly instrument-field records; 21 monthly gross-flow lower bounds; annual/net reconciliation retained; historical auction timing differences quantified | Gross BMatch sides, timestamps, prices, actual first trade and settlement/disclosure history are not retrieved. Net flows cannot define removal of gross purchases. |
| D02, P0: FX market | Existing monthly bank transactions retained; February 2026 aggregate quarantined | Pre-order bids/asks, depth, anonymous order flow and execution history remain missing. No high-frequency design is available. |
| D03, P0: exchange rates | Existing daily rates and index series retained; official fixing clock separated from valid dates | Actual historical first releases and pre-order quotes; remaining NEER gap and index-weight vintages. General fixing methodology does not solve event timing. |
| D04, P0: operating regime | Two official operational PDFs acquired; dated August 2025 release extracted; rules/timing register and timeline committed | Historical qualitative descriptions do not establish the episode's thresholds, lookbacks, caps, overrides or version changes. No exogenous rule variation identified. |
| D05, P0: government FX | Approximate annual 2025 government receipts and FX expenditure extracted; conditional annual bridge | Exact monthly/daily conversion and settlement records, currencies, channels and coverage relative to BOP. Debt stocks and annual narrative amounts cannot substitute. |
| D06, P0: competing private flows | Detailed DCS extraction, 22 dates × 35 series, definitions and monetary identities checked; existing external-flow series preserved | Nonresident/customer decomposition, daily FX demand and historical information vintages. DCS stock differences are not transactions. |
| D07, P0: external controls | Existing SOFR, VIX, dollar and partner-FX observations preserved | Dated news, timestamp alignment and comparison-country intervention regimes remain unassembled. No donor or instrument validated. |
| D08, P1: reserve bridge | Six quarterly and 21 monthly bridges; 2025 approximate government breakdown; gold endpoint price calculation and source concordance | Gold transactions; currency/securities valuation; exact government and income flows; other volume changes/revisions. End-2024 gold mismatch remains quantified. |
| D09, P1: liquidity | 22 complete signed CBS identities; 286 instrument-position cells; monthly changes; two audited NBG debt-security reconciliations | 2025 daily history, monthly/daily average remunerated exposures and rates, transaction-level offsets and matched financing. No marginal allocation estimated. |
| D10, P1: rates/Treasury | 126 Treasury records extracted with native value dates, separate discount/yield definitions, issuance components and original prices; prior policy/interbank series retained | Actual auction trade times where absent, operation terms and historical information sets. Domestic Treasury rates are not external funding spreads. |

The public-data ledger deliverables exist. The full requirements do not: **no D01–D10 row is claimed wholly complete**. No R2 model replication, R3 causal estimation, R4 marginal-cost allocation or manuscript drafting was performed here.

## Ordered work to finish R1

1. **Treatment and rules:** pursue the existing anonymized NBG execution/rule records listed in [the follow-up specification](R1_RECORDS_REQUEST.md). Confirm gross purchase/sale directions and exact program boundaries before choosing an event design. Anonymous daily totals are a fallback for treatment measurement, not an adequate replacement for pre-order information.
2. **Matched accounting:** obtain exact government and reserve movements at monthly frequency plus revision/valuation conventions. Resolve the USD 0.402 million end-2024 gold disagreement without rewriting either source vintage. Validate approximate 2025 government entries before treating the remaining residual as a measured component.
3. **Market and liquidity history:** investigate licensed/public quote history and obtain existing daily NBG operations and average balances. Record any access restriction actually communicated by its custodian. Do not infer legal confidentiality from unsuccessful public retrieval.
4. **Close each qualification:** preserve raw observations, explain the actual correction or maintain an exclusion with its analytical consequence. Full G1 requires gross treatment measurement and documented accounting residual treatment; successfully running the software is insufficient.

The [public-access log](R1_PUBLIC_ACCESS.md) records checks already completed. The proposed follow-up is unsent. Continuing independent R2 inputs does not make the missing R1 evidence available or authorize causal estimation.
