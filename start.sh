#!/bin/bash
# Production startup script for Render
export FLASK_ENV=production
export FLASK_DEBUG=False
python app.py