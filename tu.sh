#!/bin/bash

echo $(dirname $0)

# Install dependencies

python3 -m pip install playwright
python3 -m pip install requests

# Navigate to the scripts folder
cd $(dirname $0)/scripts/

python3 tu.py > ../m3u8_urls.txt

echo m3u8 grabbed
