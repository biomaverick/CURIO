#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt
streamlit run app.py
