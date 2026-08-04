# Getting Started — PubMed Knowledge Graph

This is Samyama's **billion-edge** KG: **66.2M nodes / 1.04B edges** from the entire PubMed/MEDLINE
corpus. It is **not** a laptop-scale graph — read the two paths below and pick the one that matches your
hardware.

---

## 1. Prerequisites

- **Python ≥ 3.10** — for the ETL scripts (they use only the standard library; **nothing to `pip install`**).
- **git**
- **Docker** — to run the Samyama engine (HTTP `:8080`, RESP `:6379`).
- **For build-from-source only:** ~**101 GB** of disk for the raw XML, and the **Rust** toolchain +
  the `samyama-graph` engine source (the loader is a Rust example). This realistically needs a big
  machine / AWS box, not a laptop.

## 2. "Install"

No Python install step is needed — the scripts run directly:

```bash
git clone https://github.com/samyama-ai/pubmed-kg.git
cd pubmed-kg
python etl/download_pubmed.py --help      # works as-is (stdlib only, Python >= 3.10)
python etl/parse_pubmed_xml.py --help
```

## 3. Run the engine (Docker)

```bash
docker run --rm -p 8080:8080 -p 6379:6379 public.ecr.aws/f9f6l5u4/samyama-graph:1.1.0
```

## 4. Load the graph — into the `pubmed` tenant

### Option A — snapshot (the only practical path for most people)
```bash
curl -LO https://github.com/samyama-ai/samyama-graph/releases/download/kg-snapshots-v5/pubmed.sgsnap
curl -X POST http://localhost:8080/api/tenants -H 'Content-Type: application/json' \
  -d '{"id":"pubmed","name":"PubMed KG"}'
curl -X POST http://localhost:8080/api/tenants/pubmed/snapshot/import -F "file=@pubmed.sgsnap"
```
> ⚠️ This snapshot is **enormous** (a billion-edge graph). Importing it needs a server with a large
> amount of RAM/disk — it will **not** import on a small/laptop engine. Use a suitably-sized machine.

### Option B — build from source (AWS-scale)
```bash
python etl/download_pubmed.py --output-dir data/pubmed-raw                 # ~101 GB of XML
python etl/parse_pubmed_xml.py data/pubmed-raw/ --output-dir data/pubmed   # XML → columnar files
# the graph load itself is a Rust loader in the samyama-graph engine:
cargo run --release --example pubmed_loader -- --data-dir data/pubmed      # from the samyama-graph repo
```
*(Try a slice first: `python etl/download_pubmed.py --max-files 1` then `parse_pubmed_xml.py --max-articles 10000`.)*

## 5. Ask your first question

Top MeSH terms co-occurring with cancer research:

```bash
curl -s -X POST http://localhost:8080/api/query -H 'Content-Type: application/json' -d '{
  "graph": "pubmed",
  "query": "MATCH (a:Article)-[:ANNOTATED_WITH]->(:MeSHTerm {name: \"Neoplasms\"}) MATCH (a)-[:ANNOTATED_WITH]->(m:MeSHTerm) WHERE m.name <> \"Neoplasms\" RETURN m.name, count(DISTINCT a) AS articles ORDER BY articles DESC LIMIT 5"
}'
```

## 6. The ETL pipeline

- Data source: **PubMed/MEDLINE baseline** from NLM (1,219 XML files, 101 GB compressed).
- `etl/download_pubmed.py` — downloads the baseline XML (stdlib only).
- `etl/parse_pubmed_xml.py` — parses XML → columnar files for the loader (stdlib only).
- The load into the graph is the Rust `pubmed_loader` example in `samyama-graph`.

## Next
- **[docs/QUERYING.md](docs/QUERYING.md)** — HTTP API and the Samyama CLI
- **[Benchmark](https://samyama-ai.github.io/samyama-graph-book/biomedical_benchmark.html)** — 100 queries
