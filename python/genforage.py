import pyjson5
import csv
import pprint

FTMFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[FTM] Forage/content.json"
I18NFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/i18n/default.json"
AREAS = ["Backwoods", "BusStop", "Farm", "FarmCave", "Town", "Forest", "Woods", "Sewer",
         "BugLand", "Beach", "Mountain", "Railroad", "Mines", "WitchSwamp",
         "Desert", "IslandNorth", "IslandNorthCave1", "IslandSouth", "IslandWest", "IslandEast", "IslandSouthEast",
         "IslandShrine", "IslandSouthEastCave", "Summit", "Mine", "Volcano"]
CSVOUT = "forage.csv"
VANILLAOBJECTS = pyjson5.load(open("vanillaObjects.json"))
vids = {}
for k, v in VANILLAOBJECTS.items():
    vids[v] = k

ftmdata = pyjson5.load(open(FTMFILE, encoding="utf-8"))
langdata = pyjson5.load(open(I18NFILE, encoding="utf-8"))

fieldnames = ["ITEM"] + AREAS
items = {}
seasonKeys = ["SpringItemIndex", "SummerItemIndex", "FallItemIndex", "WinterItemIndex"]
for area in ftmdata["Forage_Spawn_Settings"]["Areas"]:
    for seasonKey in seasonKeys:
        seasonName = seasonKey[0:-9]
        if seasonKey in area and isinstance(area[seasonKey], list):
            for item in area[seasonKey]:
                if "contents" in item:
                    for si in item["contents"]:
                        if si.startswith("Raffadax"):
                            namePrep = si.split("_", 1)[1]
                            transKey = "{}.DisplayName".format(namePrep)
                            itemName = langdata[transKey]
                        else:
                            itemName = vids[str(si)]
                        if itemName not in items:
                            items[itemName] = {seasonName: {area["MapName"]: []}}
                        elif seasonName not in items[itemName]:
                            items[itemName][seasonName] = {area['MapName']: []}
                        elif area["MapName"] not in items[itemName][seasonName]:
                            items[itemName][seasonName][area["MapName"]] = []
                        chance = "Common"
                        if area["MinimumSpawnsPerDay"] < -1:
                            chance = "Rare"
                        if "SpawnWeight" in item and int(item["SpawnWeight"]) < 5:
                            chance = "Rare"
                        weather = "All"
                        if area["ExtraConditions"]["WeatherToday"]:
                            weather = area["ExtraConditions"]["WeatherToday"]
                        mapDict = {"Chance": chance,
                                   "Weather": weather}
                        if mapDict not in items[itemName][seasonName][area["MapName"]]:
                            items[itemName][seasonName][area["MapName"]] = [mapDict]
                        else:
                            items[itemName][seasonName][area["MapName"]].append(mapDict)
                else:
                    si = item["name"]
                    if si.startswith("Raffadax"):
                        namePrep = si.split("_", 1)[1]
                        transKey = "{}.DisplayName".format(namePrep)
                        itemName = langdata[transKey]
                    else:
                        itemName = vids[str(si)]
                    if itemName not in items:
                        items[itemName] = {seasonName: {area["MapName"]: []}}
                    elif seasonName not in items[itemName]:
                        items[itemName][seasonName] = {area['MapName']: []}
                    elif area["MapName"] not in items[itemName][seasonName]:
                        items[itemName][seasonName][area["MapName"]] = []
                    chance = "Common"
                    if area["MinimumSpawnsPerDay"] < -1:
                        chance = "Rare"
                    if "SpawnWeight" in item and int(item["SpawnWeight"]) < 5:
                        chance = "Rare"
                    weather = "All"
                    if area["ExtraConditions"]["WeatherToday"]:
                        weather = area["ExtraConditions"]["WeatherToday"]
                    mapDict = {"Chance": chance,
                               "Weather": weather}
                    if mapDict not in items[itemName][seasonName][area["MapName"]]:
                        items[itemName][seasonName][area["MapName"]] = [mapDict]
                    else:
                        items[itemName][seasonName][area["MapName"]].append(mapDict)
seasons = ["Spring", "Summer", "Fall", "Winter"]
with open(CSVOUT, "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for item, seasonData in items.items():
        if all(x in seasonData for x in seasons):
            defaultStr = "All"
        else:
            defaultStr = " ".join([x[0:2] for x in seasons if x in seasonData])
        outDict = {"ITEM": item}
        for season, mapData in seasonData.items():
            for mapName, dataList in mapData.items():
                outStr = defaultStr
                if mapName.startswith("Volcano"):
                    outMap = "Volcano"
                else:
                    outMap = mapName
                if all(x["Weather"] != "All" for x in dataList):
                    outStr += " ({})".format("/".join(dataList[0]["Weather"]))
                if all(x["Chance"] == "Rare" for x in dataList):
                    outStr += " (Rare)"
                outDict[outMap] = outStr
        writer.writerow(outDict)
