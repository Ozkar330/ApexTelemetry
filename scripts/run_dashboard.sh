#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.
echo "Starting ApexTelemetry Dashboard..."
echo "Access at: http://127.0.0.1:8050"
.venv/bin/python src/dashboard_app.py
