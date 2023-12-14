#!/bin/bash

echo $(dirname $0)

# Install dependencies
python3 -m pip install asyncio
python3 -m pip install argparse
python3 -m pip install playwright

# Navigate to the scripts folder
cd $(dirname $0)/scripts/

python3 tu.py > "${SCRIPT_DIR}/m3u8_urls.txt"

echo "m3u8 grabbed"
