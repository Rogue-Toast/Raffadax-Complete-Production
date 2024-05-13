import csv
import math
import pyjson5

RAFFCROPS = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Crops.json"
ESCROPS = "E:/Program Files/SteamLibrary/steamapps/common/Stardew Valley/Mods/East Scarp (1.6)/[CP] East Scarp/assets/Data/Crops.json"
VANILLAOBJECTS = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
vids = {}
for k, v in VANILLAOBJECTS.items():
    vids[v] = k
CSVOUT = "crops.csv"

fieldNames = ["Name", "Mod", "Type", "Season", "Source", "Days", "Days Ag", "Regrow Day", "Seed Multiplier", "Seed Multiplier AG"]

raff = pyjson5.load(open(RAFFCROPS))
scarp = pyjson5.load(open(ESCROPS))

with open(CSVOUT, "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldNames)
    writer.writeheader()
    for seedID, entry in raff["Changes"][0]["Entries"].items():
        if entry["HarvestItemID"].startswith("{{ModId}}"):
            cropName = entry["HarvestItemID"].split("_", 1)[1]
        else:
            cropName = vids[entry["HarvestItemID"]]
        modName = "Raffadax"
        if len(entry["Seasons"]) < 3:
            season = " ".join(x.title() for x in entry["Seasons"])
        else:
            season = "".join(x[0].title() for x in entry["Seasons"])
        days = sum(entry["DaysInPhase"])
        daysAG = math.floor(0.9 * days)
        regrow = ""
        if entry["RegrowDays"] > 0:
            regrow = entry["RegrowDays"]
        seedMulti = 1
        if days <= 28 and not regrow:
            seedMulti = math.floor(27 / days)
        seedMultiAg = 1
        if daysAG <= 28 and not regrow:
            seedMultiAg = math.floor(27 / daysAG)
        writer.writerow({"Name": cropName,
                         "Mod": modName,
                         "Season": season,
                         "Days": days,
                         "Days Ag": daysAG,
                         "Regrow Day": regrow,
                         "Seed Multiplier": seedMulti,
                         "Seed Multiplier AG": seedMultiAg})
    for seedID, entry in scarp["Changes"][1]["Entries"].items():
        if "HarvestItemID" in entry and entry["HarvestItemID"].startswith("EastScarp_"):
            cropName = entry["HarvestItemID"].split("_", 1)[1]
        elif "HarvestItemId" in entry:
            if entry["HarvestItemId"].startswith("EastScarp_"):
                cropName = entry["HarvestItemId"].split("_", 1)[1]
            else:
                cropName = vids[entry["HarvestItemId"][3:]]
        else:
            cropName = vids[entry["HarvestItemID"]]
        modName = "EastScarp"
        if len(entry["Seasons"]) < 3:
            season = " ".join(x.title() for x in entry["Seasons"])
        else:
            season = "".join(x[0].title() for x in entry["Seasons"])
        days = sum(entry["DaysInPhase"])
        daysAG = math.floor(0.9 * days)
        regrow = ""
        if entry["RegrowDays"] > 0:
            regrow = entry["RegrowDays"]
        seedMulti = 1
        if days <= 28 and not regrow:
            seedMulti = math.floor(27 / days)
        seedMultiAg = 1
        if daysAG <= 28 and not regrow:
            seedMultiAg = math.floor(27 / daysAG)
        writer.writerow({"Name": cropName,
                         "Mod": modName,
                         "Season": season,
                         "Days": days,
                         "Days Ag": daysAG,
                         "Regrow Day": regrow,
                         "Seed Multiplier": seedMulti,
                         "Seed Multiplier AG": seedMultiAg})
