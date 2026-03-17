#!/bin/bash
set -e

python src/db/init_db.py

uvicorn 'src.api.app:app' --host=0.0.0.0 --port=8000

