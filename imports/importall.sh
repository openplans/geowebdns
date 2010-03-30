#!/bin/bash

if [ "$1" = "remote" ] ; then
    shift
    CMD="silver run demo.geowebdns.org geowebdns-import-shp"
else
    CMD="../../../bin/geowebdns-import-shp"
fi

for F in `ls data/*.zip data/*.ZIP 2>/dev/null`; do
    echo -n "importing $F ... "
    $CMD $F --row-pyfile="geowebdns.importhooks:import_file_{{file_name}}" "$@" || exit 2
done
echo

