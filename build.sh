#!/usr/bin/env bash
# Install dependencies
pip install -r requirements.txt

# Create database tables
python -c "from app import create_app; from models import db; app = create_app('production'); app.app_context().push(); db.create_all()"
