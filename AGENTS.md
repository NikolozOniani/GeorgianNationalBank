# Project authority

The authoritative study identity is in `study.json`; the sole research protocol is `research/PROTOCOL.md`.

Title: The Economics of Reserve Accumulation in Georgia: An Independent Assessment of Costs, Benefits, and Optimal Reserve Adequacy

Author: Nikoloz Oniani

Research question: Did the National Bank of Georgia's large-scale foreign-currency purchases prevent the Georgian lari from appreciating, and were the resulting economic costs justified by the benefits of reserve accumulation?

Scope: One intervention episode, one economic counterfactual, and its consequences.

Do not change the title, question or scope without the author's explicit instruction. Historical instructions, handoffs and manuscripts in Git history or `archive/` are superseded. Do not revive earlier research directions or advocacy material.

Preserve archived numerical files, source hashes and analytical code. New observations require separate vintage and observation-status metadata. Never substitute reserve-stock changes for intervention, monthly disclosure dates for execution dates, forecasts for observations, or total central-bank expenses for marginal reserve costs.

Use `research/ROADMAP.md` as the authoritative research-completion sequence and `research/data_requirements.json` for its supporting acquisition specifications. The roadmap records the household-incidence dependencies of the same episode counterfactual. An accessible catalogue is not proof that the required detail or period has been retrieved. Record access failures and unresolved definitions accurately.

Do not infer causal effects from contemporaneous exchange-rate/intervention correlations. Preserve results that contradict the motivating hypothesis. Economic accounting, causal estimates, and conditional model calculations must remain distinguishable.

The latest authorized task is R1 execution: build and reconcile episode transaction, information, reserve and liquidity ledgers under the completed R0 registration. The current checkpoint and unresolved requirements are in `research/R1_STATUS.md`; full G1 remains open. Future tasks must follow the user's current authorization and the roadmap's evidence gates; the existence of a planned stage does not authorize correspondence or manufacture identification. R1 does not authorize R3 estimation or manuscript drafting. `manuscript/STRUCTURE.md` specifies the eventual academic argument. Keep programming instructions, repository commentary and project-management language out of the eventual main paper; place those in `replication/` or `docs/`.

Before committing structural changes, run `python replication/check_repository.py`. Check preservation, local documentation links, study identity and the archived numerical tests. Do not silently reset source locks or regenerate historical reports in place.
