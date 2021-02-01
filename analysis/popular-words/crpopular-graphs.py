#!/usr/bin/env python3
import os
import json
from collections import Counter

saved = os.path.join(os.path.dirname(__file__), "crpopular.json")

try:
    with open(saved) as fp:
        data = json.load(fp)
        for sp in data["speakers"]:
            data["speakers"][sp]["words"] = Counter(data["speakers"][sp]["words"])
            data["speakers"][sp]["pairs"] = Counter(data["speakers"][sp]["pairs"])
            if "role critical" in data["speakers"][sp]["pairs"]: del data["speakers"][sp]["pairs"]["role critical"]
            if "critical critical" in data["speakers"][sp]["pairs"]: del data["speakers"][sp]["pairs"]["critical critical"]
except (FileNotFoundError, json.decoder.JSONDecodeError):
    data = {"upto": 0, "speakers": {}}

CATS = {
    "dand": [
        "bonus action", "natural 20", "natural 1", "constitution saving",
        "action surge", "hit points", "lightning damage", "radiant damage",
        "psychic damage", "short rest", "saving throw", "damage plus",
        "get advantage", "saving throws", "30 feet",
        "plus four", "five feet", "attack damage", "perception check",
        "ten feet", "60 feet", "first hit", "second attack", "second hit",
        "slashing damage", "athletics check", "plus two", "dexterity saving",
        "fire damage", "piercing damage", "bludgeoning damage", "20 feet",
        "15 feet", "stealth check", "roll damage", "investigation check",
        "insight check", "plus six", "plus five", "plus seven", "wisdom saving",
        "strength check", "persuasion check", "force damage", "nature check",
        "natural 19", "history check", "survival check"
    ],
    "rogue": ["uncanny dodge", "sneak attack"],
    "monk": ["patient defense", "stunning strike", "plus another"],
    "barbarian": ["great weapon", "weapon master", "minus five",
    "savage attacker", "frenzied rage"],
    "spell": [
        "detect magic", "guiding bolt", "mass cure", "cure wounds",
        "spiritual weapon", "greater restoration", "sacred flame",
        "healing word", "hunter mark", "pass without", "cast pass",
        "cast cure", "mage hand", "bigby hand", "cutting words",
        "ten minutes", "eldritch blast", "eldritch blasts", "lightning bolt",
        "control water", "hexblade curse", "locate object", "fire bolt"
    ],
    "exandria": ["sun tree", "cobalt soul", "earth elemental", "menagerie coast", "bright queen"],
    "groups": ["vox machina", "mighty nein"],
    "cr": ["critical role", "role critical", "talks machina",
    "critical critical"],
    "cast": ["travis willingham", "laura bailey", "taliesin jaffe",
    "marisha ray", "sam riegel"],
    "cool": ["pretty cool", "pretty good", "really cool",
    "really good", "good job", "good idea", "really bad"],
    "swearing": ["holy shit", "god damn"],
    "littlebit": ["little bit"],
    "going": ["let go", "go back", "go get", "keep going", "really quickly",
    "could go"],
    "boring": ["let see", "make sure",
    "far away", "long time", "let get", "tell us", 
    "get us", "never mind", "would love"],
    "sponsors": ["loot crate", "dwarven forge", "puzzle quest"],
    "mattisms": ["brings us", "go ahead", "anything else", "turns around"],
    "intro": ["welcome back", "tonight episode", "next week", "last time"],
    "other": [],
    "double": []
}

CATDESCS = {
    "dand": ("Stuff about the game itself; checks and saves and so on", True,
        "noun_D20_2453700.svg", "D&amp;D"),
    "rogue": ("Rogues, man", True,
        "noun_dagger_3274037.svg"),
    "monk": ("Dope monk shit", True,
        "noun_Martial_Arts_3503069.svg"),
    "barbarian": ("I would like to rage!", True,
        "noun_Muscle_1873688.svg"),
    "spell": ("Anybody can make lights. I want to bend reality to my will.", True,
        "noun_magic_598261.svg"),
    "exandria": ("Things peculiar to this wonderful world", True,
        "noun_Map_2221287.svg"),
    "groups": ("These motley bands of more-or-less heroes", True,
        "noun_people_1814869.svg"),
    "cr": ("Title drops of the show itself", True,
        "critical-role.svg", "Critical Role"),
    "cast": ("Say my name, say my name", True,
        "noun_Clapperboard_3664147.svg"),
    "cool": ("If you can think of something nice to say, say it", True,
        "noun_praise_384068.svg"),
    "littlebit": ("Everybody says ‘little bit’ <em>all the goddamn time</em>. I do not understand why", False,
        "noun_Pinch_976231.svg"),
    "swearing": ("When the HSQ is this consistently high, it is not surprising that people notice", True,
        "noun_swear_3460565.svg"),
    "going": ("Talking about going places", False, "noun_Travel_1835377.svg"),
    "boring": ("Filler things that people say to make a thought into a sentence", False, "noun_Sheep_1181356.svg"),
    "sponsors": ("This week’s show is brought to you by", True,
        "noun_Money_1704826.svg"),
    "mattisms": ("Not a complaint. I love you, buddy. ‘Toothy maw’ is so far down it’s not even on the list", True,
        "noun_folding_phone_3512378.svg"),
    "intro": ("Things about the structure of the show, summaries of what happened last time, etc", False,
        "noun_introduction_2044552.svg"),
    "other": ("Everything else!", True,
        ""),
    "double": ("So good they said it twice (unless it's 'okay okay', sorry)", True,
        "noun_copy_1955602.svg"),
}
EXCLUDE = ["ORION"]

with open("index.html", mode="w", encoding="utf-8") as fp:
    fp.write(open("top.html").read())

    # must be at the same level as .people
    for cat in CATS:
        dispcat = cat
        parts = CATDESCS[cat]
        if len(parts) == 4:
            desc, display, img, dispcat = parts
        else:
            desc, display, img = parts
        checked = "checked" if display else ""
        fp.write(f'  <input type="checkbox" id="{cat}" {checked}>\n')
        fp.write(f'  <label for="{cat}"><strong>{dispcat}</strong> <span>{desc}</span></label>\n')

    fp.write(f'  <input type="checkbox" id="all">\n')
    fp.write(f'  <label for="all"><strong>Everything</strong> <span>Show all the things, not just the top 10</span></label>\n')

    fp.write('<style>\n')
    for cat in CATS:
        parts = CATDESCS[cat]
        if len(parts) == 4:
            desc, display, img, dispcat = parts
        else:
            desc, display, img = parts
        fp.write(f'input#{cat}:checked ~ #people li.{cat} ')
        fp.write("{\n")
        fp.write("  height: 2.5em; font-size: unset; ");
        fp.write("  border-bottom: 1px solid rgba(255, 255, 255, 0.1); ");
        fp.write("  transform: none; opacity: 1; }\n")
        fp.write(f'input#{cat} + label ')
        fp.write("{ ")
        fp.write(f"background-image: url(icons/white/{img});")
        fp.write(" }\n")
        fp.write(f'#people li.{cat}::before ')
        fp.write("{ ")
        fp.write(f"background-image: url(icons/white/{img});")
        fp.write(" }\n")
    fp.write('</style>\n')

    fp.write("<div id='people' class='all'>\n")
    for sp in data["speakers"]:
        if sp in EXCLUDE: continue
        wordtotal = sum(data["speakers"][sp]["words"].values())
        if wordtotal < 50000: continue
        fp.write(f"<div>\n  <h2>{sp}</h2>\n  <ol>\n")
        ucount = 0
        for w, count in data["speakers"][sp]["pairs"].most_common(1000):
            ucount += 1
            if count < 30 and ucount > 20: continue
            cat = None
            for c, vals in CATS.items():
                if w in vals:
                    cat = c
                    break
            if cat is None and w.split()[0] == w.split()[1]: cat = "double"
            if cat is None: cat = "other"
            fp.write(f'    <li title="said {count} times" class="{cat}"><a href="https://kryogenix.org/crsearch/?q=%22{w.replace(" ", "+")}%22&{sp}=on">{w}</a></li>\n')
        fp.write("  </ol>\n</div>\n")
    fp.write("</div>\n")
    fp.write(open("bottom.html").read())
