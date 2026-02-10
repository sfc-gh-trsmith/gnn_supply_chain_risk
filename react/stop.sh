#!/bin/bash

cd "$(dirname "$0")"

if [ -f .services.pid ]; then
  echo "Stopping services..."
  while read pid; do 
    kill $pid 2>/dev/null || true
  done < .services.pid
  rm .services.pid
  echo "Services stopped."
else
  echo "No services running."
fi
