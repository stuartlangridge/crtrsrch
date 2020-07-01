#!/usr/bin/env python3

from html.parser import HTMLParser
import re
import glob
import os
import sys
import json

ts_re = re.compile(r"^l([0-9]+)h([0-9]+)m([0-9]+)s$")

class CRParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_header = False
        self.in_lines = False
        self.metadata = {}
        self.lines = []
        self.process = None

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_header = True
        elif tag == "h3" and self.in_header:
            if "campaign" in self.metadata:
                self.process = "title"
            else:
                self.process = "ce"
        elif tag == "div" and ("id", "lines") in attrs:
            self.in_header = False
            self.in_lines = True
        elif tag == "strong" and self.in_lines:
            self.process = "name"
        elif tag == "dd" and self.in_lines:
            self.process = "text"
            self.lines[-1]["ts"] = self.make_timestamp(dict(attrs).get("id"))

    def make_timestamp(self, v):
        matches = ts_re.match(v).groups()
        return {"h": int(matches[0]), "m": (matches[1]), "s": int(matches[2])}

    def handle_data(self, data):
        if self.process:
            if self.process == "ce":
                _, self.metadata["campaign"], _, self.metadata["episode"] = data.split()
            elif self.process == "title":
                self.metadata["title"] = data
            elif self.process == "name":
                self.lines.append({"name": data})
            elif self.process == "text":
                self.lines[-1]["text"] = data
            else:
                print("WARNING: unknown process type")
        self.process = None

def main():
    inp = glob.glob("html/*.html")
    if not inp:
        print("This conversion script expects to find all the HTML transcripts in a folder called html.")
        print("Since it can't find them, it's aborting.")
        sys.exit(1)
    try:
        os.mkdir("json_transcripts")
    except FileExistsError:
        pass

    successes = 0
    for inpf in inp:
        with open(inpf, encoding="utf-8") as fp:
            print("Processing", inpf)
            p = CRParser()
            p.feed(fp.read())
            if "campaign" in p.metadata:
                p.metadata["html_file"] = inpf
                outf = "cr{campaign}-{episode}.json".format(**p.metadata)
                outfn = os.path.join("json_transcripts", outf)
                with open(outfn, mode="w", encoding="utf-8") as outfp:
                    json.dump({"metadata": p.metadata, "lines": p.lines}, outfp, indent=2)
                    successes += 1
    print("Successfully written {} files to json_transcripts.".format(successes))

if __name__ == "__main__":
    main()
