==================================================
How to update the getall script, in 27 easy steps:
==================================================

By Nathaniel Case

Many of the files we download here are inherently unstable.  Time passes, and
information is no longer as relevant as it once was.  To combat this, the
servers we query may update old files, or make new files available to refresh
the information to a current state.  I have tried to keep the volatile bits
out of the main loops as much as possible, but if something changes radically
or new information is requested, this document hopes to address any questions.

Note that this does not actually tell you how to get the data into geowebdns,
as that is handled by the importhooks.py script

New Files
---------

With respect to adding new sources, the easiest way to do that is to add
another line to the first for loop with the url of the new file.  For many
urls, this can get tedious and clutter the script, but if the goal is just to
get something downloaded, this will work.

The other way to add files, and the suggested one if there are multiple files
coming from a single source, is to make a new loop to download all of the
relevant files.  A typical loop looks something like this::

    SHORTURL=http://site.com/folder/
    PREFIX=map_
    SUFFIX=_2010.zip
    for NAME in file1 file2 file3 file4; do
        FILE=$PREFIX$NAME$SUFFIX
        URL=$SHORTURL$FILE
        download $FILE $URL
    done

SHORTURL is the folder all the files are commonly located in (or a common
parent folder), PREFIX and SUFFIX are common beginnings and ends of files
(if applicable), hopefully including the date-dependent information to make
updating the files easier.  For each of file1, file2, file3, and file4, the
loop adds the common components back on to the files and sends the now-
completed FILE and URL to download, the common downloading function.  More
advanced loops can be generated from this for special needs or servers with
interesting paths or multiple subfolders.

Updating Files
--------------

The easier task is to update the existing files when the naming scheme changes.
taking the previous example, we start with the following::

    SHORTURL=http://www.site.com/folder/
    PREFIX=map_
    SUFFIX=_2010.zip
    for NAME in file1 file2 file3 file4; do
        FILE=$PREFIX$NAME$SUFFIX
        URL=$SHORTURL$FILE
        download $FILE $URL
    done

Let's say that in 2011, the only thing that changes is the files change from
*_2010.zip to *_2011.zip.  Change SUFFIX to _2011.zip, and the new files will
get downloaded.  If the location of the files were moved from
http://www.site.com/folder/ to http://www2.site.com/other_folder/ along with
the year, simply change SHORTURL with the new common location, and go on your
way.
