# Phase 2 validation checkpoint — 7 November 2026

## Interruption recovery and GEOSTAT release validation — 8 November 2026

The recovery audit is recorded in `reports/recovery_audit_2026-11-08.md`. The pinned `GEOSTAT` release (GitHub release id `437541526`) contains 13 API-listed assets. Eleven pass declared SHA-256, byte-count, and file-structure checks. The 2020 and 2023 ZIPs match GitHub's declared bytes and hashes but fail ZIP central-directory parsing on repeated downloads, so they are excluded rather than repaired by inference. Validated household archives are 2016–2019, 2021–2022, 2024, and 2025. Their 154 SPSS tables contain 13,915,562 table rows in aggregate; these are table records, not unique households and must not be interpreted as sample sizes without table-specific keys.

The release-level machine-readable evidence is in `reports/release_validation_summary.json`; schema and row counts are in `reports/release_household_profiles.json`. Existing automated tests remain 4/4 passing. No causal NBG intervention estimate is produced by this validation work.

**Phase 2 is incomplete. Phase 3 causal estimation: NO-GO.** This report records executed checks and open gates, not completion of the requested empirical foundation. All Phase 1 files are preserved unchanged.

## Executed acquisition and validation

`source_manifest.json` records exact official download URLs, UTC retrieval times, errors, accepted byte counts and SHA-256 hashes. HTTP body length must match Content-Length when supplied. ZIP central-directory and member CRC checks must pass before a file is accepted. Raw data are excluded from Git pending redistribution clearance.

| Input | Result | Consequence |
|---|---|---|
| Geostat 2025, media/79814/2025.zip | Content-Length mismatch | Rejected; no sample or missingness claims |
| Geostat 2016, media/23296/2016-DB_eng.zip | Content-Length mismatch | Rejected; methodology-transition comparison blocked |
| Geostat 2017, media/62840/2017.zip | 11,891,371 bytes; ZIP integrity passed | 19 SPSS tables parsed; semantic validation remains open |
| NBG statistics catalogue | HTML downloaded, hashed | Catalogue access is not acquisition of economic time series |

The Geostat URLs were located on the official household-survey download page referenced in Phase 1. The 2017 archive includes English questionnaires. Its expenditure, income and survey-schedule tables each have 11,590 rows; the purchased-food table has 110,840 and consumption table 155,840 rows. These are record counts, **not unique household counts**. The reference/calendar table contains 86 rows and must not be mistaken for 86 sampled periods. `household_profiles.json` contains all table row counts, field labels and system-missing counts/rates. User-defined missing codes, weighted aggregate reconciliation, household identifiers and actual interview-period bounds still need validation.

## Crosswalk and reserve accounting

No consumption-to-CPI crosswalk is approved. Code labels and classifications must be reconciled with questionnaire definitions and annual CPI classifications. Unmatched expenditure share is **not computed**, not zero. `unmatched_share` implements the weighted measure once a reviewed mapping is supplied; it rejects negative/nonfinite spending or weights and returns no estimate for a zero denominator. A food-only mapping cannot establish full consumption coverage.

No reserve reconciliation was completed. Intervention, government transactions, FX/gold valuation, investment income and other adjustments are not yet jointly acquired. `reconcile` returns a blocked status if any component is missing. It never treats unknown valuation as zero or attributes the accounting residual to intervention. Inputs must share dates, currency, scale and accounting conventions before use.

## Phase 3 gate decisions

| Component | Decision | Evidence needed to reopen |
|---|---|---|
| 2017 descriptive survey statistics | Conditional, validation only | Unique identifiers, periods, weights, missing-code rules and published-aggregate reconciliation |
| 2016/2017 transition comparison | NO-GO | Complete 2016 archive and harmonized survey definitions |
| 2025 household analysis | NO-GO | Complete archive and schema/weight validation |
| Intervention event study | NO-GO | Historical auction/BMatch records and execution/disclosure timestamps; event counts remain unknown |
| Reserve accounting | NO-GO | Transaction and valuation components; unexplained residual retained explicitly |
| Household inflation exposure | NO-GO | Reviewed versioned crosswalk and measured unmatched spending |
| Causal intervention effects | NO-GO | Credible assignment mechanism or external instrument, not merely reaction-function residuals |
| Partial identification | Design only | Defensible confounding/missing-channel bounds; otherwise the identified set is uninformative |
| Structural simulation | Design only | Replicable benchmark, validated calibration and explicit policy closures; outputs remain model-dependent |

No exogenous intervention variation has been established. This checkpoint did not obtain the data necessary to independently reassess a new identification design. The Phase 1 restrictions therefore remain binding. No policy effects or household welfare were estimated.

## Reproduction and remaining work

Use CPython 3.12, create an isolated environment, and install `requirements.lock`. Run `python src/acquire.py`, `python src/profile_households.py`, and `python -m unittest discover -s tests -v`. Acquisition failures are recorded in the manifest; a successful process exit does not mean every source passed. Profiling only uses archives accepted by acquisition. Four unit tests passed, covering missing components, valuation accounting, weighted unmatched shares and zero denominators. These tests validate helpers, not the economic data.

Next work: recover complete 2016/2025 archives with documented retrieval diagnostics; establish 2017 interview bounds/keys/weights and user-missing codes; acquire adjacent 2015/2018 years; resolve NBG catalogue data endpoints and acquire each requested series; calculate series coverage/event/missingness statistics; reconcile reserve components; build and review a year-specific CPI crosswalk. No locked analysis dataset is released by this checkpoint.
