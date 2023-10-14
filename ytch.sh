#!/bin/bash

echo $(dirname $0)

python3 -m pip install requests

cd $(dirname $0)/scripts/

python3 ytg.py > ../ytcheck.m3u

echo m3u grabbed
