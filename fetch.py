#!/usr/bin/env python3

import subprocess
import json
import os
import logging
import re
import sys
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

PLAYLISTS = [
    "PL1tiwbzkOjQxD0jjAE7PsWoaCrs0EkBH2",  # campaign 1
    "PL7atuZxmT954bCkC062rKwXTvJtcqFB8i"  # campaign 2
]

SKIP = [
    "GYZqdvXb1SU",  # private video
    "oSv-RSfkzGA",  # perfume ad?
    "mHfXAXM4O3E",  # intro
    "7J4fg79Utsk",  # fan submissions
    "5UwEc10_DcI",  # slayer's cake ad
]

FAKE_VTT = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:03.533
(no captions available for this episode yet)
"""


def fixAutoCaptionedVTT(vtt):
    """If you download automatic captions, YouTube puts a bunch of weird crap
       in them, so they look like thie below. Fix it.

WEBVTT
Kind: captions
Language: en

00:00:00.030 --> 00:00:01.490 align:start position:0%

hello<00:00:00.450><c> everyone</c><00:00:00.780><c> and</c><00:00:00.930><c> we
lcome</c><00:00:00.989><c> to</c><00:00:01.380><c> tonight's</c>

00:00:01.490 --> 00:00:01.500 align:start position:0%
hello everyone and welcome to tonight's


00:00:01.500 --> 00:00:03.770 align:start position:0%
hello everyone and welcome to tonight's
episode<00:00:01.790><c> critical</c><00:00:02.790><c> role</c><00:00:02.939><c> or</c><00:00:03.149><c> a</c><00:00:03.179><c> mysterious</c>

00:00:03.770 --> 00:00:03.780 align:start position:0%
episode critical role or a mysterious
    """
    fp = open(vtt, encoding="utf-8")
    data = fp.read()
    fp.close()
    if "<c>" in data and "</c>" in data:
        out = []
        accum = []
        in_header = True
        last_time = ""
        counter = 1
        for line in data.split("\n"):
            if in_header and not line.strip():
                in_header = False
                out.append(line)
                continue
            if in_header:
                out.append(line)
                continue
            m = re.match(
                    r"([0-9]{2}[:.]){3}[0-9]{3} --> ([0-9]{2}[:.]){3}[0-9]{3}",
                    line)
            if m:
                last_time = m.group()
            elif not line.strip():
                if accum:
                    joined = " ".join(accum)
                    if "<c>" in joined:
                        accum = []
                    else:
                        out.append(str(counter))
                        out.append(last_time)
                        out.append(joined)
                        out.append("")
                        counter += 1
                        accum = []
                else:
                    # nothing accumulated; shouldn't happen
                    pass
                continue
            else:
                accum.append(line)
        print("Fixing", vtt, "from YouTube horrid auto captions to proper VTT")
        fp = open(vtt, mode="w", encoding="utf-8")
        fp.write("\n".join(out))
        fp.close()


def main():
    need_deleting = []
    added = []
    fetched = 0
    # fetch JSON files describing the playlists
    for pl in PLAYLISTS:
        out = subprocess.check_output(
            ["/home/aquarius/bin/youtube-dl", "--dump-single-json", "--flat-playlist", pl])
        lst = json.loads(out)
        for detail in lst.get("entries", {}):
            key = detail["url"]
            json_file = os.path.join("metadata", "json",
                                     "{}.info.json".format(key))
            vtt_file = os.path.join("metadata", "vtt",
                                    "{}.en.vtt".format(key))
            is_live = False
            if key in SKIP:
                logging.debug("Hardcoded skip %s", key)
                continue
            elif os.path.exists(vtt_file) and os.path.exists(json_file):
                # check to see if we already have it but it's
                # the unformatted live captions
                is_ok = True
                with open(json_file) as fp:
                    jdetails = json.load(fp)
                with open(vtt_file) as fp:
                    tagged_lines = 0
                    largest_untagged_lines = 0
                    current_untagged_lines = 0
                    for line in fp.readlines():
                        if re.match(r"^[A-Z]+:", line):
                            tagged_lines += 1
                            current_untagged_lines = 0
                        else:
                            current_untagged_lines += 1
                            if current_untagged_lines > largest_untagged_lines:
                                largest_untagged_lines = current_untagged_lines
                    if largest_untagged_lines > 1000 or tagged_lines < 25:
                        print("Re-fetch live captioned '{}' ({})".format(
                              jdetails["fulltitle"], key))
                        is_ok = False
                        is_live = True

                if is_ok:
                    logging.debug("Skip %s", key)
                    continue

            logging.info("Get %s", key)
            try:
                out2 = subprocess.check_output([
                    "/home/aquarius/bin/youtube-dl", "--skip-download", "--write-info-json",
                    "--sub-format", "vtt", "--write-auto-sub",
                    "--write-sub", "--sub-lang", "en",
                    "--restrict-filenames", "--id", "-i",
                    "https://www.youtube.com/watch?v={}".format(key)],
                    stderr=subprocess.STDOUT)
                vtt = "{}.en.vtt".format(key)
                infojson = "{}.info.json".format(key)
                if (os.path.exists(vtt) and os.path.exists(infojson)):
                    fixAutoCaptionedVTT(vtt)
                    os.rename(vtt, os.path.join("metadata", "vtt", vtt))
                    os.rename(infojson,
                              os.path.join("metadata", "json", infojson))
                    fetched += 1
                    added.append(key)
                else:
                    output = out2.decode("utf-8")
                    print("Trying to fetch {} failed to download, with error:".format(key))
                    print(output)
                    if os.path.exists(infojson):
                        # write a fake vtt file
                        print("The VTT file was not fetched, so we write a temporary fake one")
                        os.rename(infojson,
                                  os.path.join("metadata", "json", infojson))
                        fp = open(os.path.join("metadata", "vtt", vtt),
                                  mode="w", encoding="utf-8")
                        fp.write(FAKE_VTT)
                        fetched += 1

            except subprocess.CalledProcessError as e:
                if "This video is private" in e.output.decode("utf-8"):
                    print("   skipping private video")
                else:
                    raise
            if is_live:
                # check again to see if what we got is better
                with open(vtt_file) as fp:
                    tagged_lines = 0
                    tagged_lines = 0
                    largest_untagged_lines = 0
                    current_untagged_lines = 0
                    for line in fp.readlines():
                        if re.match(r"^[A-Z]+:", line):
                            tagged_lines += 1
                            current_untagged_lines = 0
                        else:
                            current_untagged_lines += 1
                            if current_untagged_lines > largest_untagged_lines:
                                largest_untagged_lines = current_untagged_lines
                    if largest_untagged_lines > 1000 or tagged_lines < 25:
                        print("Live captioned", key,
                              "is still live captioned rather",
                              "than correctly formatted")
                    else:
                        print("Live captioned", key, "is now formatted OK")
                        print("It needs to be removed from the database and",
                              "then the parser run again to update it")
                        print("Do so with:")
                        print("""    sqlite3 cr.db "delete from episode""",
                              """where ytid = '{}';" """.format(key))
                        need_deleting.append(key)
    print("Fetched {} video{}".format(fetched, "" if fetched == 1 else "s"))
    return {"added": added, "need_deleting": need_deleting}


if __name__ == "__main__":
    resp = main()
    if "--json-list" in sys.argv:
        print("BEGIN MACHINE OUTPUT")
        print("\n".join(resp["added"]))
        print("\n".join(resp["need_deleting"]))


