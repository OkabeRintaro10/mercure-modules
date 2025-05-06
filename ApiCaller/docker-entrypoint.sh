#!/usr/bin/env bash
set -Eeo pipefail
echo "-- Starting api_call.."
python api_call.py $MERCURE_IN_DIR $MERCURE_OUT_DIR
echo "-- api_call finished"