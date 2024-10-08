#!/bin/sh

set -e
  
host="$1"
shift
  
until curl -o /dev/null -s $host
do
  >&2 echo "$host is unavailable - sleeping"
  sleep 5
done
  
>&2 echo "Service is up - executing command"
exec "$@"