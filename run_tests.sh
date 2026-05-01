#!/bin/bash
cd /home/sanjay/Projects/DakBabu
source .venv/bin/activate
python -m pytest tests/test_email_formatter.py -v 2>&1
