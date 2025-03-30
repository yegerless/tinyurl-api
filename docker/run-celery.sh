#!/bin/bash

sleep 4

cd src

if [[ "${1}" == "celery" ]]; then
    celery -A links.tasks:celery worker -B --loglevel=INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=links.tasks:celery flower
 fi