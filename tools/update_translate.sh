#!/bin/sh
if [ 1 -gt $# ];
then
    echo "Usage: $0 LOCALE";
    exit;
fi;

pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app
pybabel update -i messages.pot -d app/translations -l $1

