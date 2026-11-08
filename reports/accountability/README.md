# Accountability edition: complete first version

**Main conclusion:** the evidence supports documented purchasing-power pressure, conditional policy cost/benefit mechanisms, and stronger retrospective disclosure and distributional evaluation. It does **not** establish that NBG policy caused net household impoverishment. The title is an investigation, not a predetermined verdict.

| Deliverable | File |
|---|---|
| A. Political-economic evidence dossier | [Dossier.md](Dossier.md) |
| B. Public accountability scoreboard and disclosure classifications | [Scoreboard.md](Scoreboard.md) |
| C. Quantitative examples and price-index chart | [Illustrations.md](Illustrations.md), [CSV ledger](evidence_ledger.csv), [SVG](national_cpi.svg) |
| D. Georgian public speech | [Speech_ka.md](Speech_ka.md) |
| E. Fact-checking and opposition briefing | [Fact_check.md](Fact_check.md) |
| F. Actionable reforms, owners and tradeoffs | [Reforms.md](Reforms.md) |
| Sources, hashes and current verification | [sources.md](sources.md), [JSON register](source_register.json), [retrieval results](source_retrieval.json) |
| Validation and preservation | [validation.json](validation.json), [test log](test_results.txt), [preservation lock](parent_files.lock.json) |

The Georgian delivery text has **1,609 whitespace-delimited words**, excluding its title, editorial note and claim markers. At a deliberate **110–130 words/minute**, its estimated duration is **12.4–14.6 minutes**. This is a planning estimate, not a timed rehearsal. Pause around examples; do not omit qualifications to shorten the speech. Markers S01–S17 are not read aloud. The other deliverables are in English for source/method review.

## Reproduction

From the repository root, using Python 3.12+ and the standard library:

```sh
python src/accountability_scenarios.py
python src/validate_accountability.py
```

No network, raw household files or new econometric estimation is needed. `inputs.lock.json` pins the five reused input files; the script rejects changed data. The optional `python src/accountability_sources.py` downloads only supplemental current official legal/disclosure/instrument pages into ignored content-addressed files, records failures independently, and refreshes source metadata. Review its changes before publishing a new edition. It does not overwrite old survey or policy inputs. Live HTML bytes can change without substantive text changes; hashes record vintages, not semantic equivalence.

Computational outputs: 53 ledger rows; CPI monthly index path; one deterministic standalone SVG. Baseline calculations compound CPI, invert the price factor for purchasing power, preserve the sign of net FX sales, and vary explicit loan/FX/carry assumptions. No interpolation, causal regression, new instrument or household welfare aggregation is introduced. Missing intervention fields remain blank in the original panel.

## Verified checkpoint and corrections

Started from clean `main` at **43c00d543485d47069b5ddb9755e9363b733c512**; all ten pre-existing tests passed before editing. Prior tracked content is byte-preserved except the top-level README, which adds navigation. The parent preservation lock excludes that intentional README change. The 2017 pilot was neither reprocessed nor relabeled as a total inflation result.

Current Georgian legislation and NBG disclosures were checked on **8 November 2026**. The law's current Georgian consolidation lists an October 2026 amendment; an older English translation is not substituted for it. The communication PDF's adoption/revision date was **not verified**, so this edition does not call it a 2025 revision. The historical NBG statement says 25 days for BMatch disclosure, while the currently served communication PDF says the third week: this is a wording/version question, not proof of late publication.

Two precision corrections from review: the reserve panel contains **five component columns plus a headline total**, rather than six components; and the 2024 annual report's exact intervention total is at **printed p.46 / PDF page47**, with the seven-auction summary at printed p.25 / PDF page26. Source locators in this edition use those verified page numbers. Older files are preserved rather than silently rewritten.

## Boundaries that must survive political editing

- National cumulative CPI is not a measured NBG contribution or each household's inflation.
- The partial 2017 basket contribution is not full household inflation, welfare or a current poverty measure.
- Hypothetical loan, exchange-rate and financing illustrations are not observed policy-caused losses.
- Reserve changes, intervention transactions, valuation and expenses are separate concepts.
- The IMF's favorable model evidence remains in the public speech and briefing.
- A missing project file does not prove nonpublication or deliberate concealment. No corruption, collusion or intent to impoverish is established.

This is a usable first public version with an explicit evidentiary ceiling, not a request to postpone public debate until causal identification becomes possible.
