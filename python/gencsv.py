import csv
import os
import pprint
import pyjson5
from classes import Rule

PFMFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[PFM] Raffadax Production/ProducerRules.json"
I18NFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/i18n/default.json"
MCSVOUT = "machines.csv"
GIFTSDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/NPCGiftTastes"
GCSVOUT = "gifts.csv"
VANILLAOBJECTS = pyjson5.load(open("vanillaObjects.json"))
VANILLABC = pyjson5.load(open("vanillaBigCraftables.json"))

idToObj = {}
for k, v in VANILLAOBJECTS.items():
    idToObj[v] = k

idToBC = {}
for k, v in VANILLABC.items():
    idToBC[v] = k

CATINDICES = {"-2": "Gem",
              "-4": "Fish",
              "-6": "Milk",
              "-7": "Cooking",
              "-12": "Mineral",
              "-15": "Metal Resource",
              "-16": "Building Resources",
              "-18": "Sell at Pierre or Marnie",
              "-20": "Trash",
              "-23": "Sell at Willy",
              "-25": "Cooking",
              "-26": "Artisan Goods",
              "-28": "Monster Loot",
              "-74": "Seeds",
              "-75": "Vegetable",
              "-79": "Fruit",
              "-80": "Flower",
              "-81": "Forage"}

i18n = pyjson5.load(open(I18NFILE, encoding="utf-8"))


def translateName(instr: str, mode="object"):
    if isinstance(instr, int):
        if instr < 0:
            return "Any {} item".format(CATINDICES[str(instr)])
        elif mode == "object":
            return idToObj[str(instr)]
        else:
            return idToBC[str(instr)]
    elif instr.startswith("Raffadax.RCP"):
        outStr = instr.rsplit("_", 1)[1]
        try:
            outStr = "{}.DisplayName".format(outStr)
            outStr = i18n[outStr]
        except KeyError:
            outStr = instr.rsplit("_", 1)[1]
            outStr = "{}.Displayname".format(outStr)
            outStr = i18n[outStr]
        return outStr
    elif instr.startswith("(BC)"):
        outStr = instr[4:]
        if outStr in idToBC:
            return idToBC[outStr]
        else:
            outStr = outStr.rsplit("_", 1)[1]
            outStr = i18n["{}.DisplayName".format(outStr)]
            return outStr
    elif instr.endswith("_item"):
        newStr = "Any {}".format(instr.replace("_", " "))
        return newStr
    elif instr in CATINDICES:
        return "Any {} item".format(CATINDICES[instr])
    else:
        return instr


def genMachines():
    rules = pyjson5.load(open(PFMFILE, encoding="utf-8"))
    with open(MCSVOUT, "w", newline='') as f:
        fieldNames = ["Output", "Machine", "Time", "Makes", "Chance", "Input", "Fuels"]
        writer = csv.DictWriter(f, fieldnames=fieldNames)
        writer.writeheader()
        for rule in rules:
            thisRule = Rule(**rule)
            MachineName = translateName(thisRule.ProducerQualifiedItemId, 'machine')
            Output = translateName(thisRule.OutputIdentifier)
            Input = "{} {}".format(thisRule.InputStack, translateName(thisRule.InputIdentifier)) if thisRule.InputIdentifier else "None"
            Fuel = []
            if thisRule.FuelIdentifier:
                Fuel.append("{} {}".format(thisRule.FuelStack, translateName(thisRule.FuelIdentifier)))
            if thisRule.AdditionalFuel:
                for k, v in thisRule.AdditionalFuel.items():
                    Fuel.append("{} {}".format(v, translateName(k)))
            outDict = {"Output": Output,
                       "Machine": MachineName,
                       "Time": thisRule.MinutesUntilReady,
                       "Makes": thisRule.OutputStack,
                       "Chance": 1,
                       "Input": Input,
                       "Fuels": "/".join(Fuel) if Fuel else ""}
            writer.writerow(outDict)
            if thisRule.AdditionalOutputs:
                for ao in thisRule.AdditionalOutputs:
                    outDict = {"Output": translateName(ao["OutputIdentifier"]),
                               "Machine": MachineName,
                               "Time": thisRule.MinutesUntilReady,
                               "Makes": 1,
                               "Chance": ao["OutputProbability"],
                               "Input": Input,
                               "Fuels": "/".join(Fuel) if Fuel else ""}
                    writer.writerow(outDict)


def genGifts():
    jsonFiles = []
    giftData = {}
    for entry in objectscan(GIFTSDIR):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for f in jsonFiles:
        data = pyjson5.load(open(f, encoding="utf-8"))
        for change in data["Changes"]:
            for op in change["TextOperations"]:
                if op["Target"][2] == 1:
                    npcname = op["Target"][1].strip("{}")
                    itemList = op["Value"].split(" ")
                    cleanItemList = [x.replace("{{ModId}}_", "") for x in itemList]
                    translatedItemList = [i18n["{}.Displayname".format(x) if "{}.Displayname".format(x) in i18n else "{}.DisplayName".format(x)] for x in cleanItemList]
                    for item in translatedItemList:
                        if item not in giftData:
                            giftData[item] = [npcname]
                        else:
                            giftData[item].append(npcname)
    fieldNames = ["Item", "NPCs"]
    with open(GCSVOUT, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldNames)
        writer.writeheader()
        for k, v in giftData.items():
            writer.writerow({"Item": k, "NPCs": ", ".join(v)})


def objectscan(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from objectscan(entry.path)
        elif entry.name.endswith((".json")):
            yield entry


if __name__ == "__main__":
    # genMachines()
    genGifts()
