# The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author: Nikoloz Oniani**

**Research question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

**Scope:** One intervention episode, one economic counterfactual, and its consequences.

This study evaluates the NBG's January 2025–September 2026 purchases under three calibrated economic scenarios. Both the observed episode and the no-purchases alternative begin with the December 2024 balance sheet. The [protocol](research/PROTOCOL.md) specifies the assumptions and which conclusions each calculation supports. The [roadmap](research/ROADMAP.md) starts with the monthly lari and reserve paths.

## Read the project

| Document | Purpose |
|---|---|
| [Research protocol](research/PROTOCOL.md) | Fixed question, treatment, counterfactual, estimands, admissible inference and decision gates |
| [Authoritative completion roadmap](research/ROADMAP.md) | Independent evidence assessment; ordered stages, dependencies, original quantitative findings and completion criteria |
| [R0 registration](research/R0_REGISTRATION.md) and [verification](reports/r0_2026_11_10/README.md) | Frozen experiment, timing, economic accounts, admissible methods, open decisions and reproducibility evidence |
| [R1 accounting findings](reports/r1_2026_11_10/README.md) and [requirement status](research/R1_STATUS.md) | Transaction, reserve and liquidity ledgers; gross-flow bounds, partial 2025 bridge and unresolved G1 evidence |
| [Data requirements and acquisition order](research/DATA_REQUIREMENTS.md) | What exists, what is missing, public access versus requests, and what each gap prevents |
| [Machine-readable requirements](research/data_requirements.json) | Variables, units, frequencies, periods, sources, validation and priority for each dataset |
| [Primary-source register](research/SOURCES.md) | Exact source locations and the level of access actually checked |
| [NBG request specification](research/NBG_REQUEST_SPECIFICATION.md) | Precisely defined missing records and confidentiality-preserving alternatives; not sent |
| [Existing evidence catalogue](evidence/README.md) | Reusable historical measurements and their limitations |
| [Manuscript structure](manuscript/STRUCTURE.md) | One eventual paper, with an economic argument and evidence requirements; no new draft |
| [Replication instructions](replication/README.md) | Separate technical documentation and integrity checks |

## R7 joint findings

The [quantitative synthesis](reports/r7_synthesis/README.md) brings together the currency, household, financing and reserve-insurance accounts. Without purchases, the central September 2026 lari buys 10.58% more USD. The additional reserves close a conditional twelve-month public-payment gap of USD 188.60m, rising to USD 2,631.83m under the import-scaled pandemic sales policy. At an assumed 1% annual net external opportunity cost and a five-year first-crisis loss of USD 3.81bn, the central break-even annual risk reduction is 2.55 percentage points from a 10% baseline. Actual risk reduction and the national welfare sign remain open. [Joint table](reports/r7_synthesis/joint_results.csv) · [Assumptions and replication](reports/r7_synthesis/METHODS.md)

The [marginal reserve frontier](reports/r7_frontier/README.md) prices 35 proportional purchase policies. At September 2026, USD 4.841bn gross covers the twelve-month public schedule and import-scaled sales replay. The USD 5bn policy implies 2.4694 GEL/USD centrally. Higher accumulation provided additional coverage at earlier month-ends and under more restrictive asset access.

## Evidence status

**Research direction, 24 November 2026.** The [scenario calibrations and acceptance criteria](research/PROTOCOL.md) cover FX impact and persistence, monetary policy, inflation and reserve services. The [earlier R3 experiment](reports/r3_reopen_2026_11_16/README.md) remains rejected under its original rule. The separate [historical reserve tests](reports/buffer_validation/README.md) support conditional stress comparisons. The [fixed-rate counterfactual results](reports/r3_fixed_rate/README.md) now cover all 21 months. The central calibration gives 2.3481 GEL/USD in September 2026 versus 2.6051 observed, or 2.3987 with diminishing impact. With [endogenous policy and inflation](reports/r3_policy_feedback/README.md), the central September path reaches 2.3558 GEL/USD, 5.40% annual headline inflation and a 7.98% policy rate. A separate 100 bp rate shock produces a smaller inflation response than the Georgian IMF benchmark.

The [9 November acquisition results](reports/acquisition_2026_11_09/README.md) now provide actual 2025–2026 monthly intervention observations, daily exchange rates, reserve and liquidity records, external flows, audited 2025 interest accounts and IMF ARA benchmarks. See the [current requirement status](research/ACQUISITION_STATUS.md) and [replication/manual-file instructions](replication/ACQUISITION.md). The remaining text below describes the preserved historical foundation; it is not the current acquisition inventory.

The verified supporting data include a 60-month 2020–2024 policy/reserve panel, two annual intervention benchmarks, five years of audited interest accounts, and an arithmetic reconstruction of the IMF's published 2022–2023 ARA components. They establish useful accounting foundations. They do not supply a verified 2025–2026 intervention event series or identify the exchange rate without purchases.

The [completion roadmap](research/ROADMAP.md) is the authoritative sequence from the existing evidence to the final paper. It distinguishes episode measurement, counterfactual identification, household consequences, marginal reserve costs and insurance benefits. R0 registers the experiment and verifies reproduction. R1 adds 17 accounting tables, three official source documents, additional extraction from existing workbooks/audited accounts and an explicit discrepancy register. The registered window has USD 5,803.15 million net purchases; this does not identify gross purchases or their exchange-rate effect. Full G1 remains open because gross executions, applicable rule parameters and a complete stock-flow decomposition are missing. See [R1 replication](replication/R1.md). No causal estimates, manuscript text, optimum or net economic loss are claimed.

## Repository boundaries

- `research/`: the single protocol, data-acquisition specifications and primary-source register.
- `evidence/`: an index of reusable observations and calculations; original files remain in one preserved location.
- `manuscript/`: the eventual paper's structure only. Economic methods belong in the paper; software and project administration belong in `replication/` and `docs/`.
- `replication/` and `tests/`: current checks and instructions.
- `archive/legacy/`: preserved historical data, provenance, analytical code and supporting reports. Earlier directions have no authority over this study.
- `docs/`: the reorganization record.

Superseded manuscripts, speeches and their publishing scripts have been removed from the checked-out project and remain recoverable from Git history. Numerical evidence and analytical code have been retained unchanged. The [archive register](archive/README.md) records every original file's disposition and hash. The GEOSTAT release is unchanged and belongs to the historical archive, not the active research agenda.

Run the offline integrity and numerical tests with:

```sh
python -m pip install -r replication/requirements-r3-reopen.txt
python replication/check_repository.py
```

See [the reorganization record](docs/REORGANIZATION.md) for preservation and verification details.

[R2 reserve adequacy, liquidity and IMF benchmark results](reports/r2_2026_11_11/README.md)

[R3 no-purchases exchange-rate design decision](reports/r3_2026_11_12/README.md)

[R3 reopened: quantitative model, validation failure and rejected paths](reports/r3_reopen_2026_11_16/README.md)

[R4 reserve income, funding accounts and conditional carry](reports/r4_2026_11_12/README.md)

[R5 household basket and foreign-transfer exposures](reports/r5_2026_11_13/README.md)

[R6 reserve liquidity, financing and insurance thresholds](reports/r6_2026_11_15/README.md)

[R3 standalone Georgian monetary-policy response and held-out decision tests](reports/r3_rate_rule/README.md)

[R3 Georgian purchase impact, persistence and selection tests](reports/r3_fx_response/README.md)
