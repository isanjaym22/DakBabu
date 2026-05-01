#!/bin/bash
cd /home/sanjay/Projects/DakBabu
source .venv/bin/activate
python -m pytest tests/ -v > test_results.txt 2>&1
