#!/usr/bin/env python3

"""Sometimes the CR people delete YouTube episodes and re-upload them.
This mostly only happened in the transition from G&S to CR.
Find any old episodes we have in the DB which no longer exist, and
remove them."""

import sqlite3
import sys
import subprocess
import os


def find_or_remove(remove=False):
    con = sqlite3.connect("cr.db")
    crs = con.cursor()
    crs.execute("select id, campaign, episode, title, link, ytid from episode")
    removals = []
    for rowid, campaign, episode, title, link, ytid in crs.fetchall():
        print("Checking {}x{} {}: ".format(campaign, episode, title), end="")
        ret = subprocess.call([
            "/home/aquarius/bin/youtube-dl",
            "--skip-download", "--quiet", "--get-id", link],
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        if ret == 0:
            print("exists OK")
        else:
            print("episode has been removed")
            removals.append((rowid, ytid))
    if remove:
        if removals:
            qs = ["?"] * len(removals)
            qs = ",".join(qs)
            sql = "delete from episode where id in ({})".format(qs)
            crs2 = con.cursor()
            removal_rowids = [x[0] for x in removals]
            removal_ytids = [x[1] for x in removals]
            crs2.execute(sql, removal_rowids)
            for y in removal_ytids:
                md = os.path.join(
                    os.path.split(__file__)[0], "metadata", "vtt",
                    "{}.en.vtt".format(y))
                js = os.path.join(
                    os.path.split(__file__)[0], "metadata", "json",
                    "{}.info.json".format(y))
                os.unlink(md)
                os.unlink(js)
            con.commit()
            print("{} outdated episode entries removed".format(len(removals)))
        else:
            print("All episodes exist: nothing to remove")
    else:
        if removals:
            print("Not removing any episodes (would have removed {})".format(
                len(removals)))
            print("Pass --delete to actually remove")
        else:
            print("Not removing any episodes (and they all exist anyway)")


if __name__ == "__main__":
    find_or_remove("--delete" in sys.argv)
