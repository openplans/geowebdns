#!/bin/bash
# How to use this file:
# First, fetch it, like:
#     $ wget http://bitbucket.org/ianb/geodns/raw/tip/setup-layout.sh
#     $ chmod +x setup-layout.sh
#     $ ./setup-layout.sh geodns-app


if [ -z "$1" ] || [ "$1" = "-h" ] ; then
    echo "Usage: $(basename $0) DIR"
    echo "Creates a layout for the GeoDNS application in the given directory"
    echo "toppcloud must be installed before running this"
    exit 2
fi

DIR="$1"

if ! which toppcloud ; then
    echo "toppcloud is not installed"
    echo "(or toppcloud is not on \$PATH)"
    exit 2
fi

toppcloud init $DIR
pushd $DIR

if [ ! -e src/geodns/.hg ] ; then
    hg clone ssh://hg@bitbucket.org/ianb/geodns src/geodns
fi

if [ ! -e lib/python/.hg ] ; then
    if [ -e lib/python ] ; then
        rmdir lib/python
    fi
    hg clone ssh://hg@bitbucket.org/ianb/geodns-lib lib/python
fi

if [ ! -L app.ini ] ; then
    rm app.ini
    ln -s src/geodns/toppcloud-app.ini app.ini
fi

if [ ! -L static ] ; then
    rmdir static
    ln -s src/geodns/geodns/static static
fi

