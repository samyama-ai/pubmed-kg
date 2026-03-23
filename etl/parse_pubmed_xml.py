#!/usr/bin/env python3
"""PubMed XML → Pipe-delimited flat files.

Streams PubMed baseline XML files and extracts:
- articles.txt: PMID, title, abstract, journal, pub_date, pub_year
- authors.txt: PMID, last_name, fore_name, affiliation
- mesh_terms.txt: PMID, descriptor_id, descriptor_name, is_major_topic
- chemicals.txt: PMID, registry_number, substance_name
- citations.txt: citing_pmid, cited_pmid
- grants.txt: PMID, grant_id, agency, country

Output files are pipe-delimited (|), same format as AACT for consistency.

Usage:
    # Parse a single file
    python parse_pubmed_xml.py /path/to/pubmed26n0001.xml.gz --output-dir data/

    # Parse all files in a directory
    python parse_pubmed_xml.py /path/to/baseline/ --output-dir data/

    # Parse with article limit (for testing)
    python parse_pubmed_xml.py /path/to/baseline/ --output-dir data/ --max-articles 100000
"""

import argparse
import gzip
import glob
import os
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict


def parse_pubmed_file(filepath: str, writers: dict, stats: dict, max_articles: int = 0):
    """Parse a single PubMed XML file (gzipped or plain) and write to flat files."""

    if filepath.endswith('.gz'):
        f = gzip.open(filepath, 'rb')
    else:
        f = open(filepath, 'rb')

    try:
        # Stream parse with iterparse for memory efficiency
        context = ET.iterparse(f, events=('end',))
        for event, elem in context:
            if elem.tag != 'PubmedArticle':
                continue

            if max_articles and stats['articles'] >= max_articles:
                break

            mc = elem.find('MedlineCitation')
            if mc is None:
                elem.clear()
                continue

            # PMID
            pmid_el = mc.find('PMID')
            if pmid_el is None or not pmid_el.text:
                elem.clear()
                continue
            pmid = pmid_el.text.strip()

            # Article
            article = mc.find('Article')
            if article is None:
                elem.clear()
                continue

            # Title
            title_el = article.find('ArticleTitle')
            title = ''
            if title_el is not None:
                title = ET.tostring(title_el, encoding='unicode', method='text').strip()
            title = title.replace('|', ' ').replace('\n', ' ')[:500]

            # Abstract
            abstract = ''
            abstract_el = article.find('Abstract')
            if abstract_el is not None:
                parts = []
                for at in abstract_el.findall('AbstractText'):
                    text = ET.tostring(at, encoding='unicode', method='text').strip()
                    label = at.get('Label', '')
                    if label:
                        parts.append(f"{label}: {text}")
                    else:
                        parts.append(text)
                abstract = ' '.join(parts).replace('|', ' ').replace('\n', ' ')[:2000]

            # Journal
            journal_el = article.find('Journal/Title')
            journal = (journal_el.text or '').strip().replace('|', ' ')[:200] if journal_el is not None else ''

            # Publication date
            pub_date = ''
            pub_year = ''
            pd_el = article.find('Journal/JournalIssue/PubDate')
            if pd_el is not None:
                y = pd_el.find('Year')
                m = pd_el.find('Month')
                d = pd_el.find('Day')
                pub_year = y.text if y is not None and y.text else ''
                if pub_year:
                    pub_date = pub_year
                    if m is not None and m.text:
                        pub_date += f"-{m.text}"
                    if d is not None and d.text:
                        pub_date += f"-{d.text}"

            # Write article
            writers['articles'].write(
                f"{pmid}|{title}|{abstract}|{journal}|{pub_date}|{pub_year}\n"
            )
            stats['articles'] += 1

            # Authors
            for author in article.findall('.//Author'):
                ln = author.find('LastName')
                fn = author.find('ForeName')
                aff_el = author.find('AffiliationInfo/Affiliation')
                last_name = (ln.text or '').strip().replace('|', ' ') if ln is not None else ''
                fore_name = (fn.text or '').strip().replace('|', ' ') if fn is not None else ''
                affiliation = (aff_el.text or '').strip().replace('|', ' ')[:300] if aff_el is not None else ''
                if last_name or fore_name:
                    writers['authors'].write(
                        f"{pmid}|{last_name}|{fore_name}|{affiliation}\n"
                    )
                    stats['authors'] += 1

            # MeSH terms
            for mh in mc.findall('.//MeshHeading/DescriptorName'):
                desc_name = (mh.text or '').strip().replace('|', ' ')
                desc_ui = mh.get('UI', '')
                is_major = mh.get('MajorTopicYN', 'N')
                if desc_name:
                    writers['mesh_terms'].write(
                        f"{pmid}|{desc_ui}|{desc_name}|{is_major}\n"
                    )
                    stats['mesh_terms'] += 1

            # Chemicals
            for chem in mc.findall('.//Chemical'):
                substance = chem.find('NameOfSubstance')
                if substance is not None and substance.text:
                    reg_num = (chem.find('RegistryNumber').text or '') if chem.find('RegistryNumber') is not None else ''
                    writers['chemicals'].write(
                        f"{pmid}|{reg_num}|{substance.text.strip().replace('|', ' ')}\n"
                    )
                    stats['chemicals'] += 1

            # Citations (references to other PubMed articles)
            for ref in elem.findall('.//Reference/ArticleIdList/ArticleId'):
                if ref.get('IdType') == 'pubmed' and ref.text:
                    writers['citations'].write(
                        f"{pmid}|{ref.text.strip()}\n"
                    )
                    stats['citations'] += 1

            # Grants
            for grant in article.findall('.//Grant'):
                gid = grant.find('GrantID')
                agency = grant.find('Agency')
                country = grant.find('Country')
                if gid is not None and gid.text:
                    writers['grants'].write(
                        f"{pmid}|{gid.text.strip().replace('|', ' ')}|"
                        f"{(agency.text or '').strip().replace('|', ' ') if agency is not None else ''}|"
                        f"{(country.text or '').strip() if country is not None else ''}\n"
                    )
                    stats['grants'] += 1

            # Free memory
            elem.clear()

    finally:
        f.close()


def main():
    parser = argparse.ArgumentParser(description="PubMed XML → flat files")
    parser.add_argument("input", help="XML file, .gz file, or directory of .xml.gz files")
    parser.add_argument("--output-dir", default="data/pubmed", help="Output directory")
    parser.add_argument("--max-articles", type=int, default=0, help="Max articles (0=all)")
    parser.add_argument("--max-files", type=int, default=0, help="Max XML files to process (0=all)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Determine input files
    if os.path.isdir(args.input):
        files = sorted(glob.glob(os.path.join(args.input, "*.xml.gz")))
        if not files:
            files = sorted(glob.glob(os.path.join(args.input, "*.xml")))
    else:
        files = [args.input]

    if args.max_files:
        files = files[:args.max_files]

    print(f"PubMed XML Parser")
    print(f"  Input: {len(files)} files")
    print(f"  Output: {args.output_dir}")
    if args.max_articles:
        print(f"  Max articles: {args.max_articles:,}")
    print()

    # Open output files with headers
    output_files = {
        'articles': 'articles.txt',
        'authors': 'authors.txt',
        'mesh_terms': 'mesh_terms.txt',
        'chemicals': 'chemicals.txt',
        'citations': 'citations.txt',
        'grants': 'grants.txt',
    }
    headers = {
        'articles': 'pmid|title|abstract|journal|pub_date|pub_year',
        'authors': 'pmid|last_name|fore_name|affiliation',
        'mesh_terms': 'pmid|descriptor_id|descriptor_name|is_major_topic',
        'chemicals': 'pmid|registry_number|substance_name',
        'citations': 'citing_pmid|cited_pmid',
        'grants': 'pmid|grant_id|agency|country',
    }

    writers = {}
    for key, filename in output_files.items():
        path = os.path.join(args.output_dir, filename)
        fh = open(path, 'w', encoding='utf-8')
        fh.write(headers[key] + '\n')
        writers[key] = fh

    stats = defaultdict(int)
    t0 = time.time()

    try:
        for fi, filepath in enumerate(files):
            basename = os.path.basename(filepath)
            t_file = time.time()
            parse_pubmed_file(filepath, writers, stats, args.max_articles)
            elapsed_file = time.time() - t_file

            if (fi + 1) % 10 == 0 or fi == len(files) - 1:
                elapsed_total = time.time() - t0
                rate = stats['articles'] / elapsed_total if elapsed_total > 0 else 0
                print(
                    f"  [{fi+1}/{len(files)}] {basename}: "
                    f"{stats['articles']:,} articles, "
                    f"{stats['authors']:,} authors, "
                    f"{stats['mesh_terms']:,} mesh, "
                    f"{stats['citations']:,} citations "
                    f"({rate:.0f} articles/sec, {elapsed_total:.0f}s)"
                )

            if args.max_articles and stats['articles'] >= args.max_articles:
                print(f"  Reached max articles limit ({args.max_articles:,})")
                break
    finally:
        for fh in writers.values():
            fh.close()

    elapsed = time.time() - t0
    print(f"\n{'='*50}")
    print(f"PubMed Parse Complete")
    print(f"{'='*50}")
    print(f"  Time:       {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"  Files:      {min(fi+1, len(files))}")
    print(f"  Articles:   {stats['articles']:,}")
    print(f"  Authors:    {stats['authors']:,}")
    print(f"  MeSH terms: {stats['mesh_terms']:,}")
    print(f"  Chemicals:  {stats['chemicals']:,}")
    print(f"  Citations:  {stats['citations']:,}")
    print(f"  Grants:     {stats['grants']:,}")
    print(f"\nOutput files in {args.output_dir}/")
    for key, filename in output_files.items():
        path = os.path.join(args.output_dir, filename)
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  {filename:20s} {size_mb:>8.1f} MB")


if __name__ == '__main__':
    main()
