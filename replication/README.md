# Reproducibility and repository validation

The study title, author and question are fixed in [study.json](../study.json) and [the research protocol](../research/PROTOCOL.md). This technical supplement is separate from the eventual main paper.

## Current checks

From the repository root, use Python 3.12 for the tested R3 environment:

```sh
python -m pip install -r replication/requirements-r3-reopen.txt
python replication/check_repository.py
python replication/check_repository.py --replicate
```

After dependency installation, the first checker command verifies all archived file hashes, the authoritative study identity, requirements/source references, local documentation links, current tests, and the unchanged archived numerical tests. The checker uses the standard library; the expanded current tests also require NumPy and reproduce the committed R3 model fits. Checks make no network requests. The `--replicate` command additionally reruns the four preserved numerical generators in a temporary copy and checks all pre-existing CSV outputs and selected numerical JSON outputs. It requires exact byte agreement except for two explicitly listed historical CSV files whose generators emit CRLF while the archived files use LF; those must agree after that sole newline normalization. It does not overwrite the archive, fetch observations, generate a manuscript or choose a new empirical design.

For a machine-readable verification record, append `--report replication/local-results/repository_validation.json`. Preserve dated historical verification records. The record reports exactly which tests were retired and what was reproduced; a historical test log is not represented as a fresh validation run.

The pre-reorganization baseline passed 33 tests. One mixed speech/editorial test was retired because the speech and briefing were withdrawn; its numerical partial-coverage assertions have a current replacement. The 32 remaining archived tests retain their original source bytes. The current suite includes structure, acquisition safety, definitions and stage-specific numerical regressions; the latest dated verification reports its count. See the [R0 checkpoint](../reports/r0_2026_11_10/README.md), [episode reproduction instructions](ACQUISITION.md) and [R1 reproduction instructions](R1.md) for separate original-source extraction tests.

## Existing numerical work

Original analytical scripts, data and locks are preserved beneath `archive/legacy/` with their internal relative paths unchanged. For example, `archive/legacy/src/reserve_foundations.py` still reads `archive/legacy/reports/reserve_foundations/`. Do not relocate individual inputs again without explicitly migrating their locks.

The current runner reproduces `reserve_foundations.py`, `paper_analysis.py`, `credit_analysis.py` and `accountability_scenarios.py` in an isolated temporary copy solely as a preservation check. These historical generators do not constitute new active research tracks. The current protocol defines what their output can support.

Source extraction/acquisition needs the archived dependency locks and permitted provider access. In a separate disposable copy of `archive/legacy/`, the reserve extraction command remains `python src/reserve_foundations.py --acquire --extract`; create `data/raw/` first on a fresh copy because the historical script assumes that parent directory exists. Its source hashes are pinned. Changed provider files are a new vintage, not a reason to overwrite an old lock. Raw PDFs and microdata remain ignored; source metadata and extracted rows remain tracked. Original lockfiles are retained as historical environments, not an untested promise that every pinned package installs on every present system.

Old whole-project editorial validators and manuscript renderers were retired to Git history. They required withdrawn prose or checked the former root tree and are not supported commands in this structure. Historical reports may quote those commands; use this document instead.

## Future acquisition conventions

Episode sources, outputs and code already occupy `data/raw/` (ignored), `data/derived/` and `src/`, with each dataset mapped to an ID in [the requirements register](../research/data_requirements.json). Keep source URL, retrieved UTC timestamp, SHA-256, observation period, publication date, units, currency, frequency, status, definition vintage and transformations. Do not overwrite archived inputs to make a new result fit an old test.

Use purchases-positive signs for active net FX acquisition and preserve both gross directions. Retain trade, settlement and disclosure times separately. Match accounting basis and period before reconciliation. Public monthly aggregates are not daily executions; future or forecast values are not realized observations. Every outcome must link to the single counterfactual in the protocol.

## R6 reserve-benefit thresholds

See [R6 reproduction](R6.md) for eight numerical tables, source checks, a deterministic figure and focused insurance/liquidity/bond-pricing tests. The [R6 checkpoint](../reports/r6_2026_11_15/README.md) separates financial hurdles from measured national costs and keeps achieved benefits unidentified. Historical test counts above describe their original checkpoints; the latest verification record reports the current suite.

## R3 reopened conditional-model experiment

See [R3 reopening reproduction](R3_REOPEN.md) for the pinned environment, original-source calibration checks, independent QR/matrix verification, resampling and diagnostic figure. The [decision report](../reports/r3_reopen_2026_11_16/README.md) withholds a preferred counterfactual because the model fails its registered robustness requirement. Reproducing a rejected path does not authorize presenting it as a validated estimate.
