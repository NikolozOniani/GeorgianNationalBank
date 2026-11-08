# Integrated academic working paper — Nikoloz Oniani

Read [Paper.md](Paper.md) or the [formatted PDF](../../output/pdf/Oniani_Monetary_Sovereignty_Georgia.pdf). This complete working-paper version integrates household exposure, money and bank relationships, operation costs, reserve accounting, and an independent audit of Cangul and Abel (2026). It is ready for critical external review as a descriptive/accounting paper; it is not an identified estimate of total NBG welfare effects or an externally peer-reviewed publication.

The [credit supplement](../peer_review/README.md) contains the detailed contract methods, Georgian summary, reviewer objections and 54-claim ledger. The previous [accountability dossier](../accountability/README.md), household pilot and policy panel are preserved. Older statements that monetary-operation expenses had not been retrieved are superseded by the annual-account observations here.

## Reproduce numerical results offline

```sh
python src/credit_analysis.py
python src/paper_analysis.py
python src/validate_paper.py
python -m unittest discover -s tests -v
python src/validate_credit.py --raw
```

The last command's `--raw` flag requires the credit source files; omit it for an offline-only check. Numerical calculations and tests require Python's standard library. The checked environment is CPython 3.12.14. Install `requirements-peer-review.lock` only for source PDF/XLSX extraction, figures and PDF rendering.

```sh
python src/paper_analysis.py --acquire --extract
python src/paper_figures.py
python src/paper_pdf.py
```

The annual report was reused locally from the previously verified policy work. Acquisition downloads it only if absent, checks its SHA-256, and preserves a mismatched download separately. `annual_accounts.csv` has exact PDF and printed pages, labels, extracted rows, values, units and source hashes. Duplicate text layers in the provider PDF are accepted only when the extracted value pairs agree. Failed or ambiguous row matching stops extraction.

`annual_results.csv` contains computed interest and balance-sheet aggregates; `accounting_checks.csv` contains twelve identities; `reserve_bridges.csv` separates transactions from the remaining composite; `reserve_channel_sensitivity.csv` contains 27 conditional cases; and `reserve_target_arithmetic.csv` preserves both 102% and 105% reference coverage values printed in the IMF paper. The functions and assumptions are explicit in `paper_analysis.py`.

**Review priority:** independently check the dollarization derivative and the signs on printed page 12 of Cangul and Abel against the welfare objective on page 11. The paper identifies a published-notation inconsistency, not a demonstrated coding error. The supplied numerical exercise isolates one channel and does not reproduce or replace their optimal reserve target.

The strongest next data additions are daily operation-level interest/balance histories, a complete executed-intervention ledger with valuation and government-flow bridges, and protected linked borrower-contract/income data. The present paper does not wait for those records to report the independently verified results.
