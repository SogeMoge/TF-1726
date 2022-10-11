#!/bin/bash

up() {
    /home/sogemoge/.local/bin/podman-compose pull
    /home/sogemoge/.local/bin/podman-compose up -d
}

down() {
    /home/sogemoge/.local/bin/podman-compose down
}

case $1 in
    up|down) "$1" ;;
esac

exit 0
