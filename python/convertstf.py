import json
import math
import os
import pprint
import re

import pyjson5
from unidecode import unidecode
from classes import Shop, Inventory

STFPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[STF] Raffadax Shops/shops.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Shops.json"
PORTRAITPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/textures/shopportraits.json"
NEWIDS = pyjson5.load(open("newids.json", encoding="utf-8"))
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
vanillaBC = pyjson5.load(open("vanillaBigCraftables.json", encoding="utf-8"))
jarecipes = pyjson5.load(open("jarecipeshops.json", encoding="utf-8"))  # recipes with purchase data only in JsonAssets source
jaobjects = pyjson5.load(open("jaobjectshops.json", encoding="utf-8"))  # object with purchase data only in JA source
RAFFNPCS = ["Amanra", "Astrid", "Coyote", "Mephisto", "Puck", "Shuck", "Xolotl",
            "Valkyrie"]
GUSUNDERPRICED = ["Raffadax.RCP_Waldmeister", "Raffadax.RCP_AmberAle", "Raffadax.RCP_AppleSoda", "Raffadax.RCP_ArnoldPalmer", "Raffadax.RCP_BlueRaspberryLemonade", "Raffadax.RCP_BobaTea", "Raffadax.RCP_BongsutangTea", "Raffadax.RCP_Braggot", "Raffadax.RCP_ButterscotchBeer", "Raffadax.RCP_CafeCaramel", "Raffadax.RCP_Cauim", "Raffadax.RCP_CelticBreakfastTea", "Raffadax.RCP_ChaiTea", "Raffadax.RCP_ChandanTea", "Raffadax.RCP_CherryBlossomBeer", "Raffadax.RCP_CherryCola", "Raffadax.RCP_Chicha",
                  "Raffadax.RCP_Cider", "Raffadax.RCP_CranberryGingerAle", "Raffadax.RCP_CreamSoda", "Raffadax.RCP_DarkChocolateMocha", "Raffadax.RCP_DarkCocoa", "Raffadax.RCP_DarkRoastCoffee", "Raffadax.RCP_Dr.Pimento", "Raffadax.RCP_EarlGreyTea", "Raffadax.RCP_ElderflowerSoda", "Raffadax.RCP_ElderflowerTea", "Raffadax.RCP_FruitPunch", "Raffadax.RCP_GenmaichaTea", "Raffadax.RCP_GingerBeer", "Raffadax.RCP_GinkgoTea", "Raffadax.RCP_GrapeCrash", "Raffadax.RCP_GreenTeaLemonade",
                  "Raffadax.RCP_Gruit", "Raffadax.RCP_GyokuroTea", "Raffadax.RCP_HardIceTea", "Raffadax.RCP_HardLemonade", "Raffadax.RCP_HardPinkLemonade", "Raffadax.RCP_HibiscusTea", "Raffadax.RCP_HojichaTea", "Raffadax.RCP_HotButterscotch", "Raffadax.RCP_HotCocoa", "Raffadax.RCP_IceTea", "Raffadax.RCP_IPA", "Raffadax.RCP_Lager", "Raffadax.RCP_Lambic", "Raffadax.RCP_LemonUp", "Raffadax.RCP_Lemonade", "Raffadax.RCP_LightRoastCoffee", "Raffadax.RCP_Limeade", "Raffadax.RCP_LondonFog",
                  "Raffadax.RCP_LycheeSoda", "Raffadax.RCP_MatchaTea", "Raffadax.RCP_MediumRoastCoffee", "Raffadax.RCP_MelonSoda", "Raffadax.RCP_MintCocoa", "Raffadax.RCP_MintMocha", "Raffadax.RCP_Mocha", "Raffadax.RCP_MountainBlue", "Raffadax.RCP_Orangeade", "Raffadax.RCP_PearSoda", "Raffadax.RCP_PineappleCrash", "Raffadax.RCP_PinkLemonade", "Raffadax.RCP_Pixie", "Raffadax.RCP_PuerhTea", "Raffadax.RCP_PumpkinAle", "Raffadax.RCP_PumpkinSpiceCoffee", "Raffadax.RCP_RedAle",
                  "Raffadax.RCP_RoseTea", "Raffadax.RCP_RowanberrySour", "Raffadax.RCP_Sake", "Raffadax.RCP_SakuraSoda", "Raffadax.RCP_Sakurayu", "Raffadax.RCP_Schwarzbier", "Raffadax.RCP_SenchaGreenTea", "Raffadax.RCP_Shandy", "Raffadax.RCP_SparklingCider", "Raffadax.RCP_Spurt", "Raffadax.RCP_Stout", "Raffadax.RCP_StrawberryLemonade", "Raffadax.RCP_TamarindSoda", "Raffadax.RCP_VanillaCafe", "Raffadax.RCP_WhiteChocolateMocha", "Raffadax.RCP_WhiteCocoa", "Raffadax.RCP_WolfCola",
                  "Raffadax.RCP_WoodruffSoda", "Raffadax.RCP_YellowTea"]


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
        if SHOPTONPC[oldshop["ShopName"]] != "AnyOrNone":
            newShopName = SHOPTONPC[oldshop["ShopName"]]
        else:
            newShopName = oldshop["ShopName"]
        shopID = "{{ModId}}_" + newShopName + "_Shop"
        for ist in oldshop["ItemStocks"]:
            inv = Inventory()
            prefix = QPREFIXES[ist["ItemType"]]
            if ist["MaxNumItemsSoldInItemStock"] < len(ist["ItemNames"]):
                # random
                for inm in ist["ItemNames"]:
                    if inm in ["Broccoli", "Raisins"]:
                        continue
                    else:
                        if inm in ["Crab Pot", "Sprinkler", "Quality Sprinkler", "Iridium Sprinkler"]:
                            thisID = "(O){}".format(translateName(inm))
                        else:
                            thisID = "{}{}".format(prefix, translateName(inm))
                        inv.RandomItemId.append(thisID)
                if "StockPrice" in ist:
                    inv.Price = int(ist["StockPrice"])
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
                            hearts = math.floor(int(cp[2]) / 250)
                            outStr = "PLAYER_HEARTS Current {{{{{}}}}} {}".format(cp[1], hearts)
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
            else:
                if ist["ItemNames"] == ["Broccoli Seeds"]:
                    continue
                for inm in ist["ItemNames"]:
                    if inm in ["Crab Pot", "Sprinkler", "Quality Sprinkler", "Iridium Sprinkler"]:
                        inv.ItemId = "(O){}".format(translateName(inm))
                    else:
                        inv.ItemId = "{}{}".format(prefix, translateName(inm))
                    if "StockPrice" in ist:
                        inv.Price = int(ist["StockPrice"])
                        inv.IgnoreShopPriceModifiers = True
                    elif inm.endswith("Seeds") or inm.endswith("Starter") or inm.endswith("Sapling"):
                        inv.IgnoreShopPriceModifiers = True
                        inv.UseObjectDataPrice = True
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
                                hearts = math.floor(int(cp[2]) / 250)
                                outStr = "PLAYER_HEARTS Current {{{{{}}}}} {}".format(cp[1], hearts)
                            elif cp[0] == "y":
                                outStr = "YEAR {}".format(cp[1])
                            else:
                                continue
                            outConds.append(outStr)
                        inv.Condition = ", ".join(outConds)
                    if "StockItemCurrency" in ist:
                        inv.TradeItemId = "(O){}".format(translateName(ist["StockItemCurrency"]))
                        inv.TradeItemAmount = ist["StockCurrencyStack"]
                        inv.IgnoreShopPriceModifiers = True
                    newShop.Items.append(inv.to_dict())
        newShop.SalableItemTags = [CATEGORIES[str(x)] for x in oldshop["CategoriesToSellHere"]]
        timeParts = oldshop["When"][0].split(" ")
        ownerName = SHOPTONPC[oldshop["ShopName"]]
        # portrait = "assets/textures/Portraits/{}.png".format(newShopName)
        ownerDict = {"Name": "{{{{{}}}}}".format(ownerName) if ownerName != "AnyOrNone" else ownerName,
                     "Type": "AnyOrNone",
                     "Condition": "TIME {} {}".format(timeParts[1], timeParts[2]),
                     "Dialogues": [{"Id": "{}Dialogue_1".format(newShopName),
                                    "Dialogue": "{{{{i18n:{}.ShopDialogue}}}}".format(newShopName)}
                                   ]
                     }
        i18n["default"]["{}.ShopDialogue".format(newShopName)] = oldshop["Quote"]
        i18n["default"]["{}.ShopClosed".format(newShopName)] = oldshop["ClosedMessage"]
        newShop.Owners.append(ownerDict)
        closedDict = {"Name": None,
                      "ClosedMessage": "{{{{i18n:{}.ShopClosed}}}}".format(newShopName)}
        newShop.Owners.append(closedDict)
        pmDict = {"Id": "{}_SellPriceModifier".format(newShopName),
                  "Modification": "Multiply",
                  "Amount": 1.5}
        newShop.PriceModifiers.append(pmDict)
        newShop.StackSizeVisibility = "ShowIfMultiple"
        nsChangeNode["Entries"][shopID] = newShop.to_dict()
    # uncomment below to include the new shops
    newShops["Changes"].append(nsChangeNode)
    # vanilla shops
    """
    Price Multipliers
    JOja: 1.25 if player is not member
    SeedShop 2.0
    """
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
                    if inm in ["Broccoli", "Raisins"]:
                        continue
                    else:
                        thisID = "{}{}".format(prefix, translateName(inm))
                        inv.RandomItemId.append(thisID)
                if "StockPrice" in ist:
                    if newShopName == "SeedShop":
                        inv.Price = int(ist["StockPrice"] / 2)
                    elif newShopName == "Joja":
                        inv.Price = int(ist["StockPrice"] / 1.25)
                    else:
                        inv.Price = int(ist["StockPrice"])
                elif newShopName == "Joja":
                    inv.IgnoreShopPriceModifiers = True
                    inv.UseObjectDataPrice = True
                if "Stock" in ist:
                    inv.AvailableStock = ist["Stock"]
                # if newShopName == "Saloon":
                #     inv.AvailableStock = 1
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
                            outStr = "PLAYER_FRIENDSHIP_POINTS Current {{{{{}}}}} {}".format(cp[1], cp[2])
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
                changeNode["Entries"]["Raffadax.RCP_RandomNode_{}".format(i)] = inv.to_dict()
                i += 1
            else:
                for inm in ist["ItemNames"]:
                    if inm in ["Broccoli", "Raisins"]:
                        continue
                    inv.ItemId = "{}{}".format(prefix, translateName(inm))
                    if "StockPrice" in ist:
                        if newShopName == "SeedShop":
                            inv.Price = int(ist["StockPrice"] / 2)
                        elif newShopName == "Joja":
                            inv.Price = int(ist["StockPrice"] / 1.25)
                        else:
                            inv.Price = int(ist["StockPrice"])
                    elif newShopName == "Joja":
                        inv.IgnoreShopPriceModifiers = True
                        inv.UseObjectDataPrice = True
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
    # Recipes with shop data from JA
    changeNode = {"LogName": "Raffadax Vanilla Shop Edit - IceCreamStand Recipes",
                  "Action": "EditData",
                  "Target": "Data/Shops",
                  "TargetField": ["IceCreamStand", "Items"],
                  "Entries": {}
                  }
    for itemName, shopData in jarecipes.items():
        if shopData["Source"] == "Town":
            inv = Inventory()
            inv.ItemId = itemName
            inv.Price = int(shopData["Price"])
            inv.IsRecipe = True
            changeNode["Entries"][itemName] = inv.to_dict()
    newShops["Changes"].append(changeNode)
    changeNode = {"LogName": "Raffadax Vanilla Shop Edit - IceCreamStand objects",
                  "Action": "EditData",
                  "Target": "Data/Shops",
                  "TargetField": ["IceCreamStand", "Items"],
                  "Entries": {}
                  }
    for itemName, shopData in jaobjects.items():
        if shopData["Source"] == "Town":
            inv = Inventory()
            inv.ItemId = itemName
            inv.Price = int(shopData["Price"])
            changeNode["Entries"][itemName] = inv.to_dict()
    newShops["Changes"].append(changeNode)
    return [newShops, i18n]


def translateName(instr: str):
    if instr in vanillaObjects:
        return vanillaObjects[instr]
    elif instr in vanillaBC:
        return vanillaBC[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    elif instr in NEWIDS:
        return "Raffadax.RCP_{}".format(re.sub(NAMERE, "", NEWIDS[instr]))
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
