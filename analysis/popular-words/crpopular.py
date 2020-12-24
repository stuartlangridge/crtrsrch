#!/usr/bin/env python3

import sqlite3
import os
import nltk
import json
import time
import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
nltk.download('stopwords')
nltk.download('punkt')

STOPS = stopwords.words() + ["amp", "gt", "lt"]
FILLER = ["like", "yeah", "right", "ok", "okay", "oh"]

saved = os.path.join(os.path.dirname(__file__), "crpopular.json")
saved_tmp = saved + ".tmp"

try:
    with open(saved) as fp:
        data = json.load(fp)
        for sp in data["speakers"]:
            data["speakers"][sp]["words"] = Counter(data["speakers"][sp]["words"])
            data["speakers"][sp]["pairs"] = Counter(data["speakers"][sp]["pairs"])
except (FileNotFoundError, json.decoder.JSONDecodeError):
    data = {"upto": 0, "speakers": {}}

db = sqlite3.connect('file:/home/aquarius/Documents/Reference/Critical%20Role/cr.db?mode=ro', uri=True)
crs = db.cursor()
crs.execute("select max(id) from line")
maxline = crs.fetchall()[0][0]
crs.execute("""select l.text, s.name, l.id
    from line l
    inner join speaker2line s2l on l.id=s2l.line_id
    inner join speaker s on s2l.speaker_id = s.id
    where l.id > ?
    order by l.id""", (data["upto"], ))

inc = 0
start = datetime.datetime.now()
start_upto = data["upto"]
for text, speaker, lid in crs:
    if speaker not in data["speakers"]:
        data["speakers"][speaker] = {"words": Counter(), "pairs": Counter()}
    text_tokens = [word.lower() for word in word_tokenize(text) if word.isalnum()]
    tokens_without_sw = [
        word for word in text_tokens
        if word not in STOPS
        and word not in FILLER]
    pairs = [
        (text_tokens[i], text_tokens[i + 1])
        for i in range(len(text_tokens) - 1)]
    pairs = ["{} {}".format(*p) for p in pairs 
        if p[0] not in STOPS and p[0] not in FILLER
        and p[1] not in STOPS and p[1] not in FILLER]
    data["speakers"][speaker]["words"] += Counter(tokens_without_sw)
    data["speakers"][speaker]["pairs"] += Counter(pairs)
    data["upto"] = lid
    inc += 1
    if inc % 1000 == 0:
        inc = 0
        with open(saved_tmp, mode="w") as fp:
            json.dump(data, fp, indent=2)
        os.rename(saved_tmp, saved)
        current = datetime.datetime.now()
        diff = current - start
        frac = lid / maxline
        this_time_frac = (lid - start_upto) / (maxline - start_upto)
        togo = (diff / this_time_frac) - diff
        print(f"{lid} / {maxline} ({round(100 * frac, 2)}%, {togo})")

with open(saved, mode="w") as fp:
    json.dump(data, fp, indent=2)
print("complete")
