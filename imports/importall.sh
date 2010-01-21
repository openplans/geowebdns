#!/bin/bash

if [ "$1" = "remote" ] ; then
    CMD="toppcloud run --host=geodns.open311.org"
else
    CMD="../../../bin/geodns-import-shp"

for F in data/*.zip ; do
    $CMD $F --row-pyfile="geodns.importhooks:import_file_{{file_name}}" "$@" || exit 2
done

