#!/usr/bin/env python3
import re
import os
import json
import html
import bleach
import sqlite3


def parse_time(t):
    parts = t.split(":")
    h = int(parts[0])
    m = int(parts[1])
    parts = parts[2].split(".")
    s = int(parts[0])
    ms = int(parts[1])
    return (h, m, s, ms)


MISSPELLINGS = {
    "ASLHEY": "ASHLEY",
    "ASHELY": "ASHLEY",
    "AHSLEY": "ASHLEY",
    "AHSLY": "ASHLEY",
    "ASHLY": "ASHLEY",
    "ASHEY": "ASHLEY",
    "MARISA": "MARISHA",
    "MAIRSHA": "MARISHA",
    "MAISHA": "MARISHA",
    "MARIASHA": "MARISHA",
    "MARIHSA": "MARISHA",
    "MARIHSHA": "MARISHA",
    "MARIRSHA": "MARISHA",
    "MARISAH": "MARISHA",
    "MARISAHA": "MARISHA",
    "MARISH": "MARISHA",
    "MARISHIA": "MARISHA",
    "MARISSA": "MARISHA",
    "MARSHA": "MARISHA",
    "MARSHIA": "MARISHA",
    "MARSIAH": "MARISHA",
    "MARSIHA": "MARISHA",
    "MATISHA": "MARISHA",
    "MRAISHA": "MARISHA",
    "LAIRA": "LAURA",
    "LAUAR": "LAURA",
    "LAUDA": "LAURA",
    "MAT": "MATT",
    "MATR": "MATT",
    "SAN": "SAM",
    "SASM": "SAM",
    "SMA": "SAM",
    "TAIESIN": "TALIESIN",
    "TAILESIN": "TALIESIN",
    "TALEISIN": "TALIESIN",
    "TALEISN": "TALIESIN",
    "TALESIN": "TALIESIN",
    "TALIEISIN": "TALIESIN",
    "TALIEISN": "TALIESIN",
    "TALISAN": "TALIESIN",
    "TALISEN": "TALIESIN",
    "TALISIEN": "TALIESIN",
    "TALISIN": "TALIESIN",
    "TARVIS": "TRAVIS",
    "TAVIS": "TRAVIS",
    "TRAIS": "TRAVIS",
    "TRAIVS": "TRAVIS",
    "TRAVIA": "TRAVIS",
    "TRAVS": "TRAVIS"
}


def namesplit(s):
    if " " in s:
        if "," in s:  # split on commas
            ret = []
            for part in s.split(","):
                ret += namesplit(part)
        elif " AND " in s:  # split on AND
            ret = []
            for part in s.split(" AND "):
                ret += namesplit(part)
        elif " and " in s:  # split on and
            ret = []
            for part in s.split(" and "):
                ret += namesplit(part)
        else:  # remove all lower-case (for "(whispering) LIAM:")
            removed = re.sub(r"[^A-Z]", "", s)
            if removed == s:
                if s.startswith("-"):
                    s = [s[1:]]
                ret = [s]
            else:
                ret = namesplit(removed)
    else:
        ret = [s.strip()]
        if ret[0].startswith("-"):
            ret[0] = ret[0][1:]
    for i in range(len(ret)):
        if ret[i] in MISSPELLINGS:
            ret[i] = MISSPELLINGS[ret[i]]
    return [x for x in ret if x]


assert(namesplit("STUART") == ["STUART"])
assert(namesplit("(whispering) STUART") == ["STUART"])
assert(namesplit("(whispering) STUART (annoyingly)") == ["STUART"])
assert(namesplit("STUART AND MATT") == ["STUART", "MATT"])
assert(namesplit("STUART and MATT") == ["STUART", "MATT"])
assert(namesplit("STUART AND MATT AND LAURA") == ["STUART", "MATT", "LAURA"])
assert(namesplit("STUART and MATT and LAURA") == ["STUART", "MATT", "LAURA"])
assert(namesplit("STUART, MATT AND LAURA") == ["STUART", "MATT", "LAURA"])
assert(namesplit("STUART, MATT, AND LAURA") == ["STUART", "MATT", "LAURA"])
assert(namesplit("STUART, ASLHEY, AND MARISA") == ["STUART", "ASHLEY", "MARISHA"])
assert(namesplit("-LAURA") == ["LAURA"])


def parse(file):
    def process(plines, character):
        # print("----PROCESS", plines)
        c = character
        try:
            idx = int(plines[0])
        except ValueError: # some vtt files don't have indexes
            idx = 0
            plines = [""] + plines
        time = list(plines[1].split(" --> "))
        if " " in time[1]: time[1] = time[1].split(" ")[0] # "line:15%" at end of line; ignore
        text = []
        # print("before doing lines", plines)
        for pline in plines[2:]:
            # print("do line", pline)
            m = re.match(r"^(?P<name>([A-Za-z-]+,?\s)*[A-Z-]+(,?[A-Za-z-]+,?\s)*): (?P<text>.*)$", pline)
            if m:
                parsedc = m.groupdict()["name"]
                c = namesplit(parsedc)
                text = m.groupdict()["text"]
                transcript.append({
                    "character": c,
                    "text": [text],
                    "time": time
                })
            else:
                # print("  append to previous")
                if transcript: # skip any text which is first and not a person
                    transcript[-1]["text"].append(pline)
                    transcript[-1]["time"][1] = time[1]
        # print("----END", transcript[-2:])
        return c

    transcript = []
    character = None
    with open(file, encoding="utf-8") as fp:
        in_intro = True
        accum = []
        for line in fp.readlines():
            l = line.strip()
            if l:
                accum.append(l)
            else:
                if in_intro:
                    in_intro = False
                    accum = []
                else:
                    character = process(accum, character)
                    accum = []
        if accum:
            process(accum)
    # now post-process to join items together
    newtranscript = []
    for t in transcript:
        tt = []
        for line in t["text"]:
            tt.append(line)
            if line.endswith("."):
                tt.append("\n")
            else:
                tt.append(" ")
        all_html = "".join(tt).strip()
        clean_html = bleach.clean(html.unescape(all_html))

        # now split into separate sentences (doesn't cater for ?! ends but
        # that's OK; it means that "are you OK? Yes I am. That's cool." will
        # be two sentences rather than three.
        sentences = ["{}.".format(x) for x in clean_html.split(".\n")]
        sentences[-1] = sentences[-1][:-1]

        for s in sentences:
            ss = s.strip()
            if not ss: continue
            clean_text = bleach.clean(html.unescape(ss), tags=[])
            nt = {
                "character": t["character"],
                "start": parse_time(t["time"][0]),
                "end": parse_time(t["time"][1]),
                "text": s,
                "text_text": clean_text
            }
            newtranscript.append(nt)

    # for t in transcript:
    #    print("{character}: {text}".format(**t))
    return newtranscript


HARDCODED = {
    "OJ81ydo91cw": {
        "title": "Critical Role's Critmas!",
        "campaign": "1", "episode": "OJ81ydo91cw"
    },
    "7J4fg79Utsk": {
        "title": "Why I Love Critical Role (Fan Submissions)",
        "campaign": "1", "episode": "7J4fg79Utsk"
    },
    "tasz1xUVLhg": {
        "title": "Battle Royale One-Shot",
        "campaign": "1", "episode": "tasz1xUVLhg"
    },
    "5UwEc10_DcI": {
        "title": "Visit The Slayer’s Cake In Downtown Whitestone!",
        "campaign": "1", "episode": "5UwEc10_DcI"
    },
    "LgHm3Ct0Zh0": {
        "title": "The Return of Liam!",
        "campaign": "1", "episode": "LgHm3Ct0Zh0"
    },
    "LHita2t54xY": {
        "title": "Liam's Quest: Full Circle",
        "campaign": "1", "episode": "LHita2t54xY"
    },
    "uw1crQ1d9AU": {
        "title": "Cindergrove Revisited",
        "campaign": "1", "episode": "46"
    },
    "4FI8qB-yh-w": {
        "title": "Critical Role RPG Show Q&A and Battle Royale!",
        "campaign": "1", "episode": "4FI8qB"
    },
    "98ZZ_Tw4sSI": {
        "title": "Pants Optional Critmas",
        "campaign": "1", "episode": "98ZZ_Tw4sSI"
    },
    "u8MRyyFDX3c": {
        "title": "TO THE POOP! - The Goblins (Pathfinder)",
        "campaign": "1", "episode": "u8MRyyFDX3c"
    },
    "mHfXAXM4O3E": {
        "title": "Check Out CRITICAL ROLE's New Intro!",
        "campaign": "1", "episode": "mHfXAXM4O3E"
    },
    "0rrj1v7lsxM": {
        "title": "Live From San Diego Comic-Con 2017",
        "campaign": "1", "episode": "0rrj1v7lsxM"
    },
    "DTOGH6M6INE": {
        "title": "Thursday By Night One-Shot",
        "campaign": "1", "episode": "DTOGH6M6INE"
    },
    "kLnvrocetq8": {
        "title": "Grog's One-Shot",
        "campaign": "1", "episode": "kLnvrocetq8"
    },
    "qA4-q4gk_yY": {
        "title": "Hearthstone One-Shot",
        "campaign": "1", "episode": "qA4-q4gk_yY"
    },
    "q3BGg0d8DvU": {
        "title": "Epic Level Battle Royale One-Shot",
        "campaign": "1", "episode": "q3BGg0d8DvU"
    },
    "9jbGshiuFs4": {
        "title": "Marisha's Honey Heist",
        "campaign": "1", "episode": "9jbGshiuFs4"
    },
    "rnq3VBQu_kI": {
        "title": "Bar Room Blitz One-Shot",
        "campaign": "1", "episode": "rnq3VBQu_kI"
    },
    "eXPu1wk-Ev4": {
        "title": "Thursday By Night One-Shot Part 2",
        "campaign": "1", "episode": "eXPu1wk-Ev4"
    }
}

INDEX_HEADER = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Critical Role linkable transcripts</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<main>
    <h1>Critical Role linkable transcripts</h1>

    <p><a href="../">Search these transcripts</a></p>

    <div id="list">
    <ul>
"""

HEADER = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Critical Role Campaign {campaign} Episode {episode} "{title}" linkable transcript</title>

<link rel="stylesheet" href="../style.css">
</head>
<body>
<main>
    <h1>Critical Role linkable transcripts</h1>
    <h2>Campaign {campaign} Episode {episode}</h2>
    <h2>{title}</h2>

    <div id="lines">
"""

UNPROCESSED_WARNING = """<p class="unprocessed-warning">It looks like this
transcript is the
<a href="https://critrole.com/live-closed-captions-on-twitch/">live
closed captions</a> from Twitch, and hasn't yet been processed by the
transcript team. This means that searching won’t work very well against it
yet, and nor will searching by character. It will update in time; be patient,
<a href="https://crtranscript.tumblr.com/post/186968699597/how-to-submit-corrections-maybe-put-the#notes">they
work very hard</a>.</p>"""

FOOTER = """
    </div><!-- lines -->
    <footer>
        <p>
            <a href="index.html">list of episodes</a>
            |
            <a href="../">search transcripts</a>
        </p>
        <p>This is an <a href="https://kryogenix.org/">@sil</a> thing.</p>
        <p>And a <a href="https://critrole.com/">Critical Role</a>
        thing, of course.</p>
        <p>Mostly a Critical Role thing. And a CRTranscript thing.
        Stuart didn't really have to do much.</p>
    </footer>
</body>
</html>"""

LINE_DT = """<dt><a id="{lid}" href="#{lid}">#</a> <strong>{character}</strong></dt>\n"""
LINE_DD = """<dd>{text_nl} <a href="{yt}">&rarr;</a></dd>\n"""
INDEX_LINE = ('<li><a href="cr{campaign}-{episode}.html">Campaign {campaign}, '
              'Episode {dispe}: {title}</a></li>\n')


def makedb():
    con = sqlite3.connect("cr.db")
    con.execute("""create table if not exists episode (id integer primary key,
        campaign text, episode text, title text, link text, ytid text)""")
    con.execute("""create table if not exists speaker (id integer primary key,
        name text)""")
    con.execute("""create table if not exists line (id integer primary key,
        episode_id integer,
        time_h integer, time_m integer, time_s integer,
        text text, html text,
        CONSTRAINT fk_episode
            FOREIGN KEY (episode_id)
            REFERENCES episode (id)
            ON DELETE CASCADE
        )""")
    con.execute("""create table if not exists speaker2line (speaker_id integer,
        line_id integer,
        CONSTRAINT fk_speaker
            FOREIGN KEY (speaker_id)
            REFERENCES speaker (id)
            ON DELETE CASCADE
        CONSTRAINT fk_line
            FOREIGN KEY (line_id)
            REFERENCES line (id)
            ON DELETE CASCADE
        )""")
    con.execute("""CREATE VIRTUAL TABLE if not exists "line_fts" USING FTS4 (
        line_id, indexed_text,
        CONSTRAINT fk_line
            FOREIGN KEY (line_id)
            REFERENCES line (id)
            ON DELETE CASCADE
        )""")
    con.execute("""create index if not exists idx_sid
        on speaker2line (speaker_id)""")
    con.execute("create index if not exists idx_lid on speaker2line (line_id)")
    return con


def main():
    files = os.listdir("metadata/json")
    master = []
    existing = []
    if os.path.exists("cr.db"):
        con = sqlite3.connect("cr.db")
        crs = con.cursor()
        crs.execute("select ytid from episode")
        existing = [x[0] for x in crs.fetchall()]
        con.close()

    con = makedb()

    processed = 0
    for f in files:
        root = f.split(".")[0]
        with open(os.path.join("metadata/json", f), encoding="utf-8") as fp:
            j = json.load(fp)
        ft = j["fulltitle"]
        c1 = re.match(r"^(?P<title>.*) [-|] Critical Role RPG( Show)?:?( LIVE)? Episode ((?P<ep>[0-9]+)(, pt. [0-9]+)?)$", ft)
        c2 = re.match(r"^(?P<title>.*) \| Critical Role \| Campaign 2, Episode (?P<ep>[0-9]+)(.*)?$", ft)
        data = {
            "episode": None, "campaign": None, "ytid": root,
            "title": None, "url": j["webpage_url"]}
        if c1:
            data["episode"] = c1.groupdict()["ep"]
            data["title"] = c1.groupdict()["title"]
            data["campaign"] = "1"
        elif c2:
            data["episode"] = c2.groupdict()["ep"]
            data["title"] = c2.groupdict()["title"]
            data["campaign"] = "2"
        elif root in HARDCODED:
            data = HARDCODED[root]
            data["ytid"] = root
        else:
            print("Skip unknown episode", root, ft)
            continue

        if root in existing:
            #print(("Skipping already got "
            #       "{campaign}/{episode} {title} ({ytid})").format(**data))
            continue
        processed += 1

        print("Processing {campaign}/{episode} {title}".format(**data))
        vtt = os.path.join("metadata/vtt", root + ".en.vtt")
        if not os.path.exists(vtt):
            print("Skipping nonexistent transcript of", root)
            continue
        data["transcript"] = parse(vtt)
        htmlffn = "cr{campaign}-{episode}.html".format(**data)
        htmlfn = os.path.join("html", htmlffn)
        with open(htmlfn, encoding="utf-8", mode="w") as fp:
            fp.write(HEADER.format(**data))

            # quick pass to work out how many times we change character
            lastchar = None
            character_switches = 0
            for line in data["transcript"]:
                thischar = ", ".join(line["character"])
                if thischar == lastchar:
                    pass
                else:
                    lastchar = thischar
                    character_switches += 1
            if character_switches < 20:
                fp.write(UNPROCESSED_WARNING)

            lastchar = None
            for line in data["transcript"]:
                thischar = ", ".join(line["character"])
                if thischar == lastchar:
                    pass
                else:
                    lastchar = thischar
                    d = {
                        "lid": "l{}h{}m{}s".format(
                            line["start"][0], line["start"][1], line["start"][2]),
                        "character": thischar
                    }
                    fp.write(LINE_DT.format(**d))
                d = {
                    "text_nl": line["text"].replace("\n", "<br>\n"),
                    "yt": "https://youtube.com/watch?v={}&t={}h{}m{}s".format(
                        root, line["start"][0], line["start"][1], line["start"][2]),
                }
                fp.write(LINE_DD.format(**d))
            fp.write(FOOTER.format(**data))
        try:
            e = int(data["episode"])
            dispe = e
        except:
            e = 99999
            dispe = "(special)"
        mstr = {
            "link": htmlffn,
            "title": data["title"],
            "campaign": data["campaign"],
            "episode": data["episode"],
            "e": e,
            "dispe": dispe,
            "yt": "https://youtube.com/watch?v={}".format(root),
            "ytid": root
        }
        master.append(mstr)
        crs = con.cursor()
        crs.execute("""insert into episode (campaign, episode, title, link, ytid)
            values (:campaign, :episode, :title, :yt, :ytid)""", mstr)
        inserted_episode_id = crs.lastrowid
        for line in data["transcript"]:
            crs.execute("""insert into line
                (episode_id, time_h, time_m, time_s, text, html)
                values (?, ?, ?, ?, ?, ?)""", (
                    inserted_episode_id, line["start"][0],
                    line["start"][1], line["start"][2], line["text_text"],
                    line["text"].replace("\n", "<br>\n")
            ))
            line_id = crs.lastrowid
            for cname in line["character"]:
                crs.execute("select id from speaker where name = ?", (cname,))
                result = crs.fetchone()
                if not result:
                    crs.execute("insert into speaker (name) values (?)", (cname,))
                    speaker_id = crs.lastrowid
                else:
                    speaker_id = result[0]
                crs.execute("""insert into speaker2line (speaker_id, line_id)
                    values (?, ?)""", (speaker_id, line_id))
    if processed > 0:
        print("Processed {} episodes".format(processed))
        con.execute("""delete from line_fts""")
        con.execute("""insert into line_fts (line_id, indexed_text)
            select id, text from line""")
        con.commit()
        with open(os.path.join("html", "index.html"), encoding="utf-8", mode="w") as fp:
            fp.write(INDEX_HEADER)
            crs = con.cursor()
            crs.execute("select campaign, episode, title from episode")
            master = []
            for row in crs.fetchall():
                try:
                    e = int(row[1])
                    dispe = e
                except:
                    e = 99999
                    dispe = "(special)"
                mstr = {
                    "title": row[2],
                    "campaign": row[0],
                    "episode": row[1],
                    "dispe": dispe,
                    "e": e
                }
                master.append(mstr)

            for line in sorted(master, key=lambda d: (d["campaign"], d["e"], d["title"])):
                fp.write(INDEX_LINE.format(**line))
            fp.write(FOOTER)


if __name__ == "__main__":
    main()
