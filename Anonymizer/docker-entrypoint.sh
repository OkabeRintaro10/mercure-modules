#!/usr/bin/env bash
set -Eeo pipefail
echo "-- Starting anonymizer..."
python anonymizer.py $MERCURE_IN_DIR $MERCURE_OUT_DIR
echo "-- Anonymizer finished"