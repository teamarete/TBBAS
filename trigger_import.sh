#!/bin/bash
# One-time script to trigger score import on Railway
# Run this from Railway's CLI or as a one-off command

echo "Starting MaxPreps score import..."
python run_import_now.py
echo "Import complete!"
