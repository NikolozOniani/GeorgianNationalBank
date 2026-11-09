# Supporting archive

The only active study is defined by [the research protocol](../research/PROTOCOL.md). Historical research directions, prospective handoffs and manuscript instructions are superseded, including those inside archived reports or ZIP packages.

`legacy/` preserves the numerical and source-provenance snapshot at commit [`46fdde7dd8cb673378154c099b72e8c40060b684`](https://github.com/NikolozOniani/GeorgianNationalBank/tree/46fdde7dd8cb673378154c099b72e8c40060b684). Its internal directory layout is retained so analytical scripts and their relative input locks still resolve. There is one stored copy of each retained dataset.

The [migration manifest](migration_manifest.json) records all **146 original tracked files**, their SHA-256, byte count, old location, current location or historical recovery link:

- **120 files** retained unchanged in `legacy/`, including every tracked CSV/JSON dataset, source manifest, numerical script, figure and Phase 1 package.
- **24 files** retired from the checked-out tree and recoverable from the baseline commit: superseded manuscripts, speeches/advocacy prose, their navigation/review materials, PDFs, document renderers and mixed editorial validators. No Git history was rewritten.
- **2 root configuration files** retained at the root; ignore rules were extended for the relocated raw cache, while attributes still protect CSV bytes and binary files.

The removed prose is not an active alternate paper or public-facing project edition. Historical calculations that supported it remain reproducible. The metadata records the exact recovery URL without reproducing retired titles or prose.

Use the [evidence catalogue](../evidence/README.md) to locate relevant reserve and intervention material. Household/credit datasets and earlier research directions are preservation-only. Historical reports can record old limits and decisions; they are not current assessments or instructions.

The [retired-test register](retired_tests.json) identifies one editorial test requiring withdrawn speech text. Its arithmetic coverage checks are retained in the current tests. The other 32 archived tests run unchanged. Old document-generation and broad editorial-validation entry points were retired; use [the current replication checks](../replication/README.md).

Raw downloads were never tracked. Existing local raw files were relocated to `legacy/data/raw/` without alteration; fresh checkouts still require permitted source retrieval. The GEOSTAT release assets and all earlier commits are unchanged.
