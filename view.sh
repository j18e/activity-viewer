#!/bin/bash -eu

cleanup() {
    docker-compose down
}

trap cleanup EXIT

docker-compose up -d
sleep 3
open -a firefox -g "http://localhost:3000/d/a/activity"

while true; do
    sleep 10
done

