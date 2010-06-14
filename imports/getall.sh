#!/bin/bash

# Skipping these for now, what would census tracts link to?:
#    http://www.nyc.gov/html/dcp/download/bytes/nyct2000_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nycb2000_09bav.zip
# Skipping these fire companies too:
#    http://www.nyc.gov/html/dcp/download/bytes/nyfc_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfb_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfd_09bav.zip

HAD_FAILURES=0
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
    http://gispubweb.sfgov.org/website/sfshare/catalog/bayarea_cities.zip \
    ; do
    FILE="$(basename $URL)"
    if [ ! -e data/$FILE ] ; then
        curl --silent -f $URL  > data/$FILE
	if [ "$?" != "0" ]; then
	    echo failed to download $URL
	    rm -f data/$FILE
	    HAD_FAILURES=1
	fi
    else
        echo "$FILE exists"
    fi
done

if [ "$HAD_FAILURES" == "0" ]; then
    echo "Everything fetched."
else
    echo "Not everything fetched."
    exit 1
fi
