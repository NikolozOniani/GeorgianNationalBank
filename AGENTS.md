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

Follow the 24 November 2026 calibrated structural design in research/PROTOCOL.md and the current work order at the top of research/ROADMAP.md. Apply the conservative, central and aggressive assumptions to the single registered experiment. Mark observed inputs, estimates and calibrated assumptions separately. Earlier G1–G5 checkpoint statuses describe their original empirical claims. The amended criteria govern new conditional results.

Preserve the pre-fit R3 amendment at research/R3_REOPEN_DESIGN_2026_11_16.md and the rejected results at reports/r3_reopen_2026_11_16/README.md. Use replication/R3_REOPEN.md to reproduce that experiment. Its 90% requirement applies to that experiment only. New results require feasible policy and balance-sheet paths, a documented calibration and sensitivity to the choices that drive the result. Apply the new criteria prospectively. Proceed to R7 synthesis when the relevant scenario outputs are ready.
