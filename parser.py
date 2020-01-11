#!/usr/bin/env python3
import re
import os
import json
import html
import bleach
import sqlite3
import sys


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
        elif " & " in s:  # split on &
            ret = []
            for part in s.split(" & "):
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
            process(accum, character)
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
 '0rrj1v7lsxM': {'campaign': '1',
                 'episode': '102.01',
                 'title': 'Live From San Diego Comic-Con 2017'},
 '4FI8qB-yh-w': {'campaign': '1',
                 'episode': '54.01',
                 'title': 'Critical Role RPG Show Q&A and Battle Royale!'},
 '98ZZ_Tw4sSI': {'campaign': '1',
                 'episode': '93.01',
                 'title': 'Pants Optional Critmas'},
 '9jbGshiuFs4': {'campaign': '1',
                 'episode': '115.06',
                 'title': "Marisha's Honey Heist"},
 'DTOGH6M6INE': {'campaign': '1',
                 'episode': '115.01',
                 'title': 'Thursday By Night One-Shot'},
 'LHita2t54xY': {'campaign': '1',
                 'episode': '94.01',
                 'title': "Liam's Quest: Full Circle"},
 'LfeAYN8f1AU': {'campaign': '1',
                 'episode': '115.07',
                 'title': "Sam's One-Shot"},
 'LgHm3Ct0Zh0': {'campaign': '1',
                 'episode': '65.01',
                 'title': 'The Return of Liam!'},
 'Mk21j54rX-M': {'campaign': '1',
                 'episode': '112.01',
                 'title': 'Shadow of War One-Shot Part 2'},
 'OJ81ydo91cw': {'campaign': '1',
                 'episode': '74.01',
                 'title': "Critical Role's Critmas!"},
 'c9lC5_qjkFE': {'campaign': '1',
                 'episode': '111.01',
                 'title': 'Shadow of War One-Shot Part 1'},
 'eXPu1wk-Ev4': {'campaign': '1',
                 'episode': '115.02',
                 'title': 'Thursday By Night One-Shot Part 2'},
 'kLnvrocetq8': {'campaign': '1',
                 'episode': '115.04',
                 'title': "Grog's One-Shot"},
 'q3BGg0d8DvU': {'campaign': '1',
                 'episode': '115.08',
                 'title': 'Epic Level Battle Royale One-Shot'},
 'qA4-q4gk_yY': {'campaign': '1',
                 'episode': '115.05',
                 'title': 'Hearthstone One-Shot'},
 'rnq3VBQu_kI': {'campaign': '1',
                 'episode': '115.03',
                 'title': 'Bar Room Blitz One-Shot'},
 'tasz1xUVLhg': {'campaign': '1',
                 'episode': '98.02',
                 'title': 'Battle Royale One-Shot'},
 'u8MRyyFDX3c': {'campaign': '1',
                 'episode': '43.01',
                 'title': 'TO THE POOP! - The Goblins (Pathfinder)'},
 'uw1crQ1d9AU': {'campaign': '1',
                 'episode': '45.01',
                 'title': 'Cindergrove Revisited'}
}

IGNORED_NON_EPISODES = [
    "7J4fg79Utsk",  # Why I Love Critical Role (Fan Submissions) | Talks Machina
    "oSv-RSfkzGA",  # CR: The Perfume from Critical Role
    "mHfXAXM4O3E",  # Check Out CRITICAL ROLE's New Intro!
    "_NmZ2b_Q3So",  # Talks Machina: Discussing C2E84 - Titles and Tattoos

]

INDEX_HEADER = """<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-331575-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'UA-331575-1');
</script>
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
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-331575-1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', 'UA-331575-1');
</script>

<title>Critical Role Campaign {campaign} Episode {episode} "{title}" linkable transcript</title>

<link rel="stylesheet" href="../style.css">
</head>
<body>
<main>
    <h1>Critical Role linkable transcripts</h1>
    <h2>Campaign {campaign} Episode {episode}</h2>
    <h2>{title}</h2>

    [[prevnext]]

    <nav>
        <ul>
            <li><a href="index.html">list of episodes</a></li>
            <li><a href="../">search transcripts</a></li>
        </ul>
    </nav>

    

    <div id="lines">
"""

UNPROCESSED_WARNING = """<p class="unprocessed-warning">It looks like this
transcript is the
<a href="https://critrole.com/live-closed-captions-on-twitch/">live
closed captions</a> from Twitch, and hasn't yet been processed by the
transcript team. This means that searching won’t work very well against it
yet, and nor will searching by character. It will update in time; be patient,
<a href="https://crtranscript.tumblr.com/post/186968699597/how-to-submit-corrections-maybe-put-the#notes">they
work very hard</a>. You can still view <a href="https://youtube.com/watch?v={ytid}">the
episode itself on YouTube</a>.</p>"""

FOOTER = """
    </div><!-- lines -->

    [[prevnext]]

    <footer>
        <p>This is an <a href="https://kryogenix.org/">@sil</a> thing.</p>
        <p>And a <a href="https://critrole.com/">Critical Role</a>
        thing, of course.</p>
        <p>Mostly a Critical Role thing. And a CRTranscript thing.
        Stuart tied all their hard work together.</p>
    </footer>
</body>
</html>"""

LINE_DT = """<dt><a href="#{lid}">#</a> <strong>{character}</strong></dt>\n"""
LINE_DD = """<dd id="{lid}">{text_nl} <a href="{yt}">&rarr;</a></dd>\n"""
INDEX_LINE = ('<li><a href="cr{campaign}-{episode}.html">Campaign {campaign}, '
              'Episode {dispe}: {title}</a> {unprocessed}</li>\n')


def makedb():
    con = sqlite3.connect("cr.db")
    con.execute("""create table if not exists episode (id integer primary key,
        campaign text, episode text, title text, link text,
        ytid text, sortkey text, processed boolean)""")
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
    unprocessed_episodes = []
    for f in files:
        root = f.split(".")[0]
        with open(os.path.join("metadata/json", f), encoding="utf-8") as fp:
            j = json.load(fp)
        ft = j["fulltitle"]
        c1 = re.match(r"^(?P<title>.*) [-|] Critical Role RPG( Show)?:?( LIVE)? Episode ((?P<ep>[0-9]+)(, pt. [0-9]+)?)$", ft)
        c2 = re.match(r"^(?P<title>.*) \| Critical Role *\| Campaign 2,? (Episode|Epsiode) (?P<ep>[0-9]+)(.*)?$", ft)
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
        elif root in IGNORED_NON_EPISODES:
            continue
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

            # quick pass to work out how many times we change character,
            # and whether one character has a lot of lines
            lastchar = None
            character_switches = 0
            longest_speech_lines = 0
            current_speech_lines = 0
            for line in data["transcript"]:
                thischar = ", ".join(line["character"])
                if thischar == lastchar:
                    current_speech_lines += 1
                    if current_speech_lines > longest_speech_lines:
                        longest_speech_lines = current_speech_lines
                else:
                    lastchar = thischar
                    character_switches += 1
                    current_speech_lines = 0
            if character_switches < 20 or longest_speech_lines > 500:
                fp.write(UNPROCESSED_WARNING.format(**data))
                unprocessed_episodes.append((data["campaign"], data["episode"]))

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
                    "lid": "l{}h{}m{}s".format(
                            line["start"][0], line["start"][1], line["start"][2])
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
            "ytid": root,
            "sortkey": "c{:03d}e{:07.2f}".format(
                int(data["campaign"]),
                float(data["episode"])
            ),
            "processed": (data["campaign"], data["episode"]) not in unprocessed_episodes
        }
        master.append(mstr)
        crs = con.cursor()
        crs.execute("""insert into episode (campaign, episode, title, link, ytid, sortkey, processed)
            values (:campaign, :episode, :title, :yt, :ytid, :sortkey, :processed)""", mstr)
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
    if processed > 0 or "--rebuild-index" in sys.argv:
        print("Processed {} episodes".format(processed))
        con.execute("""delete from line_fts""")
        con.execute("""insert into line_fts (line_id, indexed_text)
            select id, text from line""")
        con.commit()
        with open(os.path.join("html", "index.html"), encoding="utf-8", mode="w") as fp:
            fp.write(INDEX_HEADER)
            crs = con.cursor()
            crs.execute("select campaign, episode, title, processed from episode")
            master = []
            written_to_index = set()
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
                    "e": e,
                    "unprocessed": "" if row[3] else '<span class="unprocessed">not yet ready</span>'
                }
                master.append(mstr)

            for line in sorted(master, key=lambda d: (d["campaign"], d["e"], d["title"])):
                ekey = (line["campaign"], line["e"])
                if ekey not in written_to_index:
                    fp.write(INDEX_LINE.format(**line))
                    written_to_index.add(ekey)
            fp.write(FOOTER.replace("[[prevnext]]", ""))

    # update prevnexts
    crs = con.cursor()
    crs.execute("select campaign, episode, title from episode order by sortkey asc")
    episodes = crs.fetchall()
    for idx in range(len(episodes)):
        campaign, episode, title = episodes[idx]
        prevc, preve, prevt = None, None, None
        if idx > 0:
            prevc, preve, prevt = episodes[idx - 1]
        nextc, nexte, nextt = None, None, None
        if idx < len(episodes) - 1:
            nextc, nexte, nextt = episodes[idx + 1]
        htmlfile = "html/cr{campaign}-{episode}.html".format(
            campaign=campaign, episode=episode)
        if nextc:
            nexth = ('<a class="next" href="cr{campaign}-{episode}.html">'
                     '{campaign}x{episode} {title} &rarr;</a>').format(
                campaign=nextc, episode=nexte, title=html.escape(nextt))
        else:
            nexth = ""
        if prevc:
            prevh = ('<a class="prev" href="cr{campaign}-{episode}.html">'
                     '&larr; {campaign}x{episode} {title}</a>').format(
                campaign=prevc, episode=preve, title=html.escape(prevt))
        else:
            prevh = ""
        prevnext = '<div class="prevnext">{}{}</div>'.format(prevh, nexth)
        fp = open(htmlfile, encoding="utf-8")
        data = fp.read()
        fp.close()
        # add prevnext to newly written things
        data = data.replace("[[prevnext]]", prevnext)
        # and fix up previous things
        data = re.sub(r'<div class="prevnext">.*?</div>', prevnext, data)
        fp = open(htmlfile, encoding="utf-8", mode="w")
        fp.write(data)
        fp.close()


if __name__ == "__main__":
    main()
