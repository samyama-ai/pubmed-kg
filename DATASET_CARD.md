---
license: other
pretty_name: PubMed Knowledge Graph
tags:
  - knowledge-graph
  - samyama
  - property-graph
  - biomedical
language:
  - en
size_categories:
  - 10M<n<100M
---

# Dataset Card for `pubmed-kg`

**66.2 million nodes. 1.04 billion edges. Every article published in PubMed since 1966.**

> Part of the **Samyama** ecosystem. This card describes the dataset; the repository
> holds the loader and source-data specifics.

## Structure

**6 node labels** -- Article (37M), Author (30M), MeSHTerm (30K), Chemical (500K), Journal (30K), Grant (1M)

**6 edge types** -- AUTHORED_BY (150M), ANNOTATED_WITH (400M), MENTIONS_CHEMICAL (126M), PUBLISHED_IN (37M), CITES (70M), FUNDED_BY (5M)

**Data source** -- PubMed/MEDLINE baseline from NLM (1,219 XML files, 101 GB compressed)

## Provenance and licence

Apache 2.0 covers the loader. The data is PubMed/MEDLINE from NLM, free to redistribute
with the attribution *Courtesy of the U.S. National Library of Medicine* — except that the
`Article` nodes carry **abstract text**, which is often copyrighted by the publisher rather
than by NLM. Source-by-source terms, and that open question, are in
[`DATA-LICENSES.md`](DATA-LICENSES.md).


## Freshness

**Refresh cadence:** NLM publishes PubMed/MEDLINE as one annual **baseline** release
(each December) plus daily incremental update files on its FTP server throughout the
year. `etl/download_pubmed.py` pulls only from the baseline directory
(`https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/`), listing whatever files are current
at run time — it does not track the daily update files, so re-running the loader
picks up the latest baseline release but nothing published since.

**Data as of:** This repository ships the loader, not the graph — `data/` is empty
and gitignored, no PubMed XML is vendored. So the graph's real age is bounded by
whenever `etl/download_pubmed.py` is next run against NLM's live FTP, not by a
committed snapshot date. The loader code was last changed 2026-03-23 (`git log --
etl/download_pubmed.py`). The best evidence it was last run successfully end-to-end
is README.md's biomedical-benchmark line, which reports a completed load (66.2M
PubMed nodes feeding a 74M-node, 1-billion-edge merged graph) measured 2026-04-03.
Separately, NLM's terms-of-use page (governing redistribution, not the data's
vintage) was last checked 2026-09-18 per `DATA-LICENSES.md`.

## Reproducing

The loader in this repository rebuilds the graph from the upstream source. See the
README's Quick Start for the snapshot download and the from-source build.

## Citation

Please cite this repository if you use it. See [`CITATION.cff`](CITATION.cff) for
machine-readable metadata (CFF 1.2.0).

```bibtex
@misc{pubmed_kg_2026,
  title        = {pubmed-kg: PubMed Knowledge Graph for Samyama},
  author       = {Samyama},
  year         = {2026},
  howpublished = {\url{https://git.samyama.ai/Samyama.ai/pubmed-kg}}
}
```

**No DOI.** This release has not been deposited to Zenodo, so there is no DOI to
cite. Getting one is open work — it requires a human to make the Zenodo deposit
(KG-06).

## Known limitations

- Counts here are those stated by the repository README at the time this card was
  written; they are not re-measured by the card.
- Where a field above says *not recorded*, that is a gap in this repository rather
  than a property of the data.

## Links

| | |
|---|---|
| Samyama Graph | [github.com/samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph) |
| The Book | [samyama-ai.github.io/samyama-graph-book](https://samyama-ai.github.io/samyama-graph-book/) |
| Benchmark (100 queries) | [Biomedical Benchmark](https://samyama-ai.github.io/samyama-graph-book/biomedical_benchmark.html) |
| Contact | [samyama.dev/contact](https://samyama.dev/contact) |
