import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode

SHOPSRC = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[STF] Raffadax Shops/shops.json"
CROPDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[JA] Raffadax Crops/Objects"
TREEDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[JA] Raffadax Trees/Objects"
SAPLINGDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[JA] Raffadax Trees/FruitTrees"
SEEDDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[JA] Raffadax Crops/Crops"
ARTDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/Raffadax Artisan Assets/[JA] Raffadax Production/Objects"
BCDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/Raffadax Artisan Assets/[JA] Raffadax Production/BigCraftables"
vanillaObjects = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
vanillaBC = pyjson5.load(open("vanillaBigCraftables.json", encoding="utf-8"))
NAMERE = r"[^a-zA-Z0-9_\.]"


def getPrices():
    prices = {}
    jsonFiles = []
    # objects
    for entry in objectscan(CROPDIR):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for entry in objectscan(TREEDIR):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for entry in objectscan(ARTDIR):
        jsonFiles.append(entry.path.replace("\\", "/"))
    for jf in jsonFiles:
        objData = pyjson5.load(open(jf, encoding="utf-8"))
        objName = translateName(objData["Name"])
        prices[objName] = {}
        prices[objName]["JA"] = objData["Price"]
    # saplings
    saplingFiles = []
    for entry in objectscan(SAPLINGDIR):
        saplingFiles.append(entry.path.replace("\\", "/"))
    for jf in saplingFiles:
        objData = pyjson5.load(open(jf, encoding="utf-8"))
        objName = translateName(objData["SaplingName"])
        prices[objName] = {}
        prices[objName]["JA"] = objData["SaplingPurchasePrice"]
    # seeds
    seedFiles = []
    for entry in objectscan(SEEDDIR):
        seedFiles.append(entry.path.replace("\\", "/"))
    for jf in seedFiles:
        objData = pyjson5.load(open(jf, encoding="utf-8"))
        objName = translateName(objData["SeedName"])
        prices[objName] = {}
        prices[objName]["JA"] = objData["SeedPurchasePrice"]
    bcFiles = []
    for entry in objectscan(BCDIR):
        bcFiles.append(entry.path.replace("\\", "/"))
    for jf in bcFiles:
        objData = pyjson5.load(open(jf, encoding="utf-8"))
        objName = translateName(objData["Name"])
        prices[objName] = {}
        if "Price" in objData:
            prices[objName]["JA"] = objData["Price"]
        else:
            prices[objName]["JA"] = None
    return prices


def getShopPrices(prices):
    shopData = pyjson5.load(open(SHOPSRC, encoding="utf-8"))
    for shop in shopData["Shops"]:
        shopName = shop["ShopName"]
        stocks = shop["ItemStocks"]
        for istock in stocks:
            for iname in istock["ItemNames"]:
                item = translateName(iname)
                if item not in prices:
                    if not item.isnumeric():
                        print("{} from {} does not exist".format(item, shopName))
                    prices[item] = {"JA": None}
                if "IsRecipe" in istock and istock["IsRecipe"]:
                    prices[item][shopName] = {"Recipe": istock["StockPrice"]}
                else:
                    if "StockItemCurrency" in istock:
                        prices[item][shopName] = "{} {}".format(istock["StockCurrencyStack"], istock["StockItemCurrency"])
                    elif "StockPrice" in istock:
                        prices[item][shopName] = istock["StockPrice"]
                    else:
                        prices[item][shopName] = prices[item]["JA"]
    for shop in shopData["VanillaShops"]:
        shopName = shop["ShopName"]
        stocks = shop["ItemStocks"]
        for istock in stocks:
            for iname in istock["ItemNames"]:
                item = translateName(iname)
                if item not in prices:
                    if not item.isnumeric():
                        print("{} from {} does not exist".format(item, shopName))
                    prices[item] = {"JA": None}
                if "IsRecipe" in istock and istock["IsRecipe"]:
                    prices[item][shopName] = {"Recipe": istock["StockPrice"]}
                else:
                    if "StockItemCurrency" in istock:
                        prices[item][shopName] = "{} {}".format(istock["StockCurrencyStack"], istock["StockItemCurrency"])
                    elif "StockPrice" in istock:
                        prices[item][shopName] = istock["StockPrice"]
                    else:
                        prices[item][shopName] = prices[item]["JA"]
    return prices


def objectscan(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from objectscan(entry.path)
        elif entry.name.endswith((".json")):
            yield entry


def translateName(instr: str):
    if instr in vanillaObjects:
        return vanillaObjects[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    elif instr in vanillaBC:
        return "(BC){}".format(vanillaBC[instr])
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    prices = getPrices()
    # pprint.pprint(prices)
    # quit()
    prices = getShopPrices(prices)

    with open("pricereference.json", 'w', encoding='utf-8') as f:
        json.dump(prices, f, indent=4, ensure_ascii=False)

    for item, priceDict in prices.items():
        if "GusShop" in priceDict and isinstance(priceDict["GusShop"], int) and isinstance(priceDict["JA"], int) and priceDict["GusShop"] < priceDict["JA"]:
            print(item)
