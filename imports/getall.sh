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

# TODO: these NYC data URIs are not permanent, it changes
# every few months when they release new files. They
# apparently don't preserve the old URIs!

for URL in http://www.nyc.gov/html/dcp/download/bytes/nyad_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycc_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycg_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyss_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyed_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nymc_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nybb_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nycd_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nysd_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nypp_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyhc_10aav.zip \
    http://www.nyc.gov/html/dcp/download/bytes/nyha_10aav.zip \
    http://dcatlas.dcgis.dc.gov/download/DCBndyPly.ZIP \
    http://gispubweb.sfgov.org/website/sfshare/catalog/bayarea_cities.zip \
    ; do
    FILE="$(basename $URL)"
    if [ ! -e data/$FILE ] ; then
	echo -n "Downloading $URL..."
        curl --silent -f $URL  > data/$FILE
	if [ "$?" == "0" ]; then
	    echo "OK"
	else
	    echo FAILED
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
