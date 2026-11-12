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

The R3 public-evidence design decision is in reports/r3_2026_11_12/README.md. G2 remains unsatisfied. Use public evidence only. Preserve the registered episode and R1 accounting checkpoint. See reports/r2_2026_11_11/README.md for reconstructed ratios, conditional liquidity and remaining replication gaps. `manuscript/STRUCTURE.md` specifies the eventual academic argument. Keep programming instructions, repository commentary and project-management language out of the eventual main paper; place those in `replication/` or `docs/`.

Before committing structural changes, run `python replication/check_repository.py`. Check preservation, local documentation links, study identity and the archived numerical tests. Do not silently reset source locks or regenerate historical reports in place.
