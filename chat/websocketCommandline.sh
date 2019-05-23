#!/bin/sh
uwsgi --http :8081 --gevent 100 --module websocket --gevent-monkey-patch --master --processes 4
