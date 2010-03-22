#!/bin/bash
# How to use this file:
# First, fetch it, like:
#     $ wget http://bitbucket.org/ianb/geodns/raw/tip/setup-layout.sh
#     $ chmod +x setup-layout.sh
#     $ ./setup-layout.sh geodns-app


if [ -z "$1" ] || [ "$1" = "-h" ] ; then
    echo "Usage: $(basename $0) DIR"
    echo "Creates a layout for the GeoDNS application in the given directory"
    echo "silverlining must be installed before running this"
    exit 2
fi

DIR="$1"

if ! which silver ; then
    echo "silverlining is not installed"
    echo "(or silver is not on \$PATH)"
    exit 2
fi

silver init $DIR
pushd $DIR

if [ ! -e src/geodns/.hg ] ; then
    hg clone ssh://hg@bitbucket.org/slinkp/geodns src/geodns
fi

if [ ! -e src/geoalchemy/.hg ] ; then
    hg clone ssh://hg@bitbucket.org/ianb/geoalchemy src/geoalchemy
fi

if [ ! -e lib/python/.hg ] ; then
    if [ -e lib/python ] ; then
        rmdir lib/python
    fi
    hg clone ssh://hg@bitbucket.org/ianb/geodns-lib lib/python
fi

if [ ! -L app.ini ] ; then
    rm app.ini
    ln -s src/geodns/silver-app.ini app.ini
fi

if [ ! -L static ] ; then
    rmdir static
    ln -s src/geodns/geodns/static static
fi

if [ ! -L bin ] ; then
    mv bin bin.tmp
    ln -s lib/python/bin bin
    mv bin.tmp/* bin/
    rmdir bin.tmp
fi

