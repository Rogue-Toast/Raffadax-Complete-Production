import json
import os
import pprint

VANILLAPATH = "H:/Stardew Decompiled/Content (unpacked)/Data/Objects.json"
VANILLABCPATH = "H:/Stardew Decompiled/Content (unpacked)/Data/BigCraftables.json"

if __name__ == "__main__":
    rawvanillaobjects = json.load(open(VANILLAPATH, encoding="utf-8"))
    outDict = {}
    for id, data in rawvanillaobjects.items():
        outDict[data["Name"]] = id
    outJson = json.dumps(outDict)
    filename = "vanillaObjects.json"
    with open(filename, 'w') as f:
        f.write(outJson)

    rawvanillabc = json.load(open(VANILLABCPATH, encoding="utf-8"))
    outDict = {}
    for id, data in rawvanillabc.items():
        outDict[data['Name']] = id
    outJson = json.dumps(outDict)
    filename = "vanillaBigCraftables.json"
    with open(filename, 'w') as f:
        f.write(outJson)
