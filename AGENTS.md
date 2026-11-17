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

The R4 funding and income accounts are in reports/r4_2026_11_12/README.md. G3 is incomplete for episode attribution. The R3 public-evidence design decision is in reports/r3_2026_11_12/README.md. G2 remains unsatisfied. Use public evidence only. Preserve the registered episode and R1 accounting checkpoint. See reports/r2_2026_11_11/README.md for reconstructed ratios, conditional liquidity and remaining replication gaps. `manuscript/STRUCTURE.md` specifies the eventual academic argument. Keep programming instructions, repository commentary and project-management language out of the eventual main paper; place those in `replication/` or `docs/`.

Before committing structural changes, run `python replication/check_repository.py`. Check preservation, local documentation links, study identity and the archived numerical tests. Do not silently reset source locks or regenerate historical reports in place.

R6 conditional benefit calculations are in reports/r6_2026_11_15/README.md. G4 remains partial. The financial hurdle is not a measured national resource cost, hypothetical hazard reductions are not achieved reductions, and the single-issue spread diagnostic does not replicate the full IMF optimum. Preserve the audited R5 correction.

The author reopened R3 before R7 or manuscript drafting. The pre-fit amendment is research/R3_REOPEN_DESIGN_2026_11_16.md, committed at 3546bce794d093ef6458fa8813d570b14a68e42c. Results are in reports/r3_reopen_2026_11_16/README.md: the candidate fails its precommitted resampling gate. No preferred path or empirical range is released. Do not propagate rejected candidate paths into household, cost-benefit or optimal-reserve claims. R7 and drafting remain paused; any subsequent model change requires its own dated design amendment and independent validation. Use replication/R3_REOPEN.md for dependencies and source/model checks.
