#!/bin/bash

# Create and activate virtual environment (if it doesn't exist)
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

python3 main.py

deactivate # Deactivate virtual environment (after the app finishes)