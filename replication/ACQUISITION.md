# Replicating the November 2026 acquisition

The [source plan](../data/source_plan.json) and [source manifest](../data/source_manifest.json) contain original URLs, expected hashes, format, requirement IDs, local paths and retrieval metadata. The catalogue update date is not an observation's first-publication date. This is a latest-available vintage, not a real-time information dataset.

Install `requirements-acquisition.txt` in a Python 3.12 environment. Run from the repository root:

```sh
python src/validate_episode.py
python -m unittest discover -s tests -v
python replication/check_repository.py
```

These checks work with committed compact outputs. `validation.json` reports which raw hashes were actually checked and which raw caches are absent. The stored acquisition-run report checked the locally available sources; a fresh clone must not claim those raw files have been verified until supplied.

Full source-to-output replication, after supplying the pinned source files:

```sh
python src/extract_episode.py --check
python src/validate_episode.py
python src/plot_episode.py
```

`--check` regenerates in a temporary directory and requires byte equality. Normal extraction stages all outputs before promoting them; source SHA mismatches stop extraction. Acquisition writes successful assets and an atomic manifest incrementally; failed assets do not discard other successes. A failed source pin survives subsequent retries. Changed upstream files require a separate reviewed vintage, not a reset of this lock.

## Manual large-file handoff

Per the author's instruction, no new large-file downloads or uploads are attempted. Files acquired before that instruction remain locally available. The acquisition code refuses known files above 1 MB before requesting their contents and bounds unknown responses. It does not silently refresh a cached source.

All original raw files remain outside this commit. Two generated files above 1 MB also await manual commit: `data/derived/episode_2026_11_09/reserve_liquidity_cells.csv` and `data/derived/episode_2026_11_09/money_transfers_country.csv`. Their exact hashes, source paths and sizes appear in [manual artifacts](../data/manual_artifacts.json). The compact reported R1 cells and transfer-country sums are committed, so current accounting validation does not depend on transferring the larger files. Omitted R1 cells retain their blank status in the catalogue; absence never means zero.

Please manually commit the two generated CSVs and supply the source files listed in the manifest at their recorded local paths (or use a versioned release for permitted source-data artifacts). Keep original bytes. The 2025 annual report PDF can be supplied locally for verification without redistributing the full publication. `git add -f` is needed for deliberately ignored paths. No source-file transfer has been represented as completed by this commit.

Small missing assets may be retrieved explicitly with `python src/acquire_episode.py --ids SOURCE_ID`. Existing large files are hash-checked locally without downloading again. Full source replication is pending manual availability on a fresh clone; output-level accounting and tests are already reproducible.

## Interpretation and accounting conventions

- FX-market `USD_Buy-eng ` C is NBG auction sales; D is net non-auction NBG sales, so multiply D by −1 for purchase-positive net. `USD_Sell-eng ` D is auction purchases; C is exercised options and E swaps. Non-auction gross purchase/sale columns stay blank.
- Official FX observations are calendar-valid dates, not execution timestamps. Divide each currency quote by its header denomination (AMD is quoted per 1,000 dram). Annual worksheet selection excludes overlap outside its named year.
- Source reserve stocks and transfers in USD thousand are divided by 1,000. TIBR/CD/market-rate decimal values are multiplied by 100. Interbank repo rates already use percent. Central-bank balances are GEL million; events are GEL units.
- Annual BOP totals are distinct from quarterly flows. Debt-service schedules describe future contractual payments at the stated vintage; they are not realized future observations. Overlapping maturity buckets cannot be summed indiscriminately.
- The source reports 2026 government debt including accrued interest. Invalid source dates remain explicitly invalid. Economic validation tolerances are recorded with each check.
- Three source comparisons remain qualified in `validation.json`; passing software tests does not turn them into passed source reconciliations. The 2023 annual discrepancy and quarantined FX-market total are separately retained.
- Global US closing prices and SOFR effective dates do not supply Georgian pre-trade information automatically. First-release timestamps and complete market calendars are unavailable; no causal time alignment is claimed.
