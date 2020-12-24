inotifywait -e modify -r -m . --exclude index.html  | while read f; do python3 crpopular-graphs.py; echo "built"; done
