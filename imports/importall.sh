#!/bin/bash

if [ "$1" = "remote" ] ; then
    shift
    CMD="silver run demo.geowebdns.org geodns-import-shp"
else
    CMD="../../../bin/geodns-import-shp"
fi

for F in `ls data/*.zip data/*.ZIP 2>/dev/null`; do
    echo -n "importing $F ... "
    $CMD $F --row-pyfile="geodns.importhooks:import_file_{{file_name}}" "$@" || exit 2
done
echo

