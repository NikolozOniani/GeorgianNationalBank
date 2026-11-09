# Replicating the November 2026 acquisition

The [source plan](../data/source_plan.json) and [source manifest](../data/source_manifest.json) contain original URLs, expected hashes, format, requirement IDs, local paths and retrieval metadata. The catalogue update date is not an observation's first-publication date. This is a latest-available vintage, not a real-time information dataset.

Install `requirements-acquisition.txt` in a Python 3.12 environment. Run from the repository root:

```sh
python src/validate_episode.py
python -m unittest discover -s tests -v
python replication/check_repository.py
```

These checks require all 36 committed derived tables, including the two larger CSVs. Validation writes to ignored `replication/local-results/episode/` by default, preserving the dated acquisition report. Its `raw_source_validation_complete` flag distinguishes a complete original-source hash check from output-only validation. A fresh clone must not claim absent source files have been verified. Use `--require-raw` to make missing or invalid original sources a failing condition.

Full source-to-output replication, after supplying the pinned source files:

```sh
python src/extract_episode.py --check
python src/validate_episode.py --require-raw
python src/plot_episode.py
```

`--check` regenerates in a temporary directory and requires byte equality. Normal extraction stages all outputs before promoting them; source SHA mismatches stop extraction. Acquisition writes successful assets and an atomic manifest incrementally; failed assets do not discard other successes. A failed source pin survives subsequent retries. Changed upstream files require a separate reviewed vintage, not a reset of this lock.

## Source access and reproducibility

The obsolete 1 MB manual-download limit has been removed. Explicit acquisition permits ordinary source files up to a bounded 128 MiB per response, checks Content-Length where supplied, validates format and the pinned SHA-256, and returns failure if any selected asset failed. Successful assets survive partial failures. No source was downloaded during R0; the larger-download behavior is tested with an in-memory response. Cached sources are not silently refreshed.

The full generated outputs `data/derived/episode_2026_11_09/reserve_liquidity_cells.csv` and `data/derived/episode_2026_11_09/money_transfers_country.csv` are committed and required. Their hashes, source paths and sizes appear in [artifact dispositions](../data/manual_artifacts.json), whose historical filename is retained for compatibility. Omitted reserve-template cells retain their blank status in the catalogue; absence never means zero.

Original raw source files remain outside the commit. Supply them at their recorded manifest paths, or use a versioned release for permitted source-data artifacts, to repeat the extraction from original workbooks. Keep original bytes. The 2025 annual report PDF can be supplied locally for verification without redistributing the full publication.

Missing assets may be retrieved explicitly with `python src/acquire_episode.py --ids SOURCE_ID`. The frozen manifest includes six catalogue snapshots outside the 51-item numerical source plan; `python src/acquire_episode.py --discover` retrieves those separately and still enforces previous pins. Do not interpret a changed dynamic provider response as the original vintage. Obtain original bytes from the provider or a lawful author copy when needed, and record a new vintage for new observations. The [R0 source-access register](../reports/r0_2026_11_10/source_access.json) records exact URLs, hashes, local verification and rights/access limitations for every source. Public download access does not establish redistribution permission. No raw-source redistribution rights are asserted.

The [R0 verification report](../reports/r0_2026_11_10/README.md) tests a clean checkout without sources, then supplies the existing pinned local files and repeats extraction with byte comparisons. Repeat it with:

```sh
python replication/audit_r0.py --output-dir replication/local-results/r0-audit
python replication/verify_r0.py
```

The clean-checkout test uses indexed paths with current working bytes; stage new files before testing a pending commit. It copies sources only after explicitly recording their absence. It uses the installed environment; it is not an independent installation or a test of future upstream availability. Raw data remain outside Git, so a clone alone reproduces output checks but needs original files to reproduce extraction. Installation instructions and source routes are the recovery path; the local cache is not a permanent public archive.

## Interpretation and accounting conventions

- FX-market `USD_Buy-eng ` C is NBG auction sales; D is net non-auction NBG sales, so multiply D by −1 for purchase-positive net. `USD_Sell-eng ` D is auction purchases; C is exercised options and E swaps. Non-auction gross purchase/sale columns stay blank.
- Official FX observations are calendar-valid dates, not execution timestamps. Divide each currency quote by its header denomination (AMD is quoted per 1,000 dram). Annual worksheet selection excludes overlap outside its named year.
- Source reserve stocks and transfers in USD thousand are divided by 1,000. TIBR/CD/market-rate decimal values are multiplied by 100. Interbank repo rates already use percent. Central-bank balances are GEL million; events are GEL units.
- Annual BOP totals are distinct from quarterly flows. Debt-service schedules describe future contractual payments at the stated vintage; they are not realized future observations. Overlapping maturity buckets cannot be summed indiscriminately.
- The source reports 2026 government debt including accrued interest. Invalid source dates remain explicitly invalid. Economic validation tolerances are recorded with each check.
- Three source comparisons remain qualified in `validation.json`; passing software tests does not turn them into passed source reconciliations. The 2023 annual discrepancy and quarantined FX-market total are separately retained.
- Global US closing prices and SOFR effective dates do not supply Georgian pre-trade information automatically. First-release timestamps and complete market calendars are unavailable; no causal time alignment is claimed.
