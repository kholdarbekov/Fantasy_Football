#!/usr/bin/env bash
DJANGO_SETTINGS_MODULE=soccer.settings.dev \
DJANGO_SECRET_KEY='2*+cf3-p93@572xtlyovps8k^n+ckob&2kw&no!r_)^(6jmo$@' \
DATABASE_NAME=soccer_db \
DATABASE_USER=soccer_db_usr \
DATABASE_PASSWORD="soccer_db_usr_12345" \
PIP_REQUIREMENTS=dev.txt \
docker-compose up --detach --build