#!/bin/bash

# Skipping these for now, what would census tracts link to?:
#    http://www.nyc.gov/html/dcp/download/bytes/nyct2000_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nycb2000_09bav.zip
# Skipping these fire companies too:
#    http://www.nyc.gov/html/dcp/download/bytes/nyfc_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfb_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfd_09bav.zip

mkdir -p data
for URL in http://www.nyc.gov/html/dcp/download/bytes/nyad_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycc_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycg_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyss_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyed_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nymc_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nybb_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycd_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nysd_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nypp_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyhc_09bav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyha_09bav.zip \
    http://dcatlas.dcgis.dc.gov/download/DCBndyPly.ZIP \
    ; do
    FILE="$(basename $URL)"
    if [ ! -e data/$FILE ] ; then
        wget $URL  -O data/$FILE
    else
        echo "$FILE exists"
    fi
done
echo "Everything fetched."
