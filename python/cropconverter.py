import argparse
import copy
import os
import pprint
from dataclasses import dataclass, field
from math import ceil, floor
from typing import Optional

import pyjson5
from PIL import Image

CATEGORIES = {"Flower": -80,
              "Fruit": -79,
              "Greens": -81,
              "Mineral": -2,
              "Seeds": -74,
              "Vegetable": -75}

CATINDICES = {"-2": "Mineral",
              "-74": "Seeds",
              "-75": "Vegetable",
              "-79": "Fruit",
              "-80": "Flower",
              "-81": "Forage"}


@dataclass
class Buff():
    Duration: int = 0
    Id: str = ""
    FarmingLevel: Optional[int] = 0
    FishingLevel: Optional[int] = 0
    ForagingLevel: Optional[int] = 0
    LuckLevel: Optional[int] = 0
    MiningLevel: Optional[int] = 0
    Attack: Optional[int] = 0
    Defense: Optional[int] = 0
    MagnetRadius: Optional[int] = 0
    MaxStamina: Optional[int] = 0

    def to_dict(self):
        outDict = {"Id": "",
                   "Duration": 0,
                   "IsDebuff": False,
                   "CustomAttributes": {}}
        for k, v in self.__dict__.items():
            if k in ["Id", "Duration"]:
                outDict[k] == v
            else:
                if v:
                    outDict["CustomAttributes"][k] = v
                if v < 0:
                    outDict["IsDebuff"] = True
        return outDict


@dataclass
class Crop():
    Seasons: list = field(default_factory=lambda: [])
    DaysInPhase: list = field(default_factory=lambda: [])
    HarvestItemID: str = ""
    Texture: str = ""
    RegrowDays: Optional[int] = -1
    IsRaised: Optional[bool] = False
    IsPaddyCrop: Optional[bool] = False
    NeedsWatering: Optional[bool] = True
    HarvestMethod: Optional[str] = "Grab"
    HarvestMinStack: Optional[int] = 1
    HarvestMaxStack: Optional[int] = 1
    HarvestMinQuality: Optional[int] = 0
    HarvestMaxQuality: Optional[int] = 0
    HarvestMaxIncreasePerFarmingLevel: Optional[int] = 0
    ExtraHarvestChance: Optional[int] = 0
    SpriteIndex: Optional[int] = 0
    TintColors: Optional[list] = field(default_factory=lambda: [])
    CountForMonoculture: Optional[bool] = False
    CountForPolyculture: Optional[bool] = False
    PlantableLocationRules: Optional[dict] = field(default_factory=lambda: [])

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Seasons", "DaysInPhase", "HarvestItemID", "Texture"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


@dataclass
class SVObject():
    Name: str = ""
    Displayname: str = ""
    Description: str = ""
    Type: str = ""
    Category: int = 0
    Price: int = 0
    Texture: str = ""
    SpriteIndex: int = 0
    Edibility: Optional[int] = -1
    IsDrink: Optional[bool] = False
    GeodeDrops: Optional[list] = field(default_factory=lambda: [])
    Buffs: Optional[list] = field(default_factory=lambda: [])
    ArtifactSpotChances: Optional[dict] = field(default_factory=lambda: {})
    ContextTags: Optional[list] = field(default_factory=lambda: [])
    ExcludeFromRandomSale: Optional[bool] = False
    ExcludeFromFishingCollection: Optional[bool] = False
    ExcludeFromShippingCollection: Optional[bool] = False

    def to_dict(self):
        outDict = {}
        mandatoryKeys = ["Name", "DisplayName", "Description", "Type",
                         "Category", "Price"]
        for k, v in self.__dict__.items():
            if k in mandatoryKeys or v:
                outDict[k] = v
        return outDict


def buildCrops(srcDir, modId, objectData, objectSprites, i18n, spritesheet):
    cropDir = "{}Crops".format(srcDir)
    newCrops = {"Action": "EditData",
                "Target": "Data/Crops",
                "Entries": {}}
    jsonFiles = []
    cropSprites = {}
    i = len(objectSprites) + 1
    j = 0
    for entry in objectscan(cropDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # seed object
        seedObj = SVObject()
        nameStr = data["SeedName"].replace(" ", "")
        seedObj.Name = "{}_{}".format(modId, nameStr)
        i18n["en"]["{}.Displayname".format(nameStr)] = data["Name"]
        seedObj.Displayname = "{{i18n: {}.Displayname}}".format(nameStr)
        # build the description.
        i18n["en"]["{}.Description".format(nameStr)] = data["SeedDescription"]
        seedObj.Description = "{{i18n: {}.Description}}".format(nameStr)
        seedObj.Type = "Seeds"
        seedObj.Category = -74
        if "SeedPurchasePrice" in data:
            seedObj.Price = data["SeedPurchasePrice"]
        seedObj.Texture = "assets/textures/{}.png".format(spritesheet)
        seedObj.SpriteIndex = i
        spritename = jf.rsplit("/", 1)[0] + "/seeds.png"
        if "SeedNameLocalization" in data:
            for langKey, langStr in data["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "SeedDescriptionLocalization" in data:
            for langKey, langStr in data["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        objectSprites[spritename] = seedObj.SpriteIndex
        objectData["Entries"][seedObj.Name] = seedObj.to_dict()

        # crop object
        cropObj = Crop()
        cropObj.Seasons = data["Seasons"]
        cropObj.DaysInPhase = data["Phases"]
        cropObj.HarvestItemID = "{}_{}".format(modId, data["Product"].replace(" ", ""))
        cropObj.Texture = "assets/textures/crops.png"
        if "RegrowthPhase" in data:
            cropObj.RegrowDays = data["RegrowthPhase"]
        if "TrellisCrop" in data:
            cropObj.IsRaised = data["TrellisCrop"]
        if "HarvestWithScythe" in data:
            cropObj.HarvestMethod = "Scythe"
        if "Bonus" in data:
            if "MinimumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMinStack = data["Bonus"]["MinimumPerHarvest"]
            if "MaximumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMaxStack = data["Bonus"]["MinimumPerHarvest"]
            if "MaxIncreasePerFarmLevel" in data["Bonus"]:
                cropObj.HarvestMaxIncreasePerFarmingLevel = data["Bonus"]["MaxIncreasePerFarmLevel"]
            if "ExtraChance" in data["Bonus"]:
                cropObj.ExtraHarvestChance = data["Bonus"]["ExtraChance"]
        if "Colors" in data and data["Colors"]:
            cropObj.TintColors = data["Colors"]
        cropObj.SpriteIndex = j
        cropspritename = jf.rsplit("/", 1)[0] + "/crop.png"
        cropSprites[cropspritename] = cropObj.SpriteIndex
        if "CropType" in data and data["CropType"]:
            if data["CropType"] == "Paddy":
                cropObj.IsPaddyCrop = True
            if data["CropType"] == "IndoorsOnly":
                newRule = {"Id": "{}_Rule".format(seedObj.Name),
                           "Result": "Deny",
                           "Condition": "LOCATION_IS_OUTDOORS Here"}
                cropObj.PlantableLocationRules.append(newRule)
        newCrops["Entries"][seedObj.Name] = cropObj.to_dict()
        i += 1
        j += 1
    return [objectData, newCrops, cropSprites, objectSprites, i18n]


def buildObjects(srcDir, modId, spritesheet):
    newObjects = {"Action": "EditData",
                  "Target": "Data/Objects",
                  "Entries": {}
                  }
    newGifts = {"Action": "EditData",
                "Target": "Data/NPCGiftTastes",
                "Fields": []}
    i18n = {"en": {}}
    i = 0
    jsonFiles = []
    spriteFiles = {}
    objDir = "{}Objects".format(srcDir)
    # tasteKeys = {"Love": 1, "Like": 3, "Neutral": 9, "Dislike": 5, "Hate": 7}
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        objData = pyjson5.load(open(jf, encoding="utf-8"))
        newObj = SVObject()
        nameStr = objData["Name"].replace(" ", "")
        newObj.Name = "{}_{}".format(modId, nameStr)
        newObj.Displayname = "{{i18n:{}.DisplayName}}".format(nameStr)
        i18n["en"]["{}.DisplayName".format(nameStr)] = objData["Name"]
        if isinstance(objData["Category"], str):
            if objData["Category"].strip("-").isnumeric():
                newObj.Category = int(objData["Category"])
                newObj.Type = CATINDICES[str(objData["Category"])]
            else:
                newObj.Type = objData["Category"]
                if newObj.Type in CATEGORIES:
                    newObj.Category = CATEGORIES[newObj.Type]
                else:
                    print("No Cat found for {}".format(newObj.Type))
        else:
            print("Non string cat for {}".format(newObj.Name))
        if "Description" in objData:
            newObj.Description = "{{i18n:{}.Description}}".format(objData["Name"])
            i18n["en"]["{}.Description".format(nameStr)] = objData["Description"]
        if "Price" in objData:
            newObj.Price = objData["Price"]
        newObj.Texture = "assets/textures/{}.png".format(spritesheet)
        newObj.SpriteIndex = i
        if "Edibility" in objData:
            newObj.Edibility = objData["Edibility"]
        if "EdibleIsDrink" in objData:
            newObj.IsDrink = objData["EdibleIsDrink"]
        if "EdibleBuffs" in objData:
            newBuff = Buff()
            newBuff.Id = "{}_buff".format(newObj.Name)
            for bk, bv in objData["EdibleBuffs"].items():
                if bk in ["Farming", "Mining", "Foraging", "Luck", "Fishing"]:
                    setattr(newBuff, "{}Level".format(bk), bv)
                else:
                    setattr(newBuff, bk, bv)
            newObj.Buffs.append(newBuff.to_dict())
        if "ContextTags" in objData:
            newObj.ContextTags = objData["ContextTags"]
        if "CategoryTextOverride" in objData:  # this may have to become a CustomField
            newObj.ContextTags.append("category_{}".format(objData["CategoryTextOverride"].lower().replace(" ", "_")))
        if "NameLocalization" in objData:
            for langKey, langStr in objData["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "DescriptionLocalization" in objData:
            for langKey, langStr in objData["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        newObjects["Entries"][newObj.Name] = newObj.to_dict()
        spritename = jf[0:-5] + ".png"
        spriteFiles[spritename] = newObj.SpriteIndex
        i += 1
    return [newObjects, spriteFiles, newGifts, i18n]


def buildSprites(spriteList, dstDir, fileName, spriteType="objects"):
    if spriteType == "objects":
        imgHeight = ceil(len(spriteList) / 24) * 16
        imgWidth = 384
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 24) * 16
            y = floor(sidx / 24) * 16
            base.paste(img, (x, y))
    elif spriteType == "crops":
        imgWidth = 256
        imgHeight = ceil(len(spriteList) / 2) * 32
        base = Image.new("RGBA", (imgWidth, imgHeight))
        # maxsize = (128, 32)
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 2) * 128
            y = floor(sidx / 2) * 32
            # no resizing needed
            base.paste(img, (x, y))
    # base.show()
    outPath = "{}{}.png".format(dstDir, fileName)
    base.save(outPath)


def objectscan(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from objectscan(entry.path)
        elif entry.name.endswith((".json")):
            yield entry


if __name__ == "__main__":
    # get the path to the current file
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", dest="convertMethod", type=str, help="Selects Method, options: crops")
    parser.add_argument("--s", dest="sourceDirectory", type=str, help="Source Directory, e.g. [JA] Your Json Assets Mod")
    parser.add_argument("--d", dest="destDirectory", type=str, help="Destination Directory")
    args = parser.parse_args()
    outData = {"Format": "1.30.0",
               "Changes": []}
    dir_path = os.path.dirname(os.path.realpath(__file__))
    rootDir = dir_path.rsplit("\\", 1)[0].replace("\\", "/")
    oldFiles = "{}/1.5.6 Files/".format(rootDir)
    srcDir = "{}[JA] Raffadax Crops/".format(oldFiles)
    dstDir = "{}/1.6 Files/".format(rootDir)
    if args.sourceDirectory:
        srcDir = args.sourceDirectory
    if args.destDirectory:
        dstDir = args.destDirectory
    if args.convertMethod.lower() == "crops":
        srcDir = "{}[JA] Raffadax Crops/".format(oldFiles)
        modId = "Raffadax.Crops"
        # crop objects
        objectData, objectSprites, giftData, i18n = buildObjects(srcDir, modId, "cropobjects")
        # seed objects and cropdata
        objectData, cropData, cropSprites, objectSprites, i18n = buildCrops(srcDir, modId, objectData, objectSprites, i18n, "cropobjects")
        # write data to file
        jsonOut = {"Format": "1.30.0",
                   "Changes": [objectData, cropData]}
        outPath = "{}Crops/content.json".format(dstDir)
        outData = pyjson5.dumps(jsonOut)
        if not os.path.exists("{}Crops".format(dstDir)):
            os.mkdir("{}Crops".format(dstDir))
        with open(outPath, 'w') as f:
            f.write(outData)
        print("Content Patcher data written to {}".format(outPath))
        # write i18n data
        if not os.path.exists("{}i18n/Crops".format(dstDir)):
            os.mkdir("{}i18n/Crops".format(dstDir))
        for langKey, langData in i18n.items():
            outPath = "{}i18n/Crops/{}.json".format(dstDir, langKey)
            outData = pyjson5.dumps(langData)
            with open(outPath, 'w') as f:
                f.write(outData)
        print("i18n data written to {}".format("{}i18n/Crops".format(dstDir)))
        # make sprites
        spriteDir = "{}assets/textures/".format(dstDir)
        if not os.path.exists(spriteDir):
            os.mkdir(spriteDir)
        buildSprites(objectSprites, spriteDir, "cropobjects", "objects")
        buildSprites(cropSprites, spriteDir, "crops", "crops")
        print("Sprites saved to {}".format(spriteDir))
        # TODO: ExcludeWithMod
        # TODO: Make spritesheet
        # TODO: Handle gift tastes
