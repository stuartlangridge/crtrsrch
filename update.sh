#!/bin/bash

echo ==================================================================
echo Critical Role script updater running at $(date)
cd $(dirname $0)
output=$(python3 fetch.py --json-list 2>&1)
changes=$(echo "$output" | awk '/./{if(found) print} /BEGIN MACHINE OUTPUT/{found=1}')
count=$(echo -n "$changes" | grep -c '^')
if [ $count -eq 0 ]; then
    echo Nothing to do
    echo $output
    exit 0
fi
echo $count episodes to process
cache_purge_eps=""
for ytid in $changes; do
    nextep=$(sqlite3 cr.db "select 'C' || campaign || 'E' || episode from episode where ytid='$ytid';")
    cache_purge_eps="$cache_purge_eps $nextep"
done
for f in $changes; do
    echo Deleting episode $f
    sqlite3 cr.db "pragma foreign_keys = ON; delete from episode where ytid = '$f';"
done
echo Parsing downloaded scripts
python3 parser.py
echo Constructing sitemap
python3 sitemap.py
echo Constructing full zip file
zip -q cr_full.zip -r html README.zip.md tojson.py
echo Deploying to live
bash deploy.sh --quiet $cache_purge_eps
echo ==================================================================
