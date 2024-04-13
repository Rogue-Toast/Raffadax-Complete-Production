import os
import pprint

import pyjson5
from classes import Shop, Inventory

STFPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/NPCs/[STF] Raffadax Shops/shops.json"
OUTPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/shops.json"
PORTRAITPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/textures/shopportraits.json"
CATEGORIES = {"-5": "category_egg",
              "-9": "category_big_craftable",
              "-25": "category_ingredients",
              "-26": "category_artisan_goods",
              "-74": "category_seeds",
              "-75": "category_vegetable",
              "-79": "category_fruits",
              "-80": "category_flowers",
              "-81": "category_forage"}


def buildShops(fileIn: str, fileOut: str):
    newShops = {"Changes": []}
    iconList = []
    srcData = pyjson5.load(open(fileIn, encoding="utf-8"))
    for oldshop in srcData["Shops"]:
        newShop = Shop()
        shopID = "{{ModId}}_" + oldshop["ShopName"]
        # TODO: handle DefaultSellPriceMultiplier field from STF
        
    return [newShops, iconList]


if __name__ == "__main__":
    newShops, iconList = buildShops(STFPATH, OUTPATH)
