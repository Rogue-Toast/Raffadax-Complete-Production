import copy
import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode

vanillaObjects = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
INFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[FTM] Forage/content.json"
OUTFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[FTM] Forage/content.json"
NEWIDS = pyjson5.load(open("newids.json"))
NAMERE = r"[^a-zA-Z0-9_\.]"
FORAGE = []


def convertftm():
    src = pyjson5.load(open(INFILE, encoding="utf-8"))
    outdata = copy.deepcopy(src)
    nodenames = ["SpringItemIndex", "SummerItemIndex", "FallItemIndex", "WinterItemIndex"]
    for area in outdata["Forage_Spawn_Settings"]["Areas"]:
        for nn in nodenames:
            if isinstance(area[nn], list):
                for anode in area[nn]:
                    if "contents" in anode and anode["contents"]:
                        newcontents = []
                        for item in anode["contents"]:
                            newcontents.append(translateName(item))
                        anode["contents"] = newcontents
                    else:
                        anode["name"] = translateName(anode["name"])
                        if anode["name"] not in FORAGE and anode["name"].startswith("Raffadax"):
                            FORAGE.append(anode["name"])
    with open("forageitems.json", 'w', encoding='utf-8') as f:
        json.dump(FORAGE, f, indent=4, ensure_ascii=False)
    return outdata


def translateName(instr: str):
    if instr in vanillaObjects:
        return vanillaObjects[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    elif instr in NEWIDS:
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", NEWIDS[instr]))
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    ftmData = convertftm()
    # pprint.pprint(ftmData["Forage_Spawn_Settings"]["Areas"][0])

    with open(OUTFILE, 'w', encoding='utf-8') as f:
        json.dump(ftmData, f, indent=4, ensure_ascii=False)
