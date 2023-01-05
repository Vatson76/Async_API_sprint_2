#!/usr/bin/env bash

set -e

uwsgi --strict --ini uwsgi/uwsgi.ini
