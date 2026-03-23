#!/usr/bin/env python3
"""Download PubMed baseline XML files from NCBI FTP.

Downloads gzipped XML files to a local directory. Supports resume
(skips already-downloaded files) and file limits for testing.

Usage:
    # Download all baseline files (~101 GB)
    python download_pubmed.py --output-dir data/pubmed-raw

    # Download first 10 files (for testing)
    python download_pubmed.py --output-dir data/pubmed-raw --max-files 10

    # Resume interrupted download
    python download_pubmed.py --output-dir data/pubmed-raw
"""

import argparse
import os
import re
import sys
import time
import urllib.request


BASE_URL = "https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"


def list_baseline_files() -> list[str]:
    """Get list of all .xml.gz files from the PubMed FTP baseline directory."""
    print("Fetching file list from NCBI FTP...")
    req = urllib.request.Request(BASE_URL, headers={"User-Agent": "samyama-pubmed-loader/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode()

    files = re.findall(r'(pubmed\d+n\d+\.xml\.gz)', content)
    # Deduplicate and sort
    files = sorted(set(files))
    return files


def download_file(filename: str, output_dir: str) -> bool:
    """Download a single file with resume support."""
    url = BASE_URL + filename
    outpath = os.path.join(output_dir, filename)

    # Skip if already downloaded (basic check by existence)
    if os.path.exists(outpath):
        return False

    tmp_path = outpath + ".tmp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "samyama-pubmed-loader/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(8 * 1024 * 1024)  # 8 MB chunks
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

        os.rename(tmp_path, outpath)
        return True
    except Exception as e:
        print(f"  ERROR downloading {filename}: {e}", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download PubMed baseline")
    parser.add_argument("--output-dir", default="data/pubmed-raw")
    parser.add_argument("--max-files", type=int, default=0, help="0 = all")
    parser.add_argument("--start-from", type=int, default=0, help="Skip first N files")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    files = list_baseline_files()
    if not files:
        print("ERROR: No baseline files found")
        sys.exit(1)

    print(f"Found {len(files)} baseline files")

    if args.start_from:
        files = files[args.start_from:]
        print(f"Starting from file {args.start_from}")
    if args.max_files:
        files = files[:args.max_files]
        print(f"Limiting to {args.max_files} files")

    # Count already downloaded
    existing = sum(1 for f in files if os.path.exists(os.path.join(args.output_dir, f)))
    print(f"Already downloaded: {existing}, remaining: {len(files) - existing}")
    print()

    t0 = time.time()
    downloaded = 0
    skipped = 0

    for i, filename in enumerate(files):
        if download_file(filename, args.output_dir):
            downloaded += 1
        else:
            skipped += 1

        if (i + 1) % 10 == 0 or i == len(files) - 1:
            elapsed = time.time() - t0
            rate = downloaded / elapsed * 3600 if elapsed > 0 else 0
            total_size = sum(
                os.path.getsize(os.path.join(args.output_dir, f))
                for f in os.listdir(args.output_dir)
                if f.endswith('.xml.gz')
            ) / (1024 ** 3)
            print(
                f"  [{i+1}/{len(files)}] Downloaded: {downloaded}, "
                f"Skipped: {skipped}, "
                f"Total: {total_size:.1f} GB, "
                f"Rate: {rate:.0f} files/hr"
            )

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s. Downloaded {downloaded} files, skipped {skipped}.")


if __name__ == "__main__":
    main()
