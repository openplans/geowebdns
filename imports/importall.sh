#!/bin/bash

if [ "$1" = "remote" ] ; then
    shift
    CMD="silver run demo.geowebdns.org geodns-import-shp"
else
    CMD="../../../bin/geodns-import-shp"
fi

for F in data/*.zip ; do
    $CMD $F --row-pyfile="geodns.importhooks:import_file_{{file_name}}" "$@" || exit 2
done

