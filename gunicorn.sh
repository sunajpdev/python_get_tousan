#!/bin/sh

gunicorn flask_tousan:app -c config/gunicorn_settings.py