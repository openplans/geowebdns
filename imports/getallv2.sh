#!/bin/bash

# Keeps track of the number of files that have failed to download
HAD_FAILURES=0
# Make a 'data' directory if one does not already exist
mkdir -p data

# Due to having several categories of downloads sharing a common download
# method, I spun it out into a function.  This shouldn't need to be changed
# unless you need some need not covered here.
function download {
    # $1 = FILE, $2 = URL, $3 = POSTDATA
    if [ ! -e data/$1 ] ; then
        FILE=$1
        URL=$2
        if [ $# = 3 ]; then
            # If we need to send additional information, append it to $URL.
            URL=$URL?$3
        fi
        echo -n "Downloading $URL..."
        wget --quiet -O data/$FILE $URL
        
        if [ "$?" == "0" ]; then
            echo "OK"
        else
            echo FAILED
            rm -f data/$FILE
            HAD_FAILURES=$(($HAD_FAILURES+1))
        fi
    else
        echo "$FILE exists"
    fi
}


# Skipping these for now, what would census tracts link to?:
#    http://www.nyc.gov/html/dcp/download/bytes/nyct2000_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nycb2000_09bav.zip
# Skipping these fire companies too:
#    http://www.nyc.gov/html/dcp/download/bytes/nyfc_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfb_09bav.zip
#    http://www.nyc.gov/html/dcp/download/bytes/nyfd_09bav.zip

# TODO: these NYC data URIs are not permanent, it changes
# every few months when they release new files. They
# apparently don't preserve the old URIs!

# In the first example, we just have a list of complete URLs to download.
# In general, for one-off additions, add them here; for multiple similar files,
# make a new loop based off one of the later examples.
for URL in \
    http://www.nyc.gov/html/dcp/download/biggapps/DCP_nycdav_001.zip \
    http://dcatlas.dcgis.dc.gov/download/DCBndyPly.ZIP \
    http://gispubweb.sfgov.org/website/sfshare/catalog/bayarea_cities.zip \
    ; do
    FILE="$(basename $URL)"
    download $FILE $URL
done

# In the second example, we have several files coming from the same address,
# so we can make a new loop to alter the URL and build the files' names as we
# go.
# Should the files change, hopefully only the suffix will need to change.  If
# you want to add new sources, add their two-letter code to the for loop.

# NOTE: The name $SHORTURL is used to avoid download clobbering $URL.
SHORTURL=http://www.nyc.gov/html/dcp/download/bytes/
PREFIX=ny
SUFFIX=_10aav.zip
for NAME in ad cc cg ss ed mc bb cd sd pp hc ha; do
    # rebuild the filename
    FILE=$PREFIX$NAME$SUFFIX
    # (ie nyad_10aav.zip)
    FULLURL=$SHORTURL$FILE
    download $FILE $FULLURL
done

# The third section is similar to the second, but also needs to send extra data
# with the requests.  In this case, we loop over the extra data, then send it all
# to the download function.

# NOTE: "926 census_boundaries_shp.zip" and "927 civil_boundaries_shp.zip"
# redirect to a license page.  It is probably skippable given enough skill.
SHORTURL=http://www.nysgis.state.ny.us/gisdata/fileserver/
for FILE in \
    "1122 assembly2002.zip" \
    "1122 congress2002.zip" \
    "1122 senate2002.zip" \
    ; do
    # Chop $FILE into $1 and $2, breaking on spaces.
    set -- $FILE
    DSID=$1
    FILE=$2
    POST="DSID=$DSID&file=$FILE"
    download $FILE $SHORTURL $POST
done

# Another source for multiple files.  This one is again similar toy the
# previous two, but has two pieces of the URL to loop over.

# Ideally, these two variables should be the only two that need to be changed
# as the locations of the files change.
SHORTURL=ftp://ftp2.census.gov/geo/tiger/TIGER2009
PREFIX=tl_2009_
for STATE in \
    "06 CALIFORNIA" \
    "17 ILLINOIS" \
    "33 NEW_HAMPSHIRE" \
    "36 NEW_YORK" \
    ; do
    set -- $STATE
    STATENUM=$1_ # We'll be using this later
    STATE=$STATENUM$2 # The state code (ie 36_NEW_YORK)
    # tabblock = Census Block
    # bg = Block Group (No data since 2000)
    # tract = Census Tract (No data since 2000)
    # cd111 = 111th Congressional District
    # county = County
    # cousub = County Subdivision
    # csa = Combined Statistical Area (Missing for AK, AZ, HI, MO, WY)
    # metdiv = Metropolitan Division (Missing for AL, AK, AZ, AR, CO, CT,
    # GA, HI, ID, IA, KS, KY, LA, ME, MN, MS, MO, MT, NE, NV, NM, NC, ND,
    # OH, OK, OR, RI, SC, SD, TN, UT, VT)
    # cbsa = Metropolitan/Micropolitan Statistical Area
    # place = Place
    # puma1 = Super Public Use Microdata Area (No data since 2000)
    # puma5 = Public Use Microdata Area (No data since 2000)
    # elsd = Elementary School District (Missing for AL, AK, AR, CO, DE,
    # DC, FL, GA, HI, ID, IA, KS, LA, MD, MN, MS, NE, NV, NM, NC, OH, PA,
    # SD, UT, WV, WY)
    # scsd = Secondary School District (Missing for AL, AK, AR, CO, DE,
    # DC, FL, GA, HI, ID, IN, IA, KS, LA, MD, MI, MN, MS, MO, NE, NV, NM,
    # NC, ND, OH, OK, PA, SD, UT, VA, WA, WV, WY)
    # unsd = Unified School District
    # sldu = State Legislative District (Upper Chamber)
    # sldl = State Legislative District (Lower Chamber) (Missing for DC, NE)
    # zcta5 = Zip Code
    # zcta3 = Zip Code
    # Total download (all states) as of 6/15/10 is 7.6GB in 687 files
    # Pipe to census appears to be capped at 500 KB/s making the download 
    # approximately 5.5 hours
    for FILE in \
        tabblock.zip \
        cd111.zip \
        county.zip \
        cousub.zip \
        csa.zip \
        metdiv.zip \
        cbsa.zip \
        place.zip \
        elsd.zip \
        scsd.zip \
        unsd.zip \
        sldu.zip \
        sldl.zip \
        zcta5.zip \
        zcta3.zip \
        ; do
        FILE=$PREFIX$STATENUM$FILE # The whole drawn out filename
                                        # (ie tl_2009_36_cousub.zip)
        FULLURL=$SHORTURL/$STATE/$FILE
        download $FILE $FULLURL
    done
done

# If any of the downloads failed, report it.
if [ "$HAD_FAILURES" == "0" ]; then
    echo "Everything fetched."
else
    echo "Not everything fetched.  $HAD_FAILURES files failed to download."
    exit 1
fi

# Commented to keep time down.  Many states are largely complete, except where noted above
    #"01 ALABAMA" \
    #"02 ALASKA" \
    #"04 ARIZONA" \
    #"05 ARKANSAS" \
    #"08 COLORADO" \
    #"09 CONNECTICUT" \
    #"10 DELAWARE" \
    #"11 DISTRICT_OF_COLUMBIA" \
    #"12 FLORIDA" \
    #"13 GEORGIA" \
    #"15 HAWAII" \
    #"16 IDAHO" \
    #"18 INDIANA" \
    #"19 IOWA" \
    #"20 KANSAS" \
    #"21 KENTUCKY" \
    #"22 LOUISIANA" \
    #"23 MAINE" \
    #"24 MARYLAND" \
    #"25 MASSACHUSETTS" \
    #"26 MICHIGAN" \
    #"27 MINNESOTA" \
    #"28 MISSISSIPPI" \
    #"29 MISSOURI" \
    #"30 MONTANA" \
    #"31 NEBRASKA" \
    #"32 NEVADA" \
    #"34 NEW_JERSEY" \
    #"35 NEW_MEXICO" \
    #"37 NORTH_CAROLINA" \
    #"38 NORTH_DAKOTA" \
    #"39 OHIO" \
    #"40 OKLAHOMA" \
    #"41 OREGON" \
    #"42 PENNSYLVANIA" \
    #"44 RHODE_ISLAND" \
    #"45 SOUTH_CAROLINA" \
    #"46 SOUTH_DAKOTA" \
    #"47 TENNESSEE" \
    #"48 TEXAS" \
    #"49 UTAH" \
    #"50 VERMONT" \
    #"51 VIRGINIA" \
    #"53 WASHINGTON" \
    #"54 WEST_VIRGINIA" \
    #"55 WISCONSIN" \
    #"56 WYOMING" \
