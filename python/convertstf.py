import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode
from classes import Shop, Inventory

STFPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs/[STF] Raffadax Shops/shops.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/shops.json"
PORTRAITPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/textures/shopportraits.json"
NAMERE = r"[^a-zA-Z0-9_\.]"
CATEGORIES = {"-5": "category_egg",
              "-9": "category_big_craftable",
              "-25": "category_ingredients",
              "-26": "category_artisan_goods",
              "-28": "category_monster_loot",
              "-74": "category_seeds",
              "-75": "category_vegetable",
              "-79": "category_fruits",
              "-80": "category_flowers",
              "-81": "category_forage"}
QPREFIXES = {"Object": "(O)",
             "Ring": "(O)",
             "BigCraftable": "(BC)",
             "Clothing": "(S)",
             "Hat": "(H)",
             "Boot": "(B)",
             "Furniture": "(F)",
             "Weapon": "(W)",
             "Wallpaper": "(WP)",
             "Floors": "(FL)",
             "Seed": "(O)"}
SHOPTONPC = {"Djinn": "Amanra",
             "Selkie": "Astrid",
             "Coyotl": "Coyote",
             "Azeban": "Mephisto",
             "Pookah": "Puck",
             "Barghest": "Shuck",
             "Nagual": "Xolotl",
             "Valkyrie": "AnyOrNone",
             "Humidor": "AnyOrNone",
             "SodaMachine": "AnyOrNone",
             "ClintShop": "Blacksmith",
             "DwarfShop": "Dwarf",
             "DesertTrader": "DesertTrade",
             "GusShop": "Saloon",
             "HarveyShop": "Hospital",
             "JojaShop": "Joja",
             "KrobusShop": "ShadowShop",
             "MarlonShop": "AdventureShop",
             "MarnieShop": "AnimalShop",
             "PierreShop": "SeedShop",
             "RobinShop": "Carpenter",
             "SandyShop": "Sandy",
             "TravellingMerchant": "Traveler",
             "WillyShop": "FishShop",
             }
vanillaObjects = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
RAFFNPCS = ["Amanra", "Astrid", "Coyote", "Mephisto", "Puck", "Shuck", "Xolotl"]


def buildShops(fileIn: str, fileOut: str):
    newShops = {"Changes": []}
    srcData = pyjson5.load(open(fileIn, encoding="utf-8"))
    i18n = {"default": {}}
    # new shops
    nsChangeNode = {"LogName": "Raffadax New Shops",
                    "Action": "EditData",
                    "Target": "Data/Shops",
                    "Entries": {}
                    }
    for oldshop in srcData["Shops"]:
        newShop = Shop()
        shopID = "{{ModId}}_" + oldshop["ShopName"]
        for ist in oldshop["ItemStocks"]:
            inv = Inventory()
            prefix = QPREFIXES[ist["ItemType"]]
            if ist["MaxNumItemsSoldInItemStock"] < len(ist["ItemNames"]):
                # random
                for inm in ist["ItemNames"]:
                    thisID = "{}{}".format(prefix, translateName(inm))
                    inv.RandomItemId.append(thisID)
                if "StockPrice" in ist:
                    inv.Price = ist["StockPrice"]
                if "Stock" in ist:
                    inv.AvailableStock = ist["Stock"]
                if "IsRecipe" in ist and ist["IsRecipe"]:
                    inv.IsRecipe = True
                inv.AvoidRepeat = True
                if "When" in ist and isinstance(ist["When"], list):
                    conditions = list(set(ist["When"][0].split("/")))
                    outConds = []
                    for c in conditions:
                        cp = c.split(" ")
                        if cp[0] == "f":
                            outStr = "PLAYER_FRIENDSHIP_POINTS Current {} {}".format(cp[1], cp[2])
                        elif cp[0] == "y":
                            outStr = "YEAR {}".format(cp[1])
                        else:
                            continue
                        outConds.append(outStr)
                    inv.Condition = ", ".join(outConds)
                if "StockItemCurrency" in ist:
                    inv.TradeItemId = "(O)Raffadax.RCP_{}".format(translateName(ist["StockItemCurrency"]))
                    inv.TradeItemAmount = ist["StockCurrencyStack"]
                newShop.Items.append(inv.to_dict())
            else:
                for inm in ist["ItemNames"]:
                    inv.ItemId = "{}{}".format(prefix, translateName(inm))
                    if "StockPrice" in ist:
                        inv.Price = ist["StockPrice"]
                    if "Stock" in ist:
                        inv.AvailableStock = ist["Stock"]
                    if "IsRecipe" in ist and ist["IsRecipe"]:
                        inv.IsRecipe = True
                    if "When" in ist and isinstance(ist["When"], list):
                        conditions = list(set(ist["When"][0].split("/")))
                        outConds = []
                        for c in conditions:
                            cp = c.split(" ")
                            if cp[0] == "f":
                                outStr = "PLAYER_FRIENDSHIP_POINTS Current {} {}".format(cp[1], cp[2])
                            elif cp[0] == "y":
                                outStr = "YEAR {}".format(cp[1])
                            else:
                                continue
                            outConds.append(outStr)
                        inv.Condition = ", ".join(outConds)
                    if "StockItemCurrency" in ist:
                        inv.TradeItemId = "(O){}".format(translateName(ist["StockItemCurrency"]))
                        inv.TradeItemAmount = ist["StockCurrencyStack"]
                    newShop.Items.append(inv.to_dict())
        newShop.SalableItemTags = [CATEGORIES[str(x)] for x in oldshop["CategoriesToSellHere"]]
        timeParts = oldshop["When"][0].split(" ")
        ownerName = SHOPTONPC[oldshop["ShopName"]]
        if ownerName in RAFFNPCS:
            portrait = "assets/textures/Portraits/{}.png".format(ownerName)
        else:
            portrait = "assets/textures/Shops/{}.png".format(oldshop["ShopName"])
        ownerDict = {"Name": ownerName,
                     "Portrait": portrait,
                     "Condition": "TIME {} {}".format(timeParts[1], timeParts[2]),
                     "ClosedMessage": "{{{{i18n:{}.ShopClosed}}}}".format(oldshop["ShopName"]),
                     "Dialogues": [{"Id": "{}dialogue_1".format(oldshop["ShopName"]),
                                    "Dialogue": "{{{{i18n:{}.ShopDialogue}}}}".format(oldshop["ShopName"])}
                                   ]
                     }
        i18n["default"]["{}.ShopDialogue".format(oldshop["ShopName"])] = oldshop["Quote"]
        i18n["default"]["{}.ShopClosed".format(oldshop["ShopName"])] = oldshop["ClosedMessage"]
        newShop.Owners.append(ownerDict)
        if "DefaultSellPriceMultiplier" in oldshop:
            pmDict = {"Id": "{}_SellPriceModifier".format(oldshop["ShopName"]),
                      "Modification": "Multiply",
                      "Amount": oldshop["DefaultSellPriceMultiplier"]}
            newShop.PriceModifiers.append(pmDict)
        newShop.StackSizeVisibility = "ShowIfMultiple"
        nsChangeNode["Entries"][shopID] = newShop.to_dict()
    # uncomment below to include the new shops
    newShops["Changes"].append(nsChangeNode)
    # vanilla shops
    for vshop in srcData["VanillaShops"]:
        newShopName = SHOPTONPC[vshop["ShopName"]]
        changeNode = {"LogName": "Raffadax Vanilla Shop Edit - {}".format(newShopName),
                      "Action": "EditData",
                      "Target": "Data/Shops",
                      "TargetField": [newShopName, "Items"],
                      "Entries": {}
                      }
        i = 0
        for ist in vshop["ItemStocks"]:
            inv = Inventory()
            prefix = QPREFIXES[ist["ItemType"]]
            if ist["MaxNumItemsSoldInItemStock"] < len(ist["ItemNames"]):
                # random
                for inm in ist["ItemNames"]:
                    thisID = "{}{}".format(prefix, translateName(inm))
                    inv.RandomItemId.append(thisID)
                if "StockPrice" in ist:
                    inv.Price = ist["StockPrice"]
                else:
                    inv.IgnoreShopPriceModifiers = True
                if "Stock" in ist:
                    inv.AvailableStock = ist["Stock"]
                if "IsRecipe" in ist and ist["IsRecipe"]:
                    inv.IsRecipe = True
                inv.AvoidRepeat = True
                if "When" in ist and isinstance(ist["When"], list):
                    # print(ist["When"])
                    conditions = list(set(ist["When"][0].split("/")))
                    outConds = []
                    for c in conditions:
                        cp = c.split(" ")
                        if cp[0] == "f":
                            outStr = "PLAYER_FRIENDSHIP_POINTS Current {} {}".format(cp[1], cp[2])
                        elif cp[0] == "y":
                            outStr = "YEAR {}".format(cp[1])
                        elif cp[0] == "d":
                            outStr = "DAY_OF_WEEK {}".format(cp[1])
                        else:
                            continue
                        outConds.append(outStr)
                    inv.Condition = ", ".join(outConds)
                if "StockItemCurrency" in ist:
                    inv.TradeItemId = "(O)Raffadax.RCP_{}".format(translateName(ist["StockItemCurrency"]))
                    inv.TradeItemAmount = ist["StockCurrencyStack"]
                changeNode["Entries"]["Raffadax.RCP_RandomNode_{}".format(i)] = inv.to_dict()
            else:
                for inm in ist["ItemNames"]:
                    inv.ItemId = "{}{}".format(prefix, translateName(inm))
                    if "StockPrice" in ist:
                        inv.Price = ist["StockPrice"]
                    else:
                        inv.IgnoreShopPriceModifiers = True
                    if "Stock" in ist:
                        inv.AvailableStock = ist["Stock"]
                    if "IsRecipe" in ist and ist["IsRecipe"]:
                        inv.IsRecipe = True
                    if "When" in ist and isinstance(ist["When"], list):
                        # print(ist["When"])
                        conditions = ist["When"][0].split("/")
                        outConds = []
                        for c in conditions:
                            cp = c.split(" ")
                            if cp[0] == "f":
                                outStr = "PLAYER_FRIENDSHIP_POINTS Current {} {}".format(cp[1], cp[2])
                            elif cp[0] == "y":
                                outStr = "YEAR {}".format(cp[1])
                            elif cp[0] == "d":
                                outStr = "DAY_OF_WEEK {}".format(cp[1])
                            else:
                                continue
                            outConds.append(outStr)
                        inv.Condition = ", ".join(outConds)
                    if "StockItemCurrency" in ist:
                        inv.TradeItemId = "(O){}".format(translateName(ist["StockItemCurrency"]))
                        inv.TradeItemAmount = ist["StockCurrencyStack"]
                    changeNode["Entries"][translateName(inm)] = inv.to_dict()
        newShops["Changes"].append(changeNode)
    return [newShops, i18n]


def translateName(instr: str):
    if instr in vanillaObjects:
        return vanillaObjects[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    newShops, i18n = buildShops(STFPATH, OUTPATH)
    # pprint.pprint(newShops)
    with open(OUTPATH, 'w', encoding='utf-8') as f:
        json.dump(newShops, f, indent=4, ensure_ascii=False)
    if i18n["default"]:
        LANGPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/npcdefault.json"
        langData = pyjson5.load(open(LANGPATH, encoding="utf-8"))
        for k, v in i18n["default"].items():
            langData[k] = v
        with open(LANGPATH, 'w', encoding='utf-8') as f:
            json.dump(langData, f, indent=4, ensure_ascii=False)
