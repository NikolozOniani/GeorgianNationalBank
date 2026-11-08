# Credit-channel study: external review packet

**Version 0.1, 8 November 2026.** This is a complete first credit-channel chapter for methodological and substantive review. It is not an externally peer-reviewed publication or a causal estimate of NBG-induced poverty.

Start with [the manuscript](Manuscript.md), the [formatted PDF](../../output/pdf/Georgia_Household_Credit_Peer_Review.pdf), [Georgian summary](Summary_ka.md), and [reviewer brief](Reviewer_Brief.md). The [prior accountability dossier](../accountability/README.md) retains the wider investigation, speech, counterarguments and reform agenda. None of that completed work was replaced.

## What is ready to review

- Actual monthly credit and deposit data: 46 series, 60 months, 2,760 observations, with source-cell provenance and 360 reconciliation checks.
- Observed rate comparisons, standardized annuity calculations, and a separate synthetic policy-indexed contract experiment with 132 sensitivity cases.
- Three figures; machine-readable tables; exact source URLs and hashes; explicit population, revision and timing limitations.
- A claim ledger, hostile-review questions, disclosure specifications, and tests covering counterevidence, accounting, effective dates and replication.

The study does not estimate a national borrower interest bill, actual income-group incidence, a causal pass-through coefficient, or net policy welfare. Contract/income linkage is the next empirical requirement, not a hidden assumption in these results.

## Replicate without downloading anything

From the repository root with Python 3.11 or newer:

```sh
python src/credit_analysis.py
python -m unittest discover -s tests -v
python src/validate_credit.py
```

The numerical calculations and tests use only Python's standard library and committed inputs. The validation script also checks that running the analysis reproduces the committed numerical outputs exactly. It records versions, preservation results and test output in this folder. It does not require access to household microdata or send any request to another person.

For extraction, figures and document rendering, install the separate reviewed dependency list:

```sh
python -m pip install -r requirements-peer-review.lock
python src/credit_figures.py
python src/credit_pdf.py
```

The PDF renderer uses DejaVu Sans TTF files, normally supplied by the `fonts-dejavu-core` system package. `--font-dir` can point to a directory containing the four standard DejaVu Sans faces. Font paths and rendering versions affect PDF bytes but not numerical results. The checked manuscript is also available as plain Markdown.

## Audit the original source extraction

```sh
python src/credit_acquire.py
python src/credit_extract.py
python src/credit_analysis.py
python src/validate_credit.py --raw
```

Run these commands separately. Acquisition retains successful files even if another source fails. Downloaded XLSX files must pass CRC and workbook-structure checks. A newly downloaded file whose SHA-256 differs from the reviewed vintage is quarantined; it is not silently substituted. Provider URLs can be revised in place. If a vintage disappears, use the committed observations for numerical replication and obtain the pinned source bytes before claiming a full source-extraction replication. Do not simply edit the expected hashes to make a mismatch pass.

Only seven workbooks are required for the core extraction. The additional L3.14 consumer-stock workbook and three interpretive PDFs are independently logged, so an unavailable unused source does not block extracting the verified core. Historical first-publication dates and revisions were not reconstructed; the data are the November 2026 vintage of 2020–2024 observations.

## Files

| File | Purpose |
|---|---|
| `credit_monthly_2020_2024.csv` | Analysis-ready monthly panel; nominal amounts/rates |
| `credit_observations.csv` | Every value with workbook, sheet, cell, date cell and source hash |
| `series_dictionary.csv`, `coverage.csv` | Definitions, populations, available coverage and missingness |
| `sources.json`, `Sources.md`, `acquisition_log.json` | Source acquisition, exact hashes and interpretation references |
| `workbook_notes.json` | Provider methodology for the seven core workbooks |
| `reconciliation.csv`, `extraction_validation.json` | Purpose, residency and sector accounting checks |
| `table1_observed.csv` | December 2020/2022/2024 actual rates and balances |
| `table2_standardized_new_loan.csv` | Assumed loan sizes/terms priced at actual housing-loan averages |
| `indexed_contract_monthly.csv` | Main synthetic loan's complete payment and balance path |
| `table3_reset_sensitivity.csv` | All reset phases, maturities and assumed linkage coefficients |
| `alternative_reference_9pct.csv` | Sensitivity to the held-rate accounting reference |
| `table4_conditional_income_exposure.csv` | Hypothetical equal-debt income comparisons, not survey groups |
| `claim_ledger.csv` | Numerical claims, evidence classes and review challenges |
| `analysis_inputs.lock.json` | Exact monthly-panel and previously verified policy-file hashes |
| `validation_report.json`, `tests.log` | Executed verification and limits |
| `Data_Request_Draft.md` | Specific additional records needed; draft only, not sent |

The starting research commit is `89bbc62a1e2d3dc1fd786568460c39bc431c6cf7`. Use the commit containing this packet, rather than an unpinned future `main`, when citing or replicating it. All prior research files are preserved; the top-level README only gains navigation to this chapter.
