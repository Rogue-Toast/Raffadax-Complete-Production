import copy
import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode

MODNAME = "Raffadax.RCP"
MYCFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[MYC] Raffadax Multi Yield/HarvestRules.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[MYC] Raffadax Multi Yield/HarvestRules.json"

if __name__ == "__main__":
    NAMERE = r"[^a-zA-Z0-9_\.]"
    mycData = pyjson5.load(open(MYCFILE), encoding="utf-8")
    vanillaFile = "vanillaObjects.json"
    vanillaData = json.load(open(vanillaFile))
    outList = []
    for rule in mycData["Harvests"]:
        outRule = copy.deepcopy(rule)
        if outRule["CropName"] not in vanillaData:
            nameStr = unidecode(rule["CropName"])
            nameStr = re.sub(NAMERE, "", nameStr)
            outRule["CropName"] = "{}_{}".format(MODNAME, nameStr)
        for hr in outRule["HarvestRules"]:
            if hr["ItemName"] not in vanillaData:
                if hr["ItemName"].startswith("Jalap"):
                    print("Hi")
                    hnameStr = "JalapenoPepper"
                else:
                    hnameStr = unidecode(hr["ItemName"])
                    hnameStr = re.sub(NAMERE, "", hnameStr)
                hr["ItemName"] = "{}_{}".format(MODNAME, hnameStr)
            else:
                hr["ItemName"] = vanillaData[hr["ItemName"]]
        outList.append(outRule)
    outDict = {"Harvests": outList}
    outJson = json.dumps(outDict, indent=4)
    with open(OUTPATH, 'w') as f:
        f.write(outJson)
