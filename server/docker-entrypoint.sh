#!/usr/bin/env bash
set -e

if [ "$1" = 'uwsgi' ] || [ "$1" = 'python' ]; then
    cd ${APP_DIR}
    # Start Apache Spark on port 8081
    bash start-master.sh --webui-port 8081
    # Start the container command
    exec gosu nlp "$@"
fi

exec "$@"
