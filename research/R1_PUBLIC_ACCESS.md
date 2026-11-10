# R1 public-source checks

**Checked:** 10 November 2026. **Scope:** public evidence for D01–D10, using existing pinned observations first. This log does not assert an exhaustive search of every NBG record or classify an unavailable field as deliberately withheld.

| Source ID / route | Action and result | What it establishes / does not establish |
|---|---|---|
| `purchase_disclosure_aug2025` — [25 August 2025 release](https://nbg.gov.ge/en/media/news/nbg-boosts-international-reserves-by-usd-1-3-billion-since-start-of-2025) | Downloaded actual HTML; pinned separately | Dated disclosure of monthly net purchases, including net-zero January–February; no gross transaction log or proof of first release for earlier months |
| `monetary_manual_2021` — official monetary-policy manual | Downloaded actual PDF, p13 paragraphs 50–52 inspected | Historical auction settlement and qualitative BMatch trigger; no confirmed episode-specific numerical assignment rule |
| `instruments_2023` — official instruments presentation | Downloaded actual PDF, p14 inspected | Historical operating windows and auction settlement convention; informational guidance, not individual execution evidence |
| `annual2025` | Reused hash-verified report; PDF pp47–48, 262 and 275 inspected | Reported accumulation phase; approximate government flows; audited gold holdings/prices and NBG debt-security cash/accrual movements |
| `fx_market`, `reserve_assets`, `bop_bpm6` | Reused pinned native observations | Net intervention and stock/transaction accounting; incomplete gross and component decomposition |
| `central_bank`, `depository_survey` | Reused actual workbooks; extracted additional sheets/rows and definition notes | Instrument positions and sector balance sheets; monthly stocks, not daily cash flows |
| `treasury_bills`, `treasury_notes` | Reused workbooks; extracted episode records | Value dates, reported issuance and rates; no invented auction timestamps or NBG cost attribution |
| `bmatch_statement`, `fx_rules`, `fx_method` | Rechecked official descriptions and existing pinned snapshots | Matching, government channel and fixing conventions; no execution history or threshold calibration |
| `purchases_2025`, `reserves_aug2026` | Reused dated releases | Net annual/partial-year benchmarks with distinct reference and disclosure periods |

Exact original URLs, retrieved timestamps, sizes and SHA-256 hashes are in the [three-source acquisition manifest](../data/r1_source_manifest.json) and the [49-source R1 register](../reports/r1_2026_11_10/sources.json). The [source plan](r1_source_plan.json) and [acquisition wrapper](../src/acquire_r1.py) preserve successful independent retrievals and the frozen checksums. Raw files remain outside Git under the existing source-recovery policy.

Public web checks used official-domain searches for BMatch thresholds/rules, the 2025 annual report and government FX flows, historical monetary instruments, and monthly purchase disclosures. They located the documents above but **did not recover** gross daily BMatch executions, a versioned numerical 2025–2026 trigger/cap/override dataset, or a full monthly reserve valuation/government transaction bridge. This is a retrieval finding, not proof of nonpublication. Further public investigation and an authorized request can run alongside each other; no legal denial or confidentiality ruling has been received.

Classification at this checkpoint:

- **Retrieved, validated to stated limits:** monthly net intervention, statistical stocks/BOP, ledger inputs, selected audited accounts and descriptive historical rules.
- **Retrieved but definition/revision unresolved:** gold 2024 overlap, older auction-month/annual discrepancies, flagged market aggregates and transfer-source differences.
- **Not retrieved at the required detail:** gross executions, applicable rule calibration, government conversions, transaction-level valuation bridge, pre-order quotes, 2025 daily liquidity and average remuneration exposures.
- **Legally confidential / genuinely unpublished:** not established for the missing fields. Counterparty names are unnecessary for the primary requests.

No correspondence was sent and no provider restriction was bypassed. No fresh research observations were manufactured from search snippets.
