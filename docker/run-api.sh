#!/bin/bash

sleep 3

alembic upgrade head

python3 ./src/main.py

# gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000