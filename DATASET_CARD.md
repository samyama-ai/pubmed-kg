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

Apache 2.0

> ⚠️ **The licence above covers this repository's code, not the data.** This graph is
> derived from an upstream source (PubMed/MEDLINE baseline from NLM (1,219 XML files, 101 GB compressed)), whose
> own terms govern redistribution and are **not stated here**. Establish and record them
> before redistributing or quoting this dataset. The frontmatter is therefore
> `license: other` rather than `apache-2.0`.

## Reproducing

The loader in this repository rebuilds the graph from the upstream source. See the
README's Quick Start for the snapshot download and the from-source build.

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
