# The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

**Author: Nikoloz Oniani**

**Research question:** Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

**Scope:** One intervention episode, one economic counterfactual, and its consequences.

This is one academic economics project. The [research protocol](research/PROTOCOL.md) is authoritative. It studies the 2025–2026 reserve-accumulation purchase episode against a specified no-purchases counterfactual. Exact execution boundaries and the last jointly observed period must be established before estimation. The year 2026 is incomplete at the source-review cutoff of 8 November 2026.

## Read the project

| Document | Purpose |
|---|---|
| [Research protocol](research/PROTOCOL.md) | Fixed question, treatment, counterfactual, estimands, admissible inference and decision gates |
| [Data requirements and acquisition order](research/DATA_REQUIREMENTS.md) | What exists, what is missing, public access versus requests, and what each gap prevents |
| [Machine-readable requirements](research/data_requirements.json) | Variables, units, frequencies, periods, sources, validation and priority for each dataset |
| [Primary-source register](research/SOURCES.md) | Exact source locations and the level of access actually checked |
| [NBG request specification](research/NBG_REQUEST_SPECIFICATION.md) | Precisely defined missing records and confidentiality-preserving alternatives; not sent |
| [Existing evidence catalogue](evidence/README.md) | Reusable historical measurements and their limitations |
| [Manuscript structure](manuscript/STRUCTURE.md) | One eventual paper, with an economic argument and evidence requirements; no new draft |
| [Replication instructions](replication/README.md) | Separate technical documentation and integrity checks |

## Evidence status

The verified supporting data include a 60-month 2020–2024 policy/reserve panel, two annual intervention benchmarks, five years of audited interest accounts, and an arithmetic reconstruction of the IMF's published 2022–2023 ARA components. They establish useful accounting foundations. They do not supply a verified 2025–2026 intervention event series or identify the exchange rate without purchases.

The immediate priorities are executed purchase/sale records and market prices; the intervention decision rule and concurrent FX flows; then matched reserve-financing accounts and usable-reserve needs. The [data assessment](research/DATA_REQUIREMENTS.md) states precisely which conclusions require which evidence. No optimum or net economic loss is assumed.

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
