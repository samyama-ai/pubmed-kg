# PubMed Knowledge Graph

Full PubMed/MEDLINE corpus as a knowledge graph — 37M+ articles with authors, MeSH terms, chemicals, citations, and grants.

## Quick Start

```bash
# 1. Download PubMed baseline (101 GB compressed, runs on AWS)
python etl/download_pubmed.py --output-dir data/pubmed-raw --max-files 10

# 2. Parse XML to flat files
python etl/parse_pubmed_xml.py data/pubmed-raw/ --output-dir data/pubmed

# 3. Load into Samyama (via Rust loader — fast)
cargo run --release --example pubmed_loader -- --data-dir data/pubmed
```

## Schema

- **Article** (37M): pmid, title, abstract, journal, pub_date
- **Author** (30M): name (deduped by last_name + fore_name)
- **MeSHTerm** (30K): descriptor_id, name
- **Chemical** (500K): registry_number, name
- **Journal** (30K): title
- **Grant** (1M): grant_id, agency, country

## Edges

- AUTHORED_BY: Article → Author (~150M)
- ANNOTATED_WITH: Article → MeSHTerm (~400M)
- MENTIONS_CHEMICAL: Article → Chemical (~126M)
- PUBLISHED_IN: Article → Journal (~37M)
- CITES: Article → Article (~70M)
- FUNDED_BY: Article → Grant (~5M)

## Scale

~75M nodes, ~788M edges. Part of the Samyama Billion-Node plan (ADR-016).
