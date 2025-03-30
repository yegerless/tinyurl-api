#!/bin/bash

sleep 2

alembic upgrade head

python3 ./src/main.py
