# Georgia monetary policy and household welfare: Phase 1

## Public accountability investigation — 8 November 2026

The complete [accountability edition](reports/accountability/README.md) contains the [evidence dossier](reports/accountability/Dossier.md), [Georgian public speech](reports/accountability/Speech_ka.md), [claim-by-claim opposition briefing](reports/accountability/Fact_check.md), [scoreboard](reports/accountability/Scoreboard.md), [quantitative illustrations](reports/accountability/Illustrations.md), and [reform agenda](reports/accountability/Reforms.md). It investigates costs, benefits and disclosure without claiming an identified net NBG-caused household loss. All previous research below is preserved.

Reproduce the new calculations **offline, without downloading the household data again**: `python src/accountability_scenarios.py`. Run `python src/validate_accountability.py` for calculations, preservation checks, all tests and the speech-length check. Supplemental current official sources can be refreshed separately with `python src/accountability_sources.py`; review any changed source vintage before revising claims.

## NBG policy data, 2020–2024

The [monthly policy panel](reports/nbg_policy_monthly_2020_2024.csv), [source manifest](reports/nbg_source_manifest.json), [series dictionary](reports/nbg_series_dictionary.csv), and [IMF benchmark and identification memorandum](reports/NBG_Policy_Dataset_and_IMF_Benchmark.md) record observed policy-rate, reserve, exchange-rate, interbank-rate, CPI and quarterly external data. Intervention transaction fields remain blank where no complete series was verified. Reproduce with `python src/nbg_policy.py` after installing `requirements.lock`; tests are `python -m unittest discover -s tests -v`. Raw provider files remain ignored.

The Phase 1 assessment, eight requested components, literature review, go/no-go decisions and Phase 2 handoff are in [`phase1/Phase1_Research_Assessment.md`](phase1/Phase1_Research_Assessment.md). The bibliography is in `phase1/references.bib`; `phase1/access_checks.json` and `phase1/audit_log.md` document source access and limitations. The complete downloadable package is [`phase1/Georgia_Phase1_Package.zip`](phase1/Georgia_Phase1_Package.zip).

Status: Phase 2 recovery audit completed. Eleven of thirteen GEOSTAT release assets pass hash and structural checks; the 2020 and 2023 release ZIPs are hash-matched but structurally malformed and are excluded. Descriptive household-price analysis may proceed on validated years. Causal NBG intervention identification remains a separate unresolved track.
## Phase 2 validation checkpoint

See [the 2017 pilot report](reports/Pilot2017_Methods_and_Results.md), [the validation checkpoint](reports/Phase2_Validation_Report.md), and [the interruption-recovery audit](reports/recovery_audit_2026-11-08.md). Raw provider data are not distributed. The pilot calculates only a matched-category fixed-basket contribution; 59.1% of weighted consumption is unmatched.

Reproduce with CPython 3.12:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
python src/release_download.py
python src/release_validation.py
python src/pilot2017.py
python -m unittest discover -s tests -v
```
