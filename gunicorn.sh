#!/bin/sh

SCRIPT_DIR=$(cd $(dirname $0); pwd)
gunicorn flask_tousan:app -c config/gunicorn_settings.py