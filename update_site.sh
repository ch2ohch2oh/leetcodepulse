#!/bin/bash
set -e

# Get the directory of the script
script_dir=$(dirname "$0")
cd "$script_dir"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "========================================"
echo "Collecting statistics..."
echo "========================================"
python collect_stats.py -v

echo ""
echo "========================================"
echo "Generating site..."
echo "========================================"
# Default output to public/index.html (default of the script)
# You can override this by passing arguments to this script if we forwarded them, 
# but for now we keep it simple.
python generate_site.py

echo ""
echo "Done! Site generated at public/index.html"
