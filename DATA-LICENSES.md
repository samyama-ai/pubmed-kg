# Data licences

`LICENSE` in this repository covers the **loader code**. It says nothing about the
upstream data this repository reads and, where a snapshot is published, redistributes.
That gap is what this file closes (samyama-cloud#97).

Each row records what the source's **own terms page** says, with the URL and the date it
was read. Where a source could not be re-verified it says so rather than guessing: an
unverified licence written down as fact is worse than the silence it replaces.

| Source | What we load | What its terms page says | Checked |
|---|---|---|---|
| [PubMed/MEDLINE baseline](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html) | Article metadata (PMID, title, abstract text, journal, dates), author names, MeSH terms, chemicals, grants, citations | NLM Terms and Conditions: free to use and redistribute, with attribution *Courtesy of the U.S. National Library of Medicine*; redistributors must keep the data current or disclose that they have not; no implication of NLM endorsement. Works produced by the U.S. government are not subject to copyright in the United States. | 2026-09-18 |

**The derived graph.** The bibliographic records are freely redistributable under NLM's
terms with the attribution above.

**One open question, and it is about the abstracts.** `etl/parse_pubmed_xml.py` extracts
`abstract` text into the `Article` nodes. NLM's terms cover NLM's own compilation; they do
not grant rights over material a publisher holds copyright in, and **abstract text in
MEDLINE is frequently publisher-copyrighted**. NLM states plainly that it does not give
legal advice on this.

So: the loader and the metadata-only graph are safe to publish. A published `.sgsnap`
that contains abstract text is not obviously safe, and this repository should either
exclude `abstract` from published snapshots or establish the position before shipping
one. Recorded here rather than resolved, because resolving it is a legal question.

## How to read the "derived graph" line

A graph built from several sources carries **all** of their terms at once. The
restrictive ones win: one non-commercial source makes the join non-commercial, one
share-alike source makes the join share-alike. That is why the derived licence below is
not simply the most permissive source in the table.

## If you redistribute

- Keep the attributions named above with the data.
- State which snapshot version you took, so a reader can check it against the source.
- Re-read the terms pages: licences change, and the dates in this table are when we last
  looked.
