import copy
import math
import json
import pprint
import pyjson5

CROPFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Crops.json"
MYCFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[MYC] Raffadax Multi Yield/HarvestRules.json"
TREEFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/FruitTrees.json"
FORAGEFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[FTM] Forage/content.json"
PFMFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[PFM] Raffadax Production/ProducerRules.json"
BAGTEMPLATE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/python/itembagtemplates.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/ItemBags/"
template = pyjson5.load(open(BAGTEMPLATE, encoding="utf-8"))


def buildBag(id: str, contents: str, items: list, hasqualities=False, isbc=False):
    bag = copy.deepcopy(template)
    bag["BagId"] = "Raffadax.{}".format(id)
    bag["BagName"] = "Raffadax {}".format(contents.title())
    bag["BagDescription"] = "A bag for storing Raffadax {}".format(contents.title())
    basePrice = 10 * len(items)
    bag["Prices"]["Small"] = basePrice
    bag["Prices"]["Medium"] = 3 * basePrice
    bag["Prices"]["Large"] = 10 * basePrice
    bag["Prices"]["Giant"] = 30 * basePrice
    bag["Prices"]["Massive"] = 100 * basePrice
    existingItems = []
    for item in items:
        if item not in existingItems:
            if item.startswith("Raffadax"):
                itemDict = {"Name": None,
                            "IsBigCraftable": isbc,
                            "HasQualities": hasqualities,
                            "RequiredSize": "Small",
                            "ObjectId": item}
            else:
                itemDict = {"Id": item,
                            "IsBigCraftable": isbc,
                            "HasQualities": hasqualities,
                            "RequiredSize": "Small"}
            bag["Items"].append(itemDict)
            existingItems.append(item)
    # print("{}: {}".format(bag["BagId"], len(bag["Items"])))
    OUTFILE = "{}Raffadax.RCP.{}.json".format(OUTPATH, id)
    with open(OUTFILE, 'w', encoding='utf-8') as f:
        json.dump(bag, f, indent=4, ensure_ascii=False)


def cropsBag():
    data = pyjson5.load(open(CROPFILE, encoding="utf-8"))
    mycdata = pyjson5.load(open(MYCFILE, encoding="utf-8"))
    outdata = {"spring": {"seeds": [], "crops": []},
               "summer": {"seeds": [], "crops": []},
               "fall": {"seeds": [], "crops": []},
               "winter": {"seeds": [], "crops": []},
               "special": {"seeds": [], "crops": []}}
    vanillaData = {"Cactus Fruit": ["special"],
                   "Corn": ["summer", "fall"],
                   "Crocus": ["winter"],
                   "Dandelion": ["spring"],
                   "Golden Pumpkin": ["fall"],
                   "Grape": ["fall"],
                   "Hot Pepper": ["summer"],
                   "Jack-O-Lantern": ["fall"],
                   "Poppy": ["summer"],
                   "Pumpkin": ["fall"],
                   "Rhubarb": ["spring"],
                   "Spring Onion": ["spring"],
                   "Tea Leaves": ["special"],
                   "Tomato": ["summer"],
                   "Truffle": ["spring", "summer", "fall"],
                   "Unmilled Rice": ["spring"],
                   "Wheat": ["summer", "fall"]}
    croptoseason = {}
    for seedID, cropData in data["Changes"][0]["Entries"].items():
        cropname = cropData["HarvestItemID"].replace("{{ModId}}", "Raffadax.RCP")
        seedname = seedID.replace("{{ModId}}", "Raffadax.RCP")
        croptoseason[cropname] = {"seed": seedname,
                                  "seasons": cropData["Seasons"]}
    for rule in mycdata["Harvests"]:
        if rule["CropName"] in croptoseason:
            croptoseason[rule["CropName"]]["Additional"] = []
            for item in rule["HarvestRules"]:
                croptoseason[rule["CropName"]]["Additional"].append(item["ItemName"])
        else:
            for item in rule["HarvestRules"]:
                croptoseason[item["ItemName"]] = {"seasons": vanillaData[rule["CropName"]]}
    pprint.pprint(croptoseason)
    for cropID, parsedData in croptoseason.items():
        if cropID != "Raffadax.RCP_GemCap" and cropID != "Raffadax.RCP_GoldenChest":
            if parsedData["seasons"]:
                for season in parsedData["seasons"]:
                    if "seed" in parsedData:
                        outdata[season.lower()]["seeds"].append(parsedData["seed"])
                    if not cropID.isnumeric():
                        outdata[season.lower()]["crops"].append(cropID)
                    if "Additional" in parsedData:
                        outdata[season.lower()]["crops"] += [x for x in parsedData["Additional"] if x not in outdata[season.lower()]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter") and x.startswith("Raffadax.RCP")]
            else:
                outdata["special"]["seeds"].append(parsedData["seed"])
                outdata["special"]["crops"].append(cropID)
                if "Additional" in parsedData:
                    outdata["special"]["crops"] += [x for x in parsedData["Additional"] if x not in outdata["special"]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter")]
        elif cropID != "Raffadax.RCP_GemCap" or cropID != "Raffadax.RCP_GoldenChest":
            outdata["special"]["seeds"].append(parsedData["seed"])
            outdata["special"]["crops"].append(cropID)
            if "Additional" in parsedData:
                outdata["special"]["crops"] += [x for x in parsedData["Additional"] if x not in outdata[season]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter")]
    for season, seasonData in outdata.items():
        buildBag(id="{}.Seeds".format(season.title()), contents="{} Seeds".format(season.title()), items=seasonData["seeds"], hasqualities=True)
        cropList = [x for x in seasonData["crops"] if x.startswith("Raffadax.RCP")]
        buildBag(id="{}.Crops".format(season.title()), contents="{} Crops".format(season.title()), items=cropList, hasqualities=True)


def forageBag():
    data = pyjson5.load(open(FORAGEFILE, encoding="utf-8"))
    commonItems = []
    rareItems = []
    indices = ["SpringItemIndex", "SummerItemIndex", "FallItemIndex", "WinterItemIndex"]
    for area in data["Forage_Spawn_Settings"]["Areas"]:
        for i in indices:
            if isinstance(area[i], list):
                for item in area[i]:
                    if "contents" in item:
                        if area["MinimumSpawnsPerDay"] >= -1:
                            commonItems += item["contents"]
                        else:
                            rareItems += item["contents"]
                    elif "name" in item:
                        if area["MinimumSpawnsPerDay"] >= -1:
                            commonItems.append(item["name"])
                        else:
                            rareItems.append(item["name"])
                    else:
                        pprint.pprint(item)
    commonItems = list(set(commonItems))
    commonItems = [x for x in commonItems if not x.isnumeric()]
    rareItems = list(set(rareItems))
    rareItems = [x for x in rareItems if x not in commonItems and not x.isnumeric()]
    buildBag("Common.Forage", "Common Forage and Trash", commonItems, hasqualities=True)
    buildBag("Rare.Forage", "Rare Forage", rareItems, hasqualities=True)


def treeBag():
    data = pyjson5.load(open(TREEFILE, encoding="utf-8"))
    saplingList = []
    fruitList = []
    for saplingID, treeData in data["Changes"][0]["Entries"].items():
        saplingList.append(saplingID.replace("{{ModId}}", "Raffadax.RCP"))
        if "Fruit" not in treeData:
            pprint.pprint(treeData)
            quit()
        for f in treeData["Fruit"]:
            if f["ItemId"].startswith("{{ModId}}"):
                fruitList.append(f["ItemId"].replace("{{ModId}}", "Raffadax.RCP"))
    buildBag("Saplings", "Saplings", saplingList, hasqualities=True)
    buildBag("Tree.Fruits", "Orchard Products", fruitList, hasqualities=True)


def artisanBag():
    data = pyjson5.load(open(PFMFILE, encoding="utf-8"))
    products = {"Automill": [],
                "Beverage.Keg": [],
                "Dairy": [],
                "Preserves.Jar": [],
                "Wines": [],
                "Divine.Wines": [],
                "Distillations": [],
                "Dry.Packer": [],
                "Fermentation.Tank": [],
                "Flow.Hive": [],
                "Fragrance.Extractor": [],
                "Incubation": [],
                "Juice.Keg": [],
                "Oxidizer": [],
                "Puree.Jar": [],
                "Tea.Keg": [],
                "Charcoal.Kiln": [],
                "Loom": [],
                "Oil.Maker": []}
    for rule in data:
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_AutoMill":
            products["Automill"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Automill"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_BeverageKeg":
            products["Beverage.Keg"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Beverage.Keg"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] in ["(BC)16", "Raffadax.RCP_CheeseProcessor", "Raffadax.RCP_Churn", "Raffadax.RCP_MilkKeg", "(BC)24"]:
            products["Dairy"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Dairy"].append(ao["OutputIdentifier"])
            if rule["InputIdentifier"].startswith("Raffadax.RCP"):
                products["Dairy"].append(rule["InputIdentifier"])
            if "AdditionalFuel" in rule:
                for fuelitem in rule["AdditionalFuel"].keys():
                    products["Dairy"].append(fuelitem)
        if rule["ProducerQualifiedItemId"] in ["(BC)Raffadax.RCP_DeluxePreservesJar", "(BC)15"]:
            products["Preserves.Jar"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Preserves.Jar"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] in ["(BC)Raffadax.RCP_DeluxeWineKeg", "(BC)12"]:
            products["Wines"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Wines"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_MagicCauldron":
            products["Divine.Wines"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Divine.Wines"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_DistillationTank":
            products["Distillations"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Distillations"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_DryPacker":
            products["Dry.Packer"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Dry.Packer"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_FermentationTank":
            products["Fermentation.Tank"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Fermentation.Tank"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_FlowHive":
            products["Flow.Hive"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Flow.Hive"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_FragranceExtractor":
            products["Fragrance.Extractor"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Fragrance.Extractor"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] in ["(BC)Raffadax.RCP_IncubationTank", "(BC)Raffadax.RCP_MoldColony"]:
            products["Incubation"].append(rule["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_JuiceKeg":
            products["Juice.Keg"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Juice.Keg"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_Oxidizer":
            products["Oxidizer"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Oxidizer"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_PureeJar":
            products["Puree.Jar"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Puree.Jar"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)Raffadax.RCP_TeaKeg":
            products["Tea.Keg"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Tea.Keg"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] in ["(BC)114"]:
            products["Charcoal.Kiln"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Charcoal.Kiln"].append(ao["OutputIdentifier"])
            if "FuelIdentifier" in rule:
                products["Charcoal.Kiln"].append(rule["FuelIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)17":
            products["Loom"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Loom"].append(ao["OutputIdentifier"])
        if rule["ProducerQualifiedItemId"] == "(BC)19":
            products["Oil.Maker"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Oil.Maker"].append(ao["OutputIdentifier"])
    for bagid, baglist in products.items():
        bagContents = " ".join(bagid.split(".")).title() + " Products"
        outlist = list(set(baglist))
        outlist = [x for x in outlist if x.startswith("Raffadax.RCP")]
        outlist.sort()
        if bagid in ["Automill", "Distillations", "Oxidizer", "Puree.Jar", "Tea.Keg"]:
            splitlists = splitList(outlist)
            i = 1
            for thislist in splitlists:
                if thislist:
                    outid = bagid if i == 1 else "{}.{}".format(bagid, i)
                    firstLetter = thislist[0].split("_", 1)[1][0:2]
                    lastLetter = thislist[-1].split("_", 1)[1][0:2]
                    buildBag(outid, "{} ({}-{})".format(bagContents, firstLetter, lastLetter), thislist, hasqualities=True)
                    i += 1
        elif bagid == "Fermentation.Tank":
            kombuchas = [x for x in outlist if x.endswith("Kombucha")]
            sparklingwines = [x for x in outlist if "Sparkling" in x]
            misc = [x for x in outlist if not x.endswith("Kombucha") and "Sparkling" not in x]
            halfkomb = int(len(kombuchas) / 2)
            firstKomb = kombuchas[:halfkomb]
            secondKomb = kombuchas[halfkomb:]
            lastLetter = firstKomb[-1].split("_", 1)[1][0:2]
            firstLetter = secondKomb[0].split("_", 1)[1][0:2]
            buildBag("Fermentation.Kombuchas", "{} (Kombuchas A-{})".format(bagContents, lastLetter), firstKomb, hasqualities=True)
            buildBag("Fermentation.Kombuchas.2", "{} (Kombuchas {}-Z)".format(bagContents, firstLetter), secondKomb, hasqualities=True)
            halfspark = int(len(sparklingwines) / 2)
            firstSpark = sparklingwines[:halfspark]
            secondSpark = sparklingwines[halfspark:]
            lastLetter = firstSpark[-1].split("Sparkling", 1)[1][0:2]
            firstLetter = secondSpark[0].split("Sparkling", 1)[1][0:2]
            buildBag("Fermentation.SparklingWines", "{} (Sparkling Wines A-{})".format(bagContents, lastLetter), firstSpark, hasqualities=True)
            buildBag("Fermentation.SparklingWines.2", "{} (Sparkling Wines {})-Z".format(bagContents, firstLetter), secondSpark, hasqualities=True)
            buildBag(bagid, "{} Misc".format(bagContents), misc, hasqualities=True)
        elif bagid == "Juice.Keg":
            juices = [x for x in outlist if "Juice" in x]
            extracts = [x for x in outlist if "Extract" in x]
            misc = [x for x in outlist if not any(y in x for y in ["Juice", "Extract"])]
            halfJuice = int(len(juices) / 2)
            firstJuice = juices[:halfJuice]
            secondJuice = juices[halfJuice:]
            lastLetter = firstJuice[-1].split("_", 1)[1][0:2]
            firstLetter = secondJuice[0].split("_", 1)[1][0:2]
            buildBag("{}.Juices".format(bagid), "{} (Juices A-{})".format(bagContents, lastLetter), firstJuice, hasqualities=True)
            buildBag("{}.Juices.2".format(bagid), "{} (Juices {}-Z)".format(bagContents, firstLetter), secondJuice, hasqualities=True)
            buildBag("{}.Extracts".format(bagid), "{} (Extracts)".format(bagContents), extracts, hasqualities=True)
            buildBag(bagid, "{} Waters & Misc".format(bagContents), misc, hasqualities=True)
        elif bagid == "Preserves.Jar":
            jelly = []
            jam = []
            compote = []
            veggies = []
            misc = []
            for item in outlist:
                if item.endswith("Jelly") and not item.endswith("HoneyJelly"):
                    jelly.append(item)
                elif item.endswith("Jam"):
                    jam.append(item)
                elif item.endswith("Compote") or item.endswith("Preserves") or item.endswith("Chutney"):
                    compote.append(item)
                elif "Pickled" in item or "Preserved" in item:
                    veggies.append(item)
                else:
                    misc.append(item)
            halfJelly = int(len(jelly) / 2)
            firstJelly = jelly[:halfJelly]
            secondJelly = jelly[halfJelly:]
            lastLetter = firstJelly[-1].split("_", 1)[1][0:2]
            firstLetter = secondJelly[0].split("_", 1)[1][0:2]
            buildBag("{}.Jelly".format(bagid), "{} (Jelly A-{})".format(bagContents, lastLetter), firstJelly, hasqualities=True)
            buildBag("{}.Jelly.2".format(bagid), "{} (Jelly {}-Z)".format(bagContents, firstLetter), secondJelly, hasqualities=True)
            buildBag("{}.Jams".format(bagid), "{} (Jams)".format(bagContents), jam, hasqualities=True)
            buildBag("{}.Compotes".format(bagid), "{} (Compotes, Preserves, Chutneys)".format(bagContents), compote, hasqualities=True)
            buildBag(bagid, "{} (Honey Jelly & Misc)".format(bagContents), misc, hasqualities=True)
        elif bagid == "Wines":
            wineList = [x for x in outlist if x not in products["Tea.Keg"]]
            secondWords = ["Brandy", "Balsam", "Midus", "Drakas", "Ismjod", "Novum"]
            thirdWords = ["PortWine", "PortMead", "Port", "Dancing", "Frostmjod", "Laughing", "Waldmeisterbowle"]
            firstpass = []
            secondpass = []
            thirdpass = []
            misc = []
            for item in wineList:
                if any(x in item for x in thirdWords):
                    thirdpass.append(item)
                elif any(x in item for x in secondWords):
                    secondpass.append(item)
                else:
                    firstpass.append(item)
            splitfirst = splitList(firstpass)
            i = 1
            for thislist in splitfirst:
                if thislist:
                    outid = "{}".format(bagid)
                    if i > 1:
                        outid += ".{}".format(i)
                    firstLetter = thislist[0].split("_", 1)[1][0:2]
                    lastLetter = thislist[-1].split("_", 1)[1][0:2]
                    buildBag(outid, "{} (Wines, Meads, & Misc {}-{})".format(bagContents, firstLetter, lastLetter), thislist, hasqualities=True)
                    i += 1
            splitsecond = splitList(secondpass)
            i = 1
            for thislist in splitsecond:
                if thislist:
                    outid = "{}.SecondPass".format(bagid)
                    if i > 1:
                        outid += ".{}".format(i)
                    firstLetter = thislist[0].split("_", 1)[1][0:2]
                    lastLetter = thislist[-1].split("_", 1)[1][0:2]
                    buildBag(outid, "{} (Brandy & Balsam {}-{})".format(bagContents, firstLetter, lastLetter), thislist, hasqualities=True)
                    i += 1
            splitthird = splitList(thirdpass)
            i = 1
            for thislist in splitthird:
                if thislist:
                    outid = "{}.ThirdPass".format(bagid)
                    if i > 1:
                        outid += ".{}".format(i)
                    firstLetter = thislist[0].split("_", 1)[1][0:2]
                    lastLetter = thislist[-1].split("_", 1)[1][0:2]
                    buildBag(outid, "{} (Ports {}-{})".format(bagContents, firstLetter, lastLetter), thislist, hasqualities=True)
                    i += 1
        else:
            buildBag(bagid, bagContents, outlist, hasqualities=True)


def splitList(thislist):
    outData = []
    if len(thislist) > 600:
        thissize = math.ceil(len(thislist) / 4)
    elif len(thislist) > 400:
        thissize = math.ceil(len(thislist) / 3)
    else:
        thissize = math.ceil(len(thislist) / 2)
    while len(thislist) > thissize:
        piece = thislist[:thissize]
        outData.append(piece)
        thislist = thislist[thissize:]
    outData.append(thislist)
    return outData


if __name__ == "__main__":
    cropsBag()
    forageBag()
    treeBag()
    artisanBag()
