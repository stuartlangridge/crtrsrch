#!/usr/bin/env python3

import subprocess
import json
import os
import logging
import re
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


def main():
    fetched = 0
    # fetch JSON files describing the playlists
    for pl in PLAYLISTS:
        out = subprocess.check_output(
            ["youtube-dl", "--dump-single-json", "--flat-playlist", pl])
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
                    for line in fp.readlines():
                        if re.match(r"^[A-Z]+:", line):
                            tagged_lines += 1
                    if tagged_lines < 25:
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
                    "youtube-dl", "--skip-download", "--write-info-json",
                    "--sub-format", "vtt", "--write-sub", "--sub-lang", "en",
                    "--restrict-filenames", "--id", "-i",
                    "https://www.youtube.com/watch?v={}".format(key)])
                vtt = "{}.en.vtt".format(key)
                infojson = "{}.info.json".format(key)
                if (os.path.exists(vtt) and os.path.exists(infojson)):
                    os.rename(vtt, os.path.join("metadata", "vtt", vtt))
                    os.rename(infojson,
                              os.path.join("metadata", "json", infojson))
                    fetched += 1
                else:
                    print("   error: didn't download the files")
                    print(out2)
            except subprocess.CalledProcessError as e:
                if "This video is private" in e.output:
                    print("   skipping private video")
                else:
                    raise
            if is_live:
                # check again to see if what we got is better
                with open(vtt_file) as fp:
                    tagged_lines = 0
                    for line in fp.readlines():
                        if re.match(r"^[A-Z]+:", line):
                            tagged_lines += 1
                    if tagged_lines < 25:
                        print("Live captioned", key, "is still live captioned")
                    else:
                        print("Live captioned", key, "is now formatted OK")
    print("Fetched {} video{}".format(fetched, "" if fetched == 1 else "s"))


if __name__ == "__main__":
    main()
