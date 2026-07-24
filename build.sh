#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
export FLASK_APP=run.py
flask db upgrade
