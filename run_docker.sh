#!/bin/bash
gunicorn --workers 3 --worker-class=gevent --worker-connections=100 -b 0.0.0.0:9341 wsgi:app --timeout 0 -k gevent