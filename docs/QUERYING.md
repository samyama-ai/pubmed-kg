# Querying the PubMed KG

Ways to ask the graph questions, once it's loaded into the `pubmed` tenant on a running engine
(see [GETTING_STARTED.md](../GETTING_STARTED.md)).

> **Note:** this is a **billion-edge** KG. The examples below are the repo's showcase **patterns** — run
> them against your loaded `pubmed` tenant on a suitably-sized engine to see current results (they are not
> pinned to exact live numbers here).

---

## 1. HTTP API (`POST /api/query`)

Top MeSH terms co-occurring with cancer research:

```bash
curl -s -X POST http://localhost:8080/api/query -H 'Content-Type: application/json' -d '{
  "graph": "pubmed",
  "query": "MATCH (a:Article)-[:ANNOTATED_WITH]->(:MeSHTerm {name: \"Neoplasms\"}) MATCH (a)-[:ANNOTATED_WITH]->(m:MeSHTerm) WHERE m.name <> \"Neoplasms\" RETURN m.name, count(DISTINCT a) AS articles ORDER BY articles DESC LIMIT 5"
}'
```

Most-cited articles:

```bash
curl -s -X POST http://localhost:8080/api/query -H 'Content-Type: application/json' -d '{
  "graph": "pubmed",
  "query": "MATCH (a:Article)<-[:CITES]-(citing:Article) RETURN a.title, count(citing) AS citations ORDER BY citations DESC LIMIT 10"
}'
```

## 2. Samyama CLI (Redis wire protocol, `:6379`)

```bash
redis-cli -p 6379 GRAPH.QUERY pubmed \
  "MATCH (a:Article)-[:PUBLISHED_IN]->(j:Journal) RETURN j.name, count(a) AS articles ORDER BY articles DESC LIMIT 5"
```

## 3. MCP (not shipped in this repo)

This repo doesn't include a bespoke MCP server (`mcp_server/` has no `server.py`). To expose the tenant
over MCP, use the generic server from the `samyama` package:

```bash
pip install samyama
claude mcp add pubmed -- samyama-mcp-serve --url http://localhost:8080 --graph pubmed
```

---

## More queries
See the [Biomedical Benchmark](https://samyama-ai.github.io/samyama-graph-book/biomedical_benchmark.html)
for 100 example queries. PubMed federates with clinicaltrials-kg, pathways-kg and druginteractions-kg for
the cross-KG billion-edge benchmark.
