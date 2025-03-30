#!/bin/bash

sleep 6

cd src

if [[ "${1}" == "celery" ]]; then
#   celery --app=tasks.tasks:celery worker -l INFO
    celery -A links.tasks:celery worker -B --loglevel=INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=links.tasks:celery flower
 fi