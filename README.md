# Georgia monetary policy and household welfare: Phase 1

The Phase 1 assessment, eight requested components, literature review, go/no-go decisions and Phase 2 handoff are in [`phase1/Phase1_Research_Assessment.md`](phase1/Phase1_Research_Assessment.md). The bibliography is in `phase1/references.bib`; `phase1/access_checks.json` and `phase1/audit_log.md` document source access and limitations. The complete downloadable package is [`phase1/Georgia_Phase1_Package.zip`](phase1/Georgia_Phase1_Package.zip).

Status: GO for Phase 2 data acquisition and validation; NO-GO for causal welfare claims with currently verified evidence. No estimation was performed.
## Phase 2 validation checkpoint

See [the validation report](reports/Phase2_Validation_Report.md). Phase 2 is incomplete; Phase 3 causal estimation remains blocked. Raw provider data are not distributed.

Reproduce with CPython 3.12:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
python src/acquire.py
python src/profile_households.py
python -m unittest discover -s tests -v
```
