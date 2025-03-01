#!/bin/bash

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix-based systems
    source venv/bin/activate
fi

# Install required packages
pip install -r requirements.txt
