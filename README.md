# PubMed Knowledge Graph

**66.2 million nodes. 1.04 billion edges. Every article published in PubMed since 1966.**

> Part of the **Samyama** ecosystem — loaded into and queried via the graph engine at [samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph).
> This repo holds the loader and source-data specifics for the KG.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue" alt="License"></a>

---

We loaded the entire PubMed/MEDLINE corpus -- 37 million articles, 30 million authors, 70 million citations -- then asked:

> *"What are the top MeSH terms co-occurring with cancer research?"*

```cypher
MATCH (a:Article)-[:ANNOTATED_WITH]->(m1:MeSHTerm {name: 'Neoplasms'})
MATCH (a)-[:ANNOTATED_WITH]->(m2:MeSHTerm)
WHERE m2.name <> 'Neoplasms'
RETURN m2.name, count(DISTINCT a) AS articles
ORDER BY articles DESC LIMIT 5
```

| MeSH Term | Articles |
|-----------|----------|
| **Humans** | **513,845** |
| Female | 298,412 |
| Male | 276,891 |
| Animals | 189,234 |
| Middle Aged | 156,728 |

**One billion edges. One query. One machine.** Powered by [Samyama Graph](https://github.com/samyama-ai/samyama-graph).

[See all 100 benchmark queries →](https://samyama-ai.github.io/samyama-graph-book/biomedical_benchmark.html)

---

## Schema

**6 node labels** -- Article (37M), Author (30M), MeSHTerm (30K), Chemical (500K), Journal (30K), Grant (1M)

**6 edge types** -- AUTHORED_BY (150M), ANNOTATED_WITH (400M), MENTIONS_CHEMICAL (126M), PUBLISHED_IN (37M), CITES (70M), FUNDED_BY (5M)

**Data source** -- PubMed/MEDLINE baseline from NLM (1,219 XML files, 101 GB compressed)

## Quick Start

### Load from snapshot (recommended)

```bash
# Download snapshot from release
curl -LO https://github.com/samyama-ai/samyama-graph/releases/download/kg-snapshots-v5/pubmed.sgsnap

# Start Samyama and import
./target/release/samyama
curl -X POST http://localhost:8080/api/tenants \
  -H 'Content-Type: application/json' \
  -d '{"id":"pubmed","name":"PubMed KG"}'
curl -X POST http://localhost:8080/api/tenants/pubmed/snapshot/import \
  -F "file=@pubmed.sgsnap"
```

### Build from source (requires AWS -- 101 GB download)

```bash
git clone https://github.com/samyama-ai/pubmed-kg.git && cd pubmed-kg
pip install -e .
python etl/download_pubmed.py --output-dir data/pubmed-raw    # 101 GB
python etl/parse_pubmed_xml.py data/pubmed-raw/ --output-dir data/pubmed
cargo run --release --example pubmed_loader -- --data-dir data/pubmed
```

## Example Queries

```cypher
-- Most-cited articles
MATCH (a:Article)<-[:CITES]-(citing:Article)
RETURN a.title, count(citing) AS citations ORDER BY citations DESC LIMIT 10

-- Cross-KG: PubMed articles linked to clinical trials
MATCH (a:Article)-[:REFERENCED_IN]->(t:ClinicalTrial)-[:TESTS]->(i:Intervention)
RETURN i.name, count(DISTINCT a) AS articles ORDER BY articles DESC LIMIT 10
```

## Part of the Biomedical Trifecta

PubMed is the backbone of Samyama's billion-edge biomedical benchmark, federated with [Clinical Trials](https://github.com/samyama-ai/clinicaltrials-kg) (27M edges), [Pathways](https://github.com/samyama-ai/pathways-kg) (835K edges), and [Drug Interactions](https://github.com/samyama-ai/druginteractions-kg) (388K edges). Together: **74M nodes, 1 billion edges, 96/100 queries passing.**

## Links

| | |
|---|---|
| Samyama Graph | [github.com/samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph) |
| The Book | [samyama-ai.github.io/samyama-graph-book](https://samyama-ai.github.io/samyama-graph-book/) |
| Benchmark (100 queries) | [Biomedical Benchmark](https://samyama-ai.github.io/samyama-graph-book/biomedical_benchmark.html) |
| Contact | [samyama.dev/contact](https://samyama.dev/contact) |

## License

Apache 2.0
