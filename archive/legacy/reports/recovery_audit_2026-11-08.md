# Interruption-recovery audit

Audit date: 2026-11-08 (UTC). Repository: `NikolozOniani/GeorgianNationalBank`.

## Last verified checkpoint

The repository's last commit is `6abc1d5` (`Create RAWDATA`), tagged `GEOSTAT`, and it is identical to `origin/main`. The preceding Phase 2 checkpoint is commit `94ddc50` (`Add Phase 2 acquisition checkpoint and household schema validation`). Its committed household profile covers only `hies2017` (19 SPSS tables); no release-asset processing was committed.

## Safe and verified

- Phase 1 files and the Phase 2 checkpoint remain present and unchanged in Git history.
- Existing validation tests pass: 4 tests, 4 passed.
- Release metadata independently fetched from the GitHub API: release id `437541526`, tag `GEOSTAT`, 13 assets. The release description attachment URLs were not used.
- Valid and SHA-256 matched release ZIPs: 2016, 2017, 2018, 2019, 2021, and 2022. Each passes ZIP CRC testing.
- The committed 2017 profile is readable and internally generated from the 2017 archive; it is not evidence that the other years were processed.

## Incomplete or failed

- Uncommitted recovery files exist: `reports/release_assets.json` and `src/release_download.py`.
- `2020.zip` and `2023.zip` exist at the release-declared byte counts but fail ZIP central-directory integrity. They are not accepted inputs and must be re-downloaded and re-hashed.
- Release assets 2024, 2025, `Consumer-basket-weights.xlsx`, `Consumer-Price-Detail-Indices-.Previous-month.100.xlsx`, and `Description-of-IHS-database-variables---Eng.pdf` are absent.
- No release-level integrity manifest has been generated or committed.
- No 2016–2025 validation, crosswalk, distributional inflation estimate, figure, or causal-identification update has been completed.

## Potential data loss

No committed Phase 1 or Phase 2 checkpoint is missing. The interrupted session left uncommitted download/processing work; absent files and invalid ZIPs are recoverable from the pinned GitHub release URLs. Any uncommitted artifacts not listed above should be treated as lost because they are not present in the workspace.

## Recovery rule

Preserve all valid matched archives and the committed profile. Repair only absent or integrity-failing release assets, then regenerate processing outputs from the verified release inputs.
