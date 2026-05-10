#! /usr/bin/env bash

set -e

# install dependencies for the project 
pip install -r requirements.txt

# project in production, collect static files
python manage.py collectstatic --no-input

# apply and run the database migrations
python manage.py migrate


