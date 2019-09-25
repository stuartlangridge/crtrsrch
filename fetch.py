#!/usr/bin/env python3

import subprocess
import json
import os
import logging
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)

PLAYLISTS = [
    "PL1tiwbzkOjQxD0jjAE7PsWoaCrs0EkBH2",  # campaign 1
    "PL7atuZxmT954bCkC062rKwXTvJtcqFB8i"  # campaign 2
]

SKIP = [
    "GYZqdvXb1SU"  # private video
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
            if os.path.exists(os.path.join("metadata", "json",
                                           "{}.info.json".format(key))):
                logging.debug("Skip %s", key)
            elif key in SKIP:
                logging.debug("Hardcoded skip %s", key)
            else:
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
    print("Fetched {} videos".format(fetched))


if __name__ == "__main__":
    main()
