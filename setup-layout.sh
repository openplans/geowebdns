#!/bin/bash
# How to use this file:
# First, fetch it, like:
#     $ wget https://github.com/openplans/geowebdns
#     $ cd geowebdns
#     $ chmod +x setup-layout.sh
#     $ ./setup-layout.sh geowebdns-app


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

if [ ! -e src/geowebdns/.git ] ; then
    git clone git@github.com:openplans/geowebdns.git src/geowebdns
fi

if [ ! -e src/geoalchemy/.hg ] ; then
    hg clone ssh://hg@bitbucket.org/ianb/geoalchemy src/geoalchemy
fi

if [ ! -e lib/python/.hg ] ; then
    if [ -e lib/python ] ; then
        rmdir lib/python
    fi
    git clone git@github.com:openplans/geowebdns-lib.git lib/python
fi

if [ ! -L app.ini ] ; then
    rm app.ini
    ln -s src/geowebdns/silver-app.ini app.ini
fi

if [ ! -L static ] ; then
    rmdir static
    ln -s src/geowebdns/geowebdns/static static
fi

cd bin
for BINFILE in ../lib/python/bin/*; do
    if [ ! -e `basename $BINFILE` ]; then
        ln -s $BINFILE .
    fi
done
cd -

