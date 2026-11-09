# Repository reorganization record

Baseline: `46fdde7dd8cb673378154c099b72e8c40060b684`, verified against GitHub `main` before changes. The working tree was clean. Source-review cutoff: 8 November 2026.

The study's final title, author, research question and scope are recorded exactly in [study.json](../study.json), the root README, project instructions, research protocol and manuscript structure. The sole active protocol is [research/PROTOCOL.md](../research/PROTOCOL.md). The study has one purchase episode and one no-purchases counterfactual. No paper was drafted or formatted; no new empirical analysis was conducted.

## Disposition of previous work

The [migration manifest](../archive/migration_manifest.json) covers every one of the 146 original tracked files. All 120 retained archive files are byte-for-byte copies at their new paths. All numerical datasets, provenance records, analytical source code, existing figures and historical source packages remain available. The local ignored raw cache was moved with its original relative layout; it was not uploaded or redownloaded.

Twenty-four obsolete publication/editorial files were removed from the checked-out project and preserved by their exact historical commit links. These include the old root navigation, two manuscripts and PDFs, speech/advocacy prose, superseded review materials, document renderers and editorial validators tied to those documents. This is a recoverable removal, not a history rewrite. Historical research still useful for definitions, calculations and replication remains in `archive/legacy/`. Archive headings and instructions have no authority over the active protocol.

The `GEOSTAT` release was not modified. No remote issue, correspondence or data request was created. No repository history was rewritten, no numerical source lock changed, and no current result was presented as a new estimate.

## Technical checks

Before migration, all 33 existing tests passed. The post-migration runner retains 32 unchanged archived tests; the one editorial test requiring withdrawn prose is explicitly retired and its numerical coverage assertions are checked by a current replacement. Four current tests check preservation, authoritative identity/links, the acquisition specification and the transferred numerical assertions.

The runner also checks numerical reproduction of the four preserved analytical generators in a temporary copy. Every pre-existing CSV there and selected numerical JSON outputs are compared after generation. Two old illustration CSVs reproduce with identical content but CRLF rather than their archived LF line endings; the runner reports this explicitly and checks only that exact formatting difference. All other compared files require byte agreement. The untouched archive is verified again afterward. These checks assess preservation and reproducibility, not causal identification or economic adequacy.

The completed run is recorded in [reorganization_validation.json](reorganization_validation.json). Historical broad editorial validators that require removed documents are retired, rather than silently represented as passing current checks. [Current replication instructions](../replication/README.md) supersede old command examples.

## Authoritative path forward

1. Acquire and reconcile the episode's gross operations and aligned market observations under D01–D07.
2. Establish the execution boundaries, intervention assignment and feasibility of the specified no-purchases counterfactual.
3. Match the reserve, liquidity and financing accounts under D08–D14, reusing historical evidence.
4. Replicate and test the reserve-benefit benchmark, financing channel and insurance assumptions under D15, D16 and D18; refine consequences with D17.
5. Pass the protocol's evidence gates and then write the single paper using its approved structure.

The acquisition plan is concrete but does not certify unacquired datasets. Public availability, retrieval failure, investigated gaps and potential formal requests are distinguished. Any future finding must answer the fixed question at the strength its evidence permits.
