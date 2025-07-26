#!/usr/bin/env bash
set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements.txt

# Create database tables
