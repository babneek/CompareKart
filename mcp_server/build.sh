#!/bin/bash
set -e

echo "Starting build process..."

# Upgrade pip first
python -m pip install --upgrade pip

# Install build dependencies
pip install setuptools wheel

# Install requirements
pip install -r requirements.txt

echo "Build completed successfully!"
