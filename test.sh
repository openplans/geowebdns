#!/bin/bash

DBNAME=test_geodns
echo Dropping $DBNAME, if it exists...
dropdb $DBNAME 2>/dev/null
echo Creating $DBNAME ....
createdb -T template_postgis $DBNAME

export CONFIG_PG_SQLALCHEMY=postgres://postgres@localhost/$DBNAME
nosetests --with-doctest

echo Dropping $DBNAME...
dropdb $DBNAME 
