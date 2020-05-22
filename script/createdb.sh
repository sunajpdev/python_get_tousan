#!/bin/sh

$ sudo su - postgres
$ createuser app_user
$ createdb web


$ psql -c "alter role app_user with password 'app_user9913';"