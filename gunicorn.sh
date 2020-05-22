#!/bin/sh

cd `dirname $0`
gunicorn flask_tousan:app -c config/gunicorn_settings.py