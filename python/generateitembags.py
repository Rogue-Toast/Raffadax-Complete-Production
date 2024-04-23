import copy
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
    bag["BagDescription"] = "A bag for storing Raffadax {}.".format(contents.title())
    basePrice = 10 * len(items)
    bag["Prices"]["Small"] = basePrice
    bag["Prices"]["Medium"] = 3 * basePrice
    bag["Prices"]["Large"] = 10 * basePrice
    bag["Prices"]["Giant"] = 30 * basePrice
    bag["Prices"]["Massive"] = 100 * basePrice
    for item in items:
        itemDict = {"Name": None,
                    "IsBigCraftable": isbc,
                    "HasQualities": hasqualities,
                    "RequiredSize": "Small",
                    "ObjectId": item}
        bag["Items"].append(itemDict)
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
    for cropID, parsedData in croptoseason.items():
        if cropID != "Raffadax.RCP_GemCap" and cropID != "Raffadax.RCP_GoldenChest":
            if parsedData["seasons"]:
                for season in parsedData["seasons"]:
                    outdata[season]["seeds"].append(parsedData["seed"])
                    if not cropID.isnumeric():
                        outdata[season]["crops"].append(cropID)
                    if "Additional" in parsedData:
                        outdata[season]["crops"] += [x for x in parsedData["Additional"] if x not in outdata[season]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter") and x.startswith("Raffadax.RCP")]
            else:
                outdata["special"]["seeds"].append(parsedData["seed"])
                outdata["special"]["crops"].append(cropID)
                if "Additional" in parsedData:
                    outdata["special"]["crops"] += [x for x in parsedData["Additional"] if x not in outdata[season]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter")]
        elif cropID != "Raffadax.RCP_GemCap" or cropID != "Raffadax.RCP_GoldenChest":
            outdata["special"]["seeds"].append(parsedData["seed"])
            outdata["special"]["crops"].append(cropID)
            if "Additional" in parsedData:
                outdata["special"]["crops"] += [x for x in parsedData["Additional"] if x not in outdata[season]["crops"] and not x.endswith("Seeds") and not x.endswith("Starter")]
    for season, seasonData in outdata.items():
        buildBag(id="{}.Seeds".format(season.title()), contents="{} Seeds".format(season.title()), items=seasonData["seeds"])
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
    buildBag("Saplings", "Saplings", saplingList)
    buildBag("Tree.Fruits", "Orchard Products", fruitList)


def artisanBag():
    data = pyjson5.load(open(PFMFILE, encoding="utf-8"))
    products = {"Automill": [],
                "Beverage.Keg": [],
                "Dairy": [],
                "Preserves.Jar": [],
                "Wines": [],
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
        if rule["ProducerQualifiedItemId"] in ["(BC)Raffadax.RCP_DeluxeWineKeg", "(BC)Raffadax.RCP_MagicCauldron", "(BC)12"]:
            products["Wines"].append(rule["OutputIdentifier"])
            if "AdditionalOutputs" in rule:
                for ao in rule["AdditionalOutputs"]:
                    products["Wines"].append(ao["OutputIdentifier"])
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
        buildBag(bagid, bagContents, outlist)


if __name__ == "__main__":
    cropsBag()
    forageBag()
    treeBag()
    artisanBag()
