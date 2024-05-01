"""Converts Raffadax JSON Assets to Content patcher.

Run convertstf.py first to generate i18n strings."""

import argparse
import copy
import json  # for writing
import os
import pprint
import re
from dataclasses import dataclass, field
from math import ceil, floor
from typing import Optional

import pyjson5  # for reading
from unidecode import unidecode  # converts diacritics to ascii
from PIL import Image
from classes import BigObject, Buff, Crop, FruitTree, MeleeWeapon, SVObject
from writeLangData import writeLanguageData

CATEGORIES = {"ArtisanGoods": -26,
              "Building Resources": -16,
              "Cooking": -7,
              "Crafting": -8,
              "Flower": -80,
              "Fruit": -79,
              "Gem": -2,
              "Greens": -81,
              "Metal Resource": -15,
              "Metal": -15,
              "Milk": -6,
              "Mineral": -12,
              "Seeds": -74,
              "Trash": -20,
              "Vegetable": -75}

CATINDICES = {"-2": "Gem",
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

VANILLANPCS = ["Abigail", "Alex", "Caroline", "Clint", "Demetrius", "Dwarf",
               "Elliott", "Emily", "Evelyn", "George", "Gus", "Haley", "Harvey",
               "Jas", "Jodi", "Kent", "Krobus", "Leah", "Leo", "Lewis", "Linus",
               "Marnie", "Maru", "Pam", "Penny", "Pierre", "Robin", "Sam",
               "Sandy", "Sebastian", "Shane", "Vincent", "Willy", "Wizard"]

RAFFNPCS = ["Amanra", "Astrid", "Coyote", "Mephisto", "Puck", "Shuck", "Xolotl"]

MODNPCS = {
    # "Amanra": "Raffadax.NPCs",
    # "Astrid": "Raffadax.NPCs",
    # "Coyote": "Raffadax.NPCs",
    # "Mephisto": "Raffadax.NPCs",
    # "Puck": "Raffadax.NPCs",
    # "Shuck": "Raffadax.NPCs",
    # "Xolotl": "Raffadax.NPCs",
    "Beatrice": "attonbomb.Beatrice",
    "Marlon": "FlashShifter.StardewValleyExpandedCP",
    "Olivia": "FlashShifter.StardewValleyExpandedCP",
    "Susan": "FlashShifter.StardewValleyExpandedCP",
    "Andy": "FlashShifter.StardewValleyExpandedCP",
    "Apples": "FlashShifter.StardewValleyExpandedCP",
    "Claire": "FlashShifter.StardewValleyExpandedCP",
    "Martin": "FlashShifter.StardewValleyExpandedCP",
    "Morris": "FlashShifter.StardewValleyExpandedCP",
    "Sophia": "FlashShifter.StardewValleyExpandedCP",
    "Victor": "FlashShifter.StardewValleyExpandedCP",
    "Morgan": "FlashShifter.StardewValleyExpandedCP",
    "Gunther": "FlashShifter.StardewValleyExpandedCP",
    "Gregory": "CPBoardingHouse",
    "Sheila": "CPBoardingHouse",
    "Hekate": "Tarniyar.NPC.GV.mod",
    "Hephaestus": "Tarniyar.NPC.GV.mod",
    "Jacob": "Lemurkat.JacobEloise.CP",
    "Eloise": "Lemurkat.JacobEloise.CP",
    "Madam": "FishingIslandNPC",
    "Jade": "malic.cp.jadeNPC",
    "Alecto": "ZoeDoll.NPCAlecto",
    "Wednesday": "RaddBlaster.Wednesday",
    "Sorren": "annachibi.SorrenNPC",
    "Ayeisha": "TheLimeyDragon.Ayeisha",
    "Denver": "MISSINGID",
    "Kim": "KimJyeulNPC.ExnoticTest",
    "Mike": "SYS.mike",
    "Mona": "Zilsara.Mona",
    "Muadhnait": "Asari.Muadhnait",
    "Nikolai": "Fellowclown.PC",
    "Paul": "Ginnyclaire.Paul",
    "Shiko": "Papaya.ShikoTakahashi",
    "Zoro": "EmpressKimi.Zoro"
}

NAMERE = r"[^a-zA-Z0-9_\.]"

EXISTINGIDS = []

NEWIDS = pyjson5.load(open("newids.json", encoding="utf-8"))
FORAGEITEMS = pyjson5.load(open("forageitems.json", encoding="utf-8"))


def buildBigObjects(srcDir, modId, spritesheet, mode, i18n=None):
    newObjects = {"LogName": "Raffadax New Big Objects - {}".format(mode),
                  "Action": "EditData",
                  "Target": "Data/BigCraftables",
                  "Entries": {}
                  }
    objTexture = {"LogName": "Raffadax Big Object Textures - {}".format(mode),
                  "Action": "Load",
                  "Target": "Mods/{}/BigObjects/{}".format(modId, mode),
                  "FromFile": "assets/textures/{}.png".format(spritesheet)}
    machines = ["Auto Mill", "Beverage Keg", "Deluxe Preserves Jar",
                "Deluxe Wine Keg", "Distillation Tank", "Dry Packer",
                "Fermentation Tank", "Flow Hive", "Fragrance Extractor",
                "Golden Spindle", "Incubation Tank", "Juice Keg",
                "Magic Cauldron", "Milk Keg", "Oxidizer", "Puree Jar",
                "Tea Keg"]
    if not i18n:
        i18n = {"en": {}}
    i = 0
    spriteFiles = {}
    jsonFiles = []
    objDir = "{}BigCraftables".format(srcDir)
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        bo = BigObject()
        nameStr = re.sub(NAMERE, "", objData["Name"])
        bo.Name = "{}_{}".format(modId, nameStr)
        bo.DisplayName = "{{{{i18n:{}.DisplayName}}}}".format(nameStr)
        i18n["en"]["{}.DisplayName".format(nameStr)] = objData["Name"]
        bo.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        i18n["en"]["{}.Description".format(nameStr)] = objData["Description"]
        if "Price" in objData:
            bo.Price = objData["Price"]
        if "ProvidesLight" in objData and objData["ProvidesLight"]:
            bo.IsLamp = True
        bo.Texture = "Mods/{}/BigObjects/{}".format(modId, mode)
        bo.SpriteIndex = i
        idxIncrement = 1
        if "ReserveExtraIndexCount" in objData:
            frameCount = objData["ReserveExtraIndexCount"]
            idxIncrement += frameCount
        spritename = jf[0:-5] + ".png"
        spriteFiles[spritename] = bo.SpriteIndex
        if idxIncrement > 1:
            for j in range(1, frameCount + 1):
                frameName = "{}-{}.png".format(jf[0:-5], j + 1)
                spriteFiles[frameName] = bo.SpriteIndex + j
        # pprint.pprint(spriteFiles)
        bo.ContextTags.append("raffadax_bigcraftable")
        if "Recipe" in objData and objData["Recipe"] and isinstance(objData["Recipe"], dict):
            bo.ContextTags.append("raffadax_crafted_bigcraftable")
        if objData["Name"] in machines:
            bo.ContextTags.append("raffadax_machine")
        newObjects["Entries"][bo.Name] = bo.to_dict()
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
        i += idxIncrement
    # # Mythril Anvil
    # ma = BigObject()
    # ma.Name = "{}_MythrilAnvil".format(modId)
    # ma.DisplayName = "{{i18n:MythrilAnvil.DisplayName}}"
    # ma.Description = "{{i18n:MythrilAnvil.Description}}"
    # ma.Texture = "Mods/{}/BigObjects/{}".format(modId, mode)
    # ma.Price = 1
    # ma.SpriteIndex = i
    # idxIncrement = 1
    # spritename = "mythrilanvil.png"
    # spriteFiles[spritename] = ma.SpriteIndex
    # ma.ContextTags.append("raffadax_bigcraftable")
    # ma.ContextTags.append("raffadax_crafted_bigcraftable")
    # ma.ContextTags.append("raffadax_machine")
    # newObjects["Entries"][ma.Name] = ma.to_dict()
    # i18n["en"]["MythrilAnvil.DisplayName"] = "Mythril Anvil"
    # i18n["en"]["MythrilAnvil.Description"] = "Unbelievably light for such a large object, this mystic anvil can imbue common weapons with the essence of divine libations to create sacred blades."
    return [newObjects, spriteFiles, i18n, objTexture]


def buildCooking(srcDir, modId, vanillaObjects, i18n):
    objDir = "{}Objects".format(srcDir)
    newRecipes = {"LogName": "Raffadax New Cooking Recipes",
                  "Action": "EditData",
                  "Target": "Data/CookingRecipes",
                  "Entries": {}}
    jsonFiles = []
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        if "Recipe" in objData and objData["Recipe"] and (objData["Category"] == "Cooking" or objData["Category"] == -7):
            outName = unidecode(objData["Name"])
            outName = re.sub(NAMERE, "", outName)
            output = "{}_{} {}".format(modId, outName, objData["Recipe"]["ResultCount"])
            ingredients = []
            for iNode in objData["Recipe"]["Ingredients"]:
                if isinstance(iNode["Object"], int) or iNode['Object'].isnumeric():
                    iStr = "{} {}".format(iNode['Object'], iNode["Count"])
                elif iNode["Object"] in vanillaObjects:
                    iStr = "{} {}".format(vanillaObjects[iNode["Object"]], iNode["Count"])
                else:
                    nameStr = unidecode(iNode["Object"])
                    nameStr = re.sub(NAMERE, "", nameStr)
                    iStr = "{}_{} {}".format(modId, nameStr, iNode["Count"])
                ingredients.append(iStr)
            newRecipes["Entries"]["{}_{}".format(modId, outName)] = "{}/2 2/{}/null/{{{{i18n:{}.RecipeName}}}}".format(" ".join(ingredients), output, outName)
            i18n["en"]["{}.RecipeName".format(outName)] = objData["Name"]
    return [newRecipes, i18n]


def buildCrafting(srcDir, modId, vanillaObjects, i18n):
    objDir = "{}Objects".format(srcDir)
    bigObjDir = "{}BigCraftables".format(srcDir)
    newRecipes = {"LogName": "Raffadax New Crafting Recipes",
                  "Action": "EditData",
                  "Target": "Data/CraftingRecipes",
                  "Entries": {}}
    jsonFiles = []
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for entry in objectscan(bigObjDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        if "Recipe" in objData and objData["Recipe"] and (("Category" in objData and objData["Category"] != "Cooking" and objData["Category"] != -7) or jf.endswith("big-craftable.json")):
            output = "{}_{} {}".format(modId, objData["Name"].replace(" ", ""), objData["Recipe"]["ResultCount"])
            outName = unidecode(objData["Name"])
            outName = re.sub(NAMERE, "", outName)
            ingredients = []
            isBC = "false"
            if jf.endswith("big-craftable.json"):
                isBC = "true"
            for iNode in objData["Recipe"]["Ingredients"]:
                if isinstance(iNode["Object"], int) or iNode['Object'].isnumeric():
                    iStr = "{} {}".format(iNode['Object'], iNode["Count"])
                elif iNode["Object"] in vanillaObjects:
                    iStr = "{} {}".format(vanillaObjects[iNode["Object"]], iNode["Count"])
                else:
                    nameStr = re.sub(NAMERE, "", iNode["Object"])
                    iStr = "{}_{} {}".format(modId, nameStr, iNode["Count"])
                ingredients.append(iStr)
            newRecipes["Entries"]["{}_{}".format(modId, outName)] = "{}/Home/{}/{}/null/{{{{i18n:{}.RecipeName}}}}".format(" ".join(ingredients), output, isBC, outName)
            i18n["en"]["{}.RecipeName".format(outName)] = objData["Name"]
    # # mythril Anvil
    # anvilIngredients = "{}_MythrilBar 50".format(modId)
    # anvilOutput = "{}_MythrilAnvil 1".format(modId)
    # anvilStr = "{}/Home/{}/{}/null/{{{{i18n:MythrilAnvil.RecipeName}}}}".format(anvilIngredients, anvilOutput, True)
    # newRecipes["Entries"]["{}_MythrilAnvil".format(modId)] = anvilStr
    # i18n["en"]["MythrilAnvil.RecipeName"] = "Mythril Anvil"
    return [newRecipes, i18n]


def buildCrops(srcDir, modId, objectData, objectSprites, i18n, spritesheet, vanillaObjects):
    cropDir = "{}Crops".format(srcDir)
    cropTexture = {"LogName": "Raffadax Crop Textures",
                   "Action": "Load",
                   "Target": "Mods/{}/Crops".format(modId),
                   "FromFile": "assets/textures/crops.png"}
    giantTexture = {"LogName": "Raffadax Giant Crop Textures",
                    "Action": "Load",
                    "Target": "Mods/{}/GiantCrops".format(modId),
                    "FromFile": "assets/textures/giantcrops.png"}
    newCrops = {"LogName": "Raffadax New Crops",
                "Action": "EditData",
                "Target": "Data/Crops",
                "Entries": {}}
    newGiants = {"LogName": "Raffadax New Giant Crops",
                 "Action": "EditData",
                 "Target": "Data/GiantCrops",
                 "Entries": {}}
    jsonFiles = []
    cropSprites = {}
    giantSprites = {}
    i = len(objectSprites)  # object sprite indices
    j = 0  # Crop sprite indices
    x = 0  # Giant sprite indices
    y = 0
    for entry in objectscan(cropDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        if data["Name"] == "Broccoli":
            continue
        # seed object
        seedObj = SVObject()
        nameStr = unidecode(data["SeedName"])
        nameStr = re.sub(NAMERE, "", nameStr)
        itemID = "{}_{}".format(modId, nameStr)
        if itemID not in EXISTINGIDS:
            EXISTINGIDS.append(itemID)
        else:
            print("{} from '{}' in Crops already exists.".format(itemID, data["Name"]))
        seedObj.Name = itemID
        i18n["en"]["{}.Displayname".format(nameStr)] = data["SeedName"]
        seedObj.DisplayName = "{{{{i18n: {}.Displayname}}}}".format(nameStr)
        # build the description.
        i18n["en"]["{}.Description".format(nameStr)] = data["SeedDescription"]
        seedObj.Description = "{{{{i18n: {}.Description}}}}".format(nameStr)
        seedObj.Type = "Seeds"
        seedObj.Category = -74
        if "SeedPurchasePrice" in data:
            seedObj.Price = data["SeedPurchasePrice"]
        seedObj.Texture = "Mods/{}/Objects/Crops".format(modId)
        seedObj.SpriteIndex = i
        seedObj.ContextTags.append("raffadax_seeds_object")
        seedObj.ContextTags.append("raffadax_object")
        seedObj.Edibility = -300
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
        if not cropObj.Seasons:
            cropObj.Seasons = ["Spring", "Summer", "Fall", "Winter"]
        cropObj.DaysInPhase = data["Phases"]
        cropName = unidecode(data["Product"])
        cropName = re.sub(NAMERE, "", cropName)
        if data["Product"] in vanillaObjects:
            cropObj.HarvestItemID = vanillaObjects[data["Product"]]
        else:
            cropObj.HarvestItemID = "{}_{}".format(modId, cropName)
        cropObj.Texture = "Mods/{}/Crops".format(modId)
        if "RegrowthPhase" in data:
            cropObj.RegrowDays = data["RegrowthPhase"]
        if "TrellisCrop" in data:
            cropObj.IsRaised = data["TrellisCrop"]
        if "HarvestWithScythe" in data and data["HarvestWithScythe"]:
            cropObj.HarvestMethod = "Scythe"
        if "Bonus" in data:
            if "MinimumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMinStack = data["Bonus"]["MinimumPerHarvest"]
            if "MaximumPerHarvest" in data["Bonus"]:
                cropObj.HarvestMaxStack = data["Bonus"]["MinimumPerHarvest"]
            # if "MaxIncreasePerFarmLevel" in data["Bonus"]:
            #     cropObj.HarvestMaxIncreasePerFarmingLevel = data["Bonus"]["MaxIncreasePerFarmLevel"]
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
                newRule = {"Id": "IndoorsOnly",
                           "Condition": "LOCATION_IS_OUTDOORS Here",
                           "PlantedIn": "Any",
                           "Result": "Deny",
                           "DeniedMessage": "{{{{i18n:{}.IndoorsOnly}}}}.".format(nameStr)}
                i18n["en"]["{}.IndoorsOnly".format(nameStr)] = "{} can only be planted indoors.".format(data["SeedName"])
                cropObj.PlantableLocationRules.append(newRule)
        newCrops["Entries"][seedObj.Name] = cropObj.to_dict()
        filepath = jf.rsplit("/", 1)[0]
        giantpath = "{}/giant.png".format(filepath)
        if os.path.exists(giantpath):
            giantID = "{}_{}_Giant".format(modId, cropName)
            giantDict = {"FromItemID": cropObj.HarvestItemID,
                         "HarvestItems": [{"Chance": 1.0,
                                           "ForShavingEnchantment": None,
                                           "ScaledMinStackWhenShaving": 2,
                                           "ScaledMaxStackWhenShaving": 2,
                                           "ItemId": cropObj.HarvestItemID,
                                           "MinStack": 15,
                                           "MaxStack": 21}],
                         "Texture": "Mods/{}/GiantCrops".format(modId),
                         "TexturePosition": {"X": x, "Y": y}}
            giantSprites[giantpath] = {"X": x, "Y": y}
            newGiants["Entries"][giantID] = giantDict
            if x < 288:
                x += 48
            else:
                x = 0
                y += 64
        # giant crops
        i += 1
        j += 1
    return [objectData, newCrops, cropSprites, objectSprites, i18n, cropTexture, giantTexture, newGiants, giantSprites]


def buildObjects(srcDir, modId, spritesheet, mode, i18n):
    newObjects = {"LogName": "Raffadax New Objects - {}".format(mode),
                  "Action": "EditData",
                  "Target": "Data/Objects",
                  "Entries": {}
                  }
    newGifts = {"LogName": "Raffadax Gift Taste Edit - {}".format(mode),
                "Action": "EditData",
                "Target": "Data/NPCGiftTastes",
                "TextOperations": []}
    conditionalGifts = {}
    raffGifts = {}
    objTexture = {"LogName": "Raffadax Object Textures - {}".format(mode),
                  "Action": "Load",
                  "Target": "Mods/{}/Objects/{}".format(modId, mode),
                  "FromFile": "assets/textures/{}.png".format(spritesheet)}
    i = 0
    jsonFiles = []
    spriteFiles = {}
    giftprefs = {}
    contextTags = []
    objDir = "{}Objects".format(srcDir)
    tasteKeys = {"Love": 1, "Like": 3, "Neutral": 9, "Dislike": 5, "Hate": 7}
    for entry in objectscan(objDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        try:
            objData = pyjson5.load(open(jf, encoding="utf-8"))
        except Exception:
            print(jf)
            quit()
        if objData["Name"] in ["Broccoli", "Raisins"]:
            continue
        newObj = SVObject()
        if objData["Name"] in NEWIDS:
            nameStr = NEWIDS[objData["Name"]]
        else:
            nameStr = unidecode(objData["Name"])
        nameStr = re.sub(NAMERE, "", nameStr)
        itemID = "{}_{}".format(modId, nameStr)
        if itemID not in EXISTINGIDS:
            EXISTINGIDS.append(itemID)
        else:
            print("{} from '{}' in {} already exists.".format(itemID, objData["Name"], mode))
        newObj.Name = itemID
        newObj.DisplayName = "{{{{i18n:{}.DisplayName}}}}".format(nameStr)
        i18n["en"]["{}.DisplayName".format(nameStr)] = objData["Name"]
        if "Category" in objData:
            if isinstance(objData["Category"], str):
                if objData["Category"].strip("-").isnumeric():
                    newObj.Category = int(objData["Category"])
                    if str(objData["Category"]) in CATINDICES:
                        newObj.Type = CATINDICES[str(objData["Category"])]
                    else:
                        print("No Cat found for {}".format(objData["Category"]))
                    if nameStr.endswith("Feather"):  # Feathers need to be Basic to have forage qualities.
                        newObj.Type = "Basic"
                else:
                    newObj.Type = objData["Category"]
                    if newObj.Type in CATEGORIES:
                        newObj.Category = CATEGORIES[newObj.Type]
                    else:
                        print("No Cat found for {}".format(newObj.Type))
                    if nameStr.endswith("Feather"):  # Feathers need to be Basic to have forage qualities.
                        newObj.Type = "Basic"
            else:
                newObj.Category = objData["Category"]
                newObj.Type = CATINDICES[str(objData["Category"])]
                if nameStr.endswith("Feather"):  # Feathers need to be Basic to have forage qualities.
                    newObj.Type = "Basic"
                # print("Non string cat for {}".format(newObj.Name))
        else:
            print("No Category data for {}".format(objData["Name"]))
            quit()
        if "Description" in objData:
            newObj.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
            i18n["en"]["{}.Description".format(nameStr)] = objData["Description"]
        if "Price" in objData:
            newObj.Price = objData["Price"]
        newObj.Texture = "Mods/{}/Objects/{}".format(modId, mode)
        newObj.SpriteIndex = i
        if "Edibility" in objData:
            newObj.Edibility = objData["Edibility"]
        if "EdibleIsDrink" in objData:
            newObj.IsDrink = objData["EdibleIsDrink"]
        if "EdibleBuffs" in objData and objData["EdibleBuffs"]:
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
            contextTags += objData["ContextTags"]
        newObj.ContextTags.append("raffadax_object")
        newObj.ContextTags.append("raffadax_{}_object".format(mode).lower())
        parsedID = "Raffadax.RCP_{}".format(nameStr)
        if parsedID in FORAGEITEMS:
            newObj.ContextTags.append("forage_item")
        if "Recipe" in objData and isinstance(objData["Recipe"], dict) and objData["Recipe"]:
            if objData["Category"] in ["Cooking", "-7"]:
                newObj.ContextTags.append("raffadax_cooked_object")
            else:
                newObj.ContextTags.append("raffadax_crafted_object")
        if "CategoryTextOverride" in objData:  # this may have to become a CustomField
            catName = re.sub(NAMERE, "", objData["CategoryTextOverride"])
            newObj.ContextTags.append("category_{}".format(catName.lower()))
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
        if "GiftTastes" in objData:
            for tk, tdata in objData["GiftTastes"].items():
                fieldIndex = tasteKeys[tk]
                for npc in tdata:
                    if npc not in VANILLANPCS and npc not in MODNPCS and npc not in RAFFNPCS:
                        print("Nonexistent NPC: {} in {}".format(npc, newObj.Name))
                        quit()
                    if npc not in giftprefs:
                        giftprefs[npc] = {}
                    if fieldIndex not in giftprefs[npc]:
                        giftprefs[npc][fieldIndex] = []
                    giftprefs[npc][fieldIndex].append(newObj.Name)
        newObjects["Entries"][newObj.Name] = newObj.to_dict()
        spritename = jf[0:-5] + ".png"
        spriteFiles[spritename] = newObj.SpriteIndex
        i += 1
    for npc, tierData in giftprefs.items():
        if npc in VANILLANPCS:
            for tier, itemList in tierData.items():
                prefDict = {"Operation": "Append",
                            "Target": ["Fields", npc, int(tier)],
                            "Value": " ".join(itemList),
                            "Delimiter": " "
                            }
                newGifts["TextOperations"].append(prefDict)
        elif npc in RAFFNPCS:
            raffGifts[npc] = {"LogName": "Raffadax Gift Taste Edit - {} - {}".format(npc, mode),
                              "Action": "EditData",
                              "Target": "Data/NPCGiftTastes",
                              "TextOperations": []}
            for tier, itemList in tierData.items():
                prefDict = {"Operation": "Append",
                            "Target": ["Fields", "{{{{{}}}}}".format(npc), int(tier)],
                            "Value": " ".join(itemList),
                            "Delimiter": " "
                            }
                raffGifts[npc]["TextOperations"].append(prefDict)
        else:
            if npc == "Marlon":
                outnpc = "MarlonFay"
            elif npc == "Morris":
                outnpc = "MorrisTod"
            elif npc == "Gunther":
                outnpc = "GuntherSilvian"
            else:
                outnpc = npc
            conditionalGifts[outnpc] = {"LogName": "Raffadax Gift Taste Edit - {} - {}".format(outnpc, mode),
                                        "Action": "EditData",
                                        "Target": "Data/NPCGiftTastes",
                                        "TextOperations": []}
            for tier, itemList in tierData.items():
                prefDict = {"Operation": "Append",
                            "Target": ["Fields", outnpc, int(tier)],
                            "Value": " ".join(itemList),
                            "Delimiter": " "
                            }
                conditionalGifts[outnpc]["TextOperations"].append(prefDict)
            modName = MODNPCS[npc]
            conditionalGifts[outnpc]["When"] = {"HasMod": modName}
    # pprint.pprint(conditionalGifts)
    # convert dict to list
    cGiftList = []
    for npc, prefData in conditionalGifts.items():
        cGiftList.append(prefData)
    contextTags = list(set(contextTags))
    return [newObjects, spriteFiles, newGifts, i18n, objTexture, cGiftList, contextTags, raffGifts]


def buildSprites(spriteList, dstDir, fileName, spriteType="objects"):
    if not os.path.exists(dstDir):
        os.mkdir(dstDir)
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
    elif spriteType == "fruittrees":
        imgWidth = 432
        imgHeight = 80 * len(spriteList)
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = 0
            y = 80 * sidx
            base.paste(img, (x, y))
    elif spriteType == "weapons":
        imgWidth = 128
        imgHeight = ceil(len(spriteList) / 8) * 16
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 8) * 16
            y = floor(sidx / 8) * 16
            base.paste(img, (x, y))
    elif spriteType == "bigobjects":
        imgHeight = ceil(len(spriteList) / 8) * 32
        imgWidth = 128
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, sidx in spriteList.items():
            img = Image.open(imgpath)
            x = (sidx % 8) * 16
            y = floor(sidx / 8) * 32
            base.paste(img, (x, y))
    elif spriteType == "giants":
        imgHeight = ceil(len(spriteList) / 5) * 64
        imgWidth = 5 * 48
        base = Image.new("RGBA", (imgWidth, imgHeight))
        for imgpath, coords in spriteList.items():
            img = Image.open(imgpath)
            x = coords["X"]
            y = coords["Y"]
            base.paste(img, (x, y))
    # base.show()
    outPath = "{}{}.png".format(dstDir, fileName)
    base.save(outPath)


def buildTrees(srcDir, modId, objectData, objectSprites, i18n, vanillaObjects, spritesheet):
    treeDir = "{}FruitTrees".format(srcDir)
    newTrees = {"LogName": "Raffadax New Trees",
                "Action": "EditData",
                "Target": "Data/fruitTrees",
                "Entries": {}}
    treeTexture = {"LogName": "Raffadax Tree Textures",
                   "Action": "Load",
                   "Target": "Mods/{}/Trees".format(modId),
                   "FromFile": "assets/textures/fruittrees.png"}
    jsonFiles = []
    treeSprites = {}
    i = len(objectSprites)
    j = 0
    for entry in objectscan(treeDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # sapling object
        saplingObj = SVObject()
        nameStr = unidecode(data["SaplingName"])
        nameStr = re.sub(NAMERE, "", nameStr)
        itemID = "{}_{}".format(modId, nameStr)
        if itemID not in EXISTINGIDS:
            EXISTINGIDS.append(itemID)
        else:
            print("{} from '{}' in Trees already exists.".format(itemID, data["Name"]))
        saplingObj.Name = itemID
        i18n["en"]["{}.Displayname".format(nameStr)] = data["SaplingName"]
        saplingObj.Displayname = "{{{{i18n:{}.Displayname}}}}".format(nameStr)
        # build the description.
        i18n["en"]["{}.Description".format(nameStr)] = data["SaplingDescription"]
        saplingObj.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        saplingObj.Type = "Seeds"
        saplingObj.Category = -74
        if "SaplingPurchasePrice" in data:
            saplingObj.Price = data["SaplingPurchasePrice"]
        saplingObj.Texture = "Mods/{}/Objects/FruitTrees".format(modId)
        saplingObj.SpriteIndex = i
        saplingObj.ContextTags.append("raffadax_sapling_object")
        saplingObj.ContextTags.append("raffadax_object")
        saplingObj.Edibility = -300
        spritename = jf.rsplit("/", 1)[0] + "/sapling.png"
        if "SaplingNameLocalization" in data:
            for langKey, langStr in data["NameLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Displayname".format(nameStr)] = langStr
        if "SaplingDescriptionLocalization" in data:
            for langKey, langStr in data["DescriptionLocalization"]:
                if langKey not in i18n:
                    i18n[langKey] = {}
                i18n[langKey]["{}.Description".format(nameStr)] = langStr
        objectSprites[spritename] = saplingObj.SpriteIndex
        objectData["Entries"][saplingObj.Name] = saplingObj.to_dict()

        # tree object
        newTree = FruitTree()
        newTree.DisplayName = "{{{{i18n:{}.TreeName}}}}".format(nameStr)
        i18n["en"]["{}.TreeName".format(nameStr)] = data["Name"]
        newTree.Seasons = [data["Season"]]
        fruitName = re.sub(NAMERE, "", data["Product"])
        if data["Product"] in vanillaObjects:
            fruit = {"ItemId": "(O){}".format(vanillaObjects[data["Product"]])}
        else:
            fruit = {"ItemId": "{}_{}".format(modId, fruitName)}
        newTree.Fruit.append(fruit)
        newTree.Texture = "Mods/{}/Trees".format(modId)
        newTree.TextureSpriteRow = j
        treespritename = jf.rsplit("/", 1)[0] + "/tree.png"
        treeSprites[treespritename] = newTree.TextureSpriteRow
        newTrees["Entries"][saplingObj.Name] = newTree.to_dict()
        i += 1
        j += 1

    return [objectData, newTrees, treeSprites, objectSprites, i18n, treeTexture]


def buildWeapons(srcDir, modId, spritesheet, i18n):
    weaponDir = "{}Weapons".format(srcDir)
    newWeapons = {"LogName": "Raffadax New Weapons",
                  "Action": "EditData",
                  "Target": "Data/Weapons",
                  "Entries": {}}
    weaponTexture = {"LogName": "Raffadax Weapon Textures",
                     "Action": "Load",
                     "Target": "Mods/{}/Weapons".format(modId),
                     "FromFile": "assets/textures/weaponobjects.png"}
    jsonFiles = []
    weaponSprites = {}
    weaponTypes = {"Sword": 0, "Dagger": 1, "Club": 2}
    i = 0
    for entry in objectscan(weaponDir):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        data = pyjson5.load(open(jf, encoding="utf-8"))
        # sapling object
        newMW = MeleeWeapon()
        nameStr = unidecode(data["Name"])
        nameStr = re.sub(NAMERE, "", nameStr)
        newMW.Name = "{}_{}".format(modId, nameStr)
        i18n["en"]["{}.Displayname".format(nameStr)] = data["Name"]
        newMW.DisplayName = "{{{{i18n:{}.Displayname}}}}".format(nameStr)
        i18n["en"]["{}.Description".format(nameStr)] = data["Description"]
        newMW.Description = "{{{{i18n:{}.Description}}}}".format(nameStr)
        newMW.Type = weaponTypes[data["Type"]]
        newMW.Texture = "Mods/{}/Weapons".format(modId)
        newMW.SpriteIndex = i
        if "MinimumDamage" in data:
            newMW.MinDamage = data["MinimumDamage"]
        if "MaximumDamage" in data:
            newMW.MaxDamage = data["MaximumDamage"]
        if "Knockback" in data:
            newMW.Knockback = float(data["Knockback"])
        if "Speed" in data:
            newMW.Speed = int(data["Speed"])
        if "Accuracy" in data:
            newMW.Precision = int(data["Accuracy"])
        if "Defense" in data:
            newMW.Defense = int(data["Defense"])
        if "ExtraSwingArea" in data:
            newMW.AreaOfEffect = int(data["ExtraSwingArea"])
        if "CritChance" in data:
            newMW.CritChance = float(data["CritChance"])
        if "CritMultiplier" in data:
            newMW.CritMultiplier = float(data["CritMultiplier"])
        if "MineDropVar" in data:
            newMW.MineBaseLevel = int(data["MineDropVar"])
        if "MineDropMinimumLevel" in data:
            newMW.MineMinLevel = int(data["MineDropMinimumLevel"])
        spritename = jf.rsplit("/", 1)[0] + "/weapon.png"
        weaponSprites[spritename] = newMW.SpriteIndex
        newWeapons["Entries"][newMW.Name] = newMW.to_dict()
        i += 1

    return [newWeapons, weaponSprites, i18n, weaponTexture]


def objectscan(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from objectscan(entry.path)
        elif entry.name.endswith((".json")):
            yield entry


def writeData(data: dict, dstDir: str, dstName: str):
    outPath = "{}data/{}.json".format(dstDir, dstName)
    # outData = json.dumps(jsonOut, indent=4)
    if not os.path.exists("{}data".format(dstDir)):
        os.mkdir("{}data".format(dstDir))
    with open(outPath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("{} data written to {}".format(dstName, outPath))


def writeGiftData(vanillaData: list, raffData: list, compatData: list, dstDir: str):
    jsonOut = {"Changes": vanillaData}
    outPath = "{}data/NPCGiftTastes/vanillagifts.json".format(dstDir)
    # outData = json.dumps(jsonOut, indent=4)
    if not os.path.exists("{}data/NPCGiftTastes".format(dstDir)):
        os.mkdir("{}data".format(dstDir))
    with open(outPath, 'w', encoding='utf-8') as f:
        json.dump(jsonOut, f, indent=4, ensure_ascii=False)
    print("Vanilla NPC Gift Pref data written to {}".format(outPath))
    for npc in RAFFNPCS:
        jsonOut = {"Changes": []}
        jsonOut['Changes'].append(raffData[0][npc])
        jsonOut['Changes'].append(raffData[1][npc])
        jsonOut['Changes'].append(raffData[2][npc])
        outPath = "{}data/NPCGiftTastes/{}gifts.json".format(dstDir, npc)
        # outData = json.dumps(jsonOut, indent=4)
        if not os.path.exists("{}data/NPCGiftTastes".format(dstDir)):
            os.mkdir("{}data".format(dstDir))
        with open(outPath, 'w', encoding='utf-8') as f:
            json.dump(jsonOut, f, indent=4, ensure_ascii=False)
        print("{} Gift Pref data written to {}".format(npc, outPath))
    jsonOut = {"Changes": []}
    for node in compatData:
        jsonOut["Changes"] += node
    outPath = "{}data/NPCGiftTastes/compatgifts.json".format(dstDir)
    # outData = json.dumps(jsonOut, indent=4)
    if not os.path.exists("{}data/NPCGiftTastes".format(dstDir)):
        os.mkdir("{}data".format(dstDir))
    with open(outPath, 'w', encoding='utf-8') as f:
        json.dump(jsonOut, f, indent=4, ensure_ascii=False)
    print("Mod Compat NPC Gift Pref data written to {}".format(outPath))


if __name__ == "__main__":
    # TODO: ExcludeWithMod
    # TODO: Add gift prefs hasmod conditions for non-Vanilla NPCs
    # TODO: Look into JA forge recipes, currently not implemented
    # QUESTION: Do we want parsers for the JA clothing items? Raffadax has none but other mods may have them.
    # get the path to the current file
    parser = argparse.ArgumentParser()
    parser.add_argument("--m", dest="convertMethod", type=str, help="Selects Method, options: artisan, crops, trees, weapons, aio")
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
    spriteDir = "{}assets/textures/".format(dstDir)
    i18n = {"en": {}}
    modId = "{{ModId}}"
    if args.sourceDirectory:
        srcDir = args.sourceDirectory
    if args.destDirectory:
        dstDir = args.destDirectory
    if args.convertMethod.lower() == "crops":
        srcDir = "{}[JA] Raffadax Crops/".format(oldFiles)
        # crop objects
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "cropobjects", "Crops", i18n)
        # seed objects and cropdata
        objectData, cropData, cropSprites, objectSprites, i18n, cropTexture = buildCrops(srcDir, modId, objectData, objectSprites, i18n, "cropobjects")
        # write data to file
        writeData([objTexture, cropTexture], [objectData, cropData, giftData], dstDir, "Crops", conditionalGifts)
        # # write i18n data
        writeLanguageData(i18n, dstDir, "Crops")
        # # make sprites
        buildSprites(objectSprites, spriteDir, "cropobjects", "objects")
        buildSprites(cropSprites, spriteDir, "crops", "crops")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "trees":
        srcDir = "{}[JA] Raffadax Trees/".format(oldFiles)
        # fruit objects
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "treeobjects", "FruitTrees", i18n)
        objectData, treeData, treeSprites, objectSprites, i18n, treeTexture = buildTrees(srcDir, modId, objectData, objectSprites, i18n, "treeobjects")
        # pprint.pprint(giftData)
        writeData([objTexture, treeTexture], [objectData, treeData, giftData], dstDir, "Trees", conditionalGifts)
        writeLanguageData(i18n, dstDir, "Trees")
        buildSprites(objectSprites, spriteDir, "treeobjects", "objects")
        buildSprites(treeSprites, spriteDir, "fruittrees", "fruittrees")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "weapons":
        srcDir = "{}[JA] Raffadax Weapons/".format(oldFiles)
        weaponData, weaponSprites, i18n, weaponTexture = buildWeapons(srcDir, modId, "weaponobjects", i18n)
        writeData([weaponTexture], [weaponData], dstDir, "Weapons")
        writeLanguageData(i18n, dstDir, "Weapons")
        buildSprites(weaponSprites, spriteDir, "weaponobjects", "weapons")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "artisan":
        srcDir = "{}Raffadax Artisan Assets/[JA] Raffadax Production/".format(oldFiles)
        objectData, objectSprites, giftData, i18n, objTexture, conditionalGifts = buildObjects(srcDir, modId, "artisanobjects", "Artisan")
        bigObjectData, bigObjectSprites, i18n, bigObjTexture = buildBigObjects(srcDir, modId, "artisanmachines", "Artisan", i18n)
        # recipes
        vanillaObjects = pyjson5.load(open("vanillaObjects.json"), encoding="utf-8")
        cookingData = buildCooking(srcDir, modId, vanillaObjects)
        craftingData = buildCrafting(srcDir, modId, vanillaObjects)
        writeData([objTexture, bigObjTexture], [objectData, bigObjectData, cookingData, craftingData], dstDir, "Artisan", conditionalGifts)
        writeLanguageData(i18n, dstDir, "Artisan")
        print("Building sprites...")
        buildSprites(objectSprites, spriteDir, "artisanobjects", "objects")
        buildSprites(bigObjectSprites, spriteDir, "artisanmachines", "bigobjects")
        print("Sprites saved to {}".format(spriteDir))
    if args.convertMethod.lower() == "aio":
        cropDir = "{}[JA] Raffadax Crops/".format(oldFiles)
        treeDir = "{}[JA] Raffadax Trees/".format(oldFiles)
        wepDir = "{}[JA] Raffadax Weapons/".format(oldFiles)
        artiDir = "{}Raffadax Artisan Assets/[JA] Raffadax Production/".format(oldFiles)
        dstDir = "{}/1.6 Files/[CP] Raffadax Test/assets/".format(rootDir)
        langDir = "{}/1.6 Files/[CP] Raffadax Test/".format(rootDir)
        spriteDir = "{}textures/".format(dstDir)
        i18n = {"en": {}}
        bigCraftablesOut = {"Changes": []}
        cookingOut = {"Changes": []}
        craftingOut = {"Changes": []}
        cropsOut = {"Changes": []}
        fruittreesOut = {"Changes": []}
        objectsOut = {"Changes": []}
        loadDataOut = {"Changes": []}
        weaponsOut = {"Changes": []}
        giantsOut = {"Changes": []}
        vanillaObjects = pyjson5.load(open("vanillaObjects.json"), encoding="utf-8")
        # Crops
        print("Generating Crop Data")
        objectData, objectSprites, cropgiftData, i18n, objTexture, cropconditionalGifts, objcontextTags, cropraffgifts = buildObjects(cropDir, modId, "cropobjects", "Crops", i18n)
        # seed objects and cropdata
        objectData, cropData, cropSprites, objectSprites, i18n, cropTexture, giantTexture, giantData, giantSprites = buildCrops(cropDir, modId, objectData, objectSprites, i18n, "cropobjects", vanillaObjects)
        objectsOut["Changes"].append(objectData)
        cropsOut["Changes"].append(cropData)
        giantsOut["Changes"].append(giantData)
        loadDataOut["Changes"].append(objTexture)
        loadDataOut["Changes"].append(cropTexture)
        loadDataOut["Changes"].append(giantTexture)
        # write data to file
        # writeData([objTexture, cropTexture], [objectData, cropData], dstDir, "crops")
        # # make sprites
        buildSprites(objectSprites, spriteDir, "cropobjects", "objects")
        buildSprites(cropSprites, spriteDir, "crops", "crops")
        buildSprites(giantSprites, spriteDir, "giantcrops", "giants")
        # Trees
        print("Generating Fruit Tree Data")
        objectData, objectSprites, treegiftData, i18n, objTexture, treeconditionalGifts, treecontextTags, treeraffgifts = buildObjects(treeDir, modId, "treeobjects", "FruitTrees", i18n)
        objectData, treeData, treeSprites, objectSprites, i18n, treeTexture = buildTrees(treeDir, modId, objectData, objectSprites, i18n, vanillaObjects, "treeobjects")
        objectsOut["Changes"].append(objectData)
        fruittreesOut["Changes"].append(treeData)
        loadDataOut["Changes"].append(objTexture)
        loadDataOut["Changes"].append(treeTexture)
        # writeData([objTexture, treeTexture], [objectData, treeData], dstDir, "trees")
        buildSprites(objectSprites, spriteDir, "treeobjects", "objects")
        buildSprites(treeSprites, spriteDir, "fruittrees", "fruittrees")
        # weapons
        print("Generating Weapon Data")
        weaponData, weaponSprites, i18n, weaponTexture = buildWeapons(wepDir, modId, "weaponobjects", i18n)
        weaponsOut["Changes"].append(weaponData)
        loadDataOut["Changes"].append(weaponTexture)
        # writeData([weaponTexture], [weaponData], dstDir, "weapons")
        buildSprites(weaponSprites, spriteDir, "weaponobjects", "weapons")
        # artisan
        print("Generating Artisan Data")
        objectData, objectSprites, artgiftData, i18n, objTexture, artconditionalGifts, artisancontextTags, artraffgifts = buildObjects(artiDir, modId, "artisanobjects", "Artisan", i18n)
        bigObjectData, bigObjectSprites, i18n, bigObjTexture = buildBigObjects(artiDir, modId, "artisanmachines", "Artisan", i18n)
        # recipes
        print("Generating Cooking Data")
        cookingData, i18n = buildCooking(artiDir, modId, vanillaObjects, i18n)
        print("Generating Crafting Data")
        craftingData, i18n = buildCrafting(artiDir, modId, vanillaObjects, i18n)
        objectsOut["Changes"].append(objectData)
        bigCraftablesOut["Changes"].append(bigObjectData)
        loadDataOut["Changes"].append(objTexture)
        loadDataOut["Changes"].append(bigObjTexture)
        cookingOut["Changes"].append(cookingData)
        craftingOut["Changes"].append(craftingData)
        # writeData([objTexture, bigObjTexture], [objectData, bigObjectData, cookingData, craftingData], dstDir, "artisan")
        buildSprites(objectSprites, spriteDir, "artisanobjects", "objects")
        buildSprites(bigObjectSprites, spriteDir, "artisanmachines", "bigobjects")
        # write Data
        writeData(bigCraftablesOut, dstDir, "BigCraftables")
        writeData(cookingOut, dstDir, "CookingRecipes")
        writeData(craftingOut, dstDir, "CraftingRecipes")
        writeData(cropsOut, dstDir, "Crops")
        writeData(fruittreesOut, dstDir, "FruitTrees")
        writeData(loadDataOut, dstDir, "LoadData")
        writeData(objectsOut, dstDir, "Objects")
        writeData(weaponsOut, dstDir, "Weapons")
        writeData(giantsOut, dstDir, "GiantCrops")
        # # write i18n data
        print("Generating i18n")
        npcLang = "{}/1.6 Files/npcdefault.json".format(rootDir)
        writeLanguageData(i18n, langDir, npcLang)
        print("Generating Gift Data")
        writeGiftData([cropgiftData, treegiftData, artgiftData], [cropraffgifts, treeraffgifts, artraffgifts], [cropconditionalGifts, treeconditionalGifts, artconditionalGifts], dstDir)
        contextTags = objcontextTags + treecontextTags + artisancontextTags
        contextTags = list(set(contextTags))
        contextTags.sort()
        pprint.pprint(contextTags)
