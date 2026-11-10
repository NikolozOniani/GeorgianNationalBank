# The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author: Nikoloz Oniani**

**Research question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

**Scope:** One intervention episode, one economic counterfactual, and its consequences.

This is one academic economics project. The [research protocol](research/PROTOCOL.md) is authoritative. It studies the 2025–2026 reserve-accumulation purchase episode against a specified no-purchases counterfactual. Exact execution boundaries and the last jointly observed period must be established before estimation. The year 2026 is incomplete at the source-review cutoff of 8 November 2026.

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

## Evidence status

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
python replication/check_repository.py
```

See [the reorganization record](docs/REORGANIZATION.md) for preservation and verification details.
