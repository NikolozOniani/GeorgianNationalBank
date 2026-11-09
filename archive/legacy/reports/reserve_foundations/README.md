# Replication: reserve foundations

Results: [Findings.md](Findings.md). Main outputs: `ara_components.csv`, `ara_reconstruction.csv`, `ara_contributions.csv`, `historical_interest.csv`, `interest_observations.csv`, `reserve_level_scenarios.csv`, `comparative_column_checks.csv`, `vintage_ratios.csv`, and `validation.json`.

Numerical replication requires only Python's standard library:

```sh
python src/reserve_foundations.py
python -m unittest discover -s tests -v
```

Original-source extraction requires pypdf (version pinned in `requirements-peer-review.lock`):

```sh
python src/reserve_foundations.py --acquire --extract
```

The source manifest pins PDF URLs and hashes. Existing raw files are verified and reused. Changed downloaded bytes remain in a partial file and are rejected. Original PDFs are ignored; extracted numeric rows carry source IDs, hashes, labels and PDF pages. The IMF component table uses USD million, ratios use percent or months, financial statements use GEL thousand before conversion. No monthly interpolation is used.

This is reproduction from published component estimates, not a claim of independently rebuilding every component from bank-level submissions. Values dated 2024–2028 in the 2024 IMF table are forecasts. The source-vintage ledger is kept separate. `validation.json` retains adjusted-ARA nonreconciliation rather than marking that calculation as passed.
