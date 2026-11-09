# Reproducibility and repository validation

The study title, author and question are fixed in [study.json](../study.json) and [the research protocol](../research/PROTOCOL.md). This technical supplement is separate from the eventual main paper.

## Current checks

From the repository root, with Python 3.11 or later:

```sh
python replication/check_repository.py
python replication/check_repository.py --replicate
```

The first command verifies all archived file hashes, the authoritative study identity, requirements/source references, local documentation links, current structure tests, and the unchanged archived numerical tests. It uses only the Python standard library and makes no network requests. The second additionally reruns the four preserved numerical generators in a temporary copy and checks all pre-existing CSV outputs and selected numerical JSON outputs. It requires exact byte agreement except for two explicitly listed historical CSV files whose generators emit CRLF while the archived files use LF; those must agree after that sole newline normalization. It does not overwrite the archive, fetch observations, generate a manuscript or estimate new effects.

For a machine-readable verification record, append `--report docs/reorganization_validation.json`. The record reports exactly which tests were retired and what was reproduced; a historical test log is not represented as a fresh validation run.

The pre-reorganization baseline passed 33 tests. One mixed speech/editorial test was retired because the speech and briefing were withdrawn; its numerical partial-coverage assertions have a current replacement. The 32 remaining archived tests retain their original source bytes. Four current tests cover study consistency, requirements completeness, archive integrity and that transferred numerical check.

## Existing numerical work

Original analytical scripts, data and locks are preserved beneath `archive/legacy/` with their internal relative paths unchanged. For example, `archive/legacy/src/reserve_foundations.py` still reads `archive/legacy/reports/reserve_foundations/`. Do not relocate individual inputs again without explicitly migrating their locks.

The current runner reproduces `reserve_foundations.py`, `paper_analysis.py`, `credit_analysis.py` and `accountability_scenarios.py` in an isolated temporary copy solely as a preservation check. These historical generators do not constitute new active research tracks. The current protocol defines what their output can support.

Source extraction/acquisition needs the archived dependency locks and permitted provider access. In a separate disposable copy of `archive/legacy/`, the reserve extraction command remains `python src/reserve_foundations.py --acquire --extract`; create `data/raw/` first on a fresh copy because the historical script assumes that parent directory exists. Its source hashes are pinned. Changed provider files are a new vintage, not a reason to overwrite an old lock. Raw PDFs and microdata remain ignored; source metadata and extracted rows remain tracked. Original lockfiles are retained as historical environments, not an untested promise that every pinned package installs on every present system.

Old whole-project editorial validators and manuscript renderers were retired to Git history. They required withdrawn prose or checked the former root tree and are not supported commands in this structure. Historical reports may quote those commands; use this document instead.

## Future acquisition conventions

New episode work should use a dedicated `data/raw/` (ignored), `data/derived/` and `src/` when acquisition is authorized, with each dataset mapped to an ID in [the requirements register](../research/data_requirements.json). These are reserved locations, not populated episode datasets. Keep source URL, retrieved UTC timestamp, SHA-256, observation period, publication date, units, currency, frequency, status, definition vintage and transformations. Do not overwrite archived inputs to make a new result fit an old test.

Use purchases-positive signs for active net FX acquisition and preserve both gross directions. Retain trade, settlement and disclosure times separately. Match accounting basis and period before reconciliation. Public monthly aggregates are not daily executions; future or forecast values are not realized observations. Every outcome must link to the single counterfactual in the protocol.
