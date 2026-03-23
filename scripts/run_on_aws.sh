#!/bin/bash
# PubMed KG — Full pipeline on AWS spot instance
#
# Instance: r7i.xlarge or r8g.xlarge (4 vCPU, 32 GB RAM, ~$0.08/hr spot)
# Storage: 300 GB gp3 EBS
# Region: ap-south-1
#
# Usage:
#   ssh ubuntu@<instance>
#   bash run_on_aws.sh
#
# Pipeline:
#   1. Download PubMed baseline (101 GB compressed, ~3-4 hours)
#   2. Parse XML → flat files (37M articles, ~7-8 hours)
#   3. Build Rust loader + load into Samyama (75M nodes, ~15-30 min)
#   4. Export snapshot → upload to S3
#
# Total estimated time: ~12 hours
# Total cost: ~$1.00 on spot

set -euo pipefail

WORKDIR="${WORKDIR:-/home/ubuntu/pubmed}"
DATA_DIR="$WORKDIR/data"
RAW_DIR="$DATA_DIR/pubmed-raw"
PARSED_DIR="$DATA_DIR/pubmed-parsed"
SNAPSHOT_DIR="$DATA_DIR/snapshots"

mkdir -p "$RAW_DIR" "$PARSED_DIR" "$SNAPSHOT_DIR"

echo "============================================"
echo "PubMed KG Full Pipeline"
echo "============================================"
echo "Work dir: $WORKDIR"
echo "Disk space: $(df -h / | tail -1 | awk '{print $4}') available"
echo ""

# Step 0: Clone repos if not present
if [ ! -d "$WORKDIR/pubmed-kg" ]; then
    echo "Step 0: Cloning repos..."
    cd "$WORKDIR"
    git clone git@github.com:samyama-ai/pubmed-kg.git
    git clone git@github.com:samyama-ai/samyama-graph.git
    echo "  Repos cloned"
fi

# Step 1: Download PubMed baseline
echo ""
echo "Step 1: Downloading PubMed baseline..."
cd "$WORKDIR/pubmed-kg"
python3 etl/download_pubmed.py --output-dir "$RAW_DIR" 2>&1 | tee "$WORKDIR/download.log"

echo ""
echo "  Download complete. Files: $(ls $RAW_DIR/*.xml.gz 2>/dev/null | wc -l)"
echo "  Total size: $(du -sh $RAW_DIR | cut -f1)"

# Step 2: Parse XML → flat files
echo ""
echo "Step 2: Parsing PubMed XML..."
python3 etl/parse_pubmed_xml.py "$RAW_DIR" --output-dir "$PARSED_DIR" 2>&1 | tee "$WORKDIR/parse.log"

echo ""
echo "  Parsed files:"
ls -lh "$PARSED_DIR"/*.txt

# Step 3: Build and run Rust loader
echo ""
echo "Step 3: Building Rust loader..."
cd "$WORKDIR/samyama-graph"

# Ensure Rust is installed
if ! command -v cargo &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

cargo build --release --example pubmed_loader 2>&1 | tail -3

echo ""
echo "Step 4: Loading PubMed into Samyama..."
cargo run --release --example pubmed_loader -- \
    --data-dir "$PARSED_DIR" \
    --snapshot "$SNAPSHOT_DIR/pubmed-full.sgsnap" \
    2>&1 | tee "$WORKDIR/load.log"

# Step 5: Upload snapshot to S3
echo ""
echo "Step 5: Uploading snapshot to S3..."
aws s3 cp "$SNAPSHOT_DIR/pubmed-full.sgsnap" \
    s3://samyama-data/snapshots/pubmed-full.sgsnap \
    --storage-class STANDARD_IA

# Also upload parsed flat files (useful for re-processing)
aws s3 sync "$PARSED_DIR" s3://samyama-data/raw/pubmed/ \
    --storage-class STANDARD_IA

echo ""
echo "============================================"
echo "Pipeline complete!"
echo "============================================"
echo "  Snapshot: $SNAPSHOT_DIR/pubmed-full.sgsnap"
echo "  S3: s3://samyama-data/snapshots/pubmed-full.sgsnap"
echo "  Logs: $WORKDIR/*.log"
