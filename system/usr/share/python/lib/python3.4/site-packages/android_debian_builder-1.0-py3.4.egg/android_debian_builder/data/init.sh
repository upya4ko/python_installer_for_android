#!/bin/sh
# -*- mode: sh; tab-width: 4; indent-tabs-mode: nil -*-
PATH=/bin:/usr/bin:/sbin:/usr/sbin

do_start() {
    # Add your own setup commands here. For example:
    # /etc/init.d/ssh start
    echo "Starting Debian."
}

do_login() {
    # Take necessary steps to launch the desired shell environment.
    bash --login
}

do_stop() {
    # Add your own teardown commands here. For example:
    # /etc/init.d/ssh stop
    echo "Stopping Debian."
}

case "$1" in
    start) do_start;;
    login) do_login;;
    stop) do_stop;;
    *) echo "Usage: init.rc start | stop";;
esac
