import os
import pprint
import pyjson5

CROPFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Crops.json"
OBJFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Objects.json"
VANILLAFILE = "H:/Stardew Decompiled/1.6.0 Content (unpacked)/Data/Objects.json"

cropsraw = pyjson5.load(open(CROPFILE, encoding="utf-8"))
objsraw = pyjson5.load(open(OBJFILE, encoding="utf-8"))
vanillaobjs = pyjson5.load(open(VANILLAFILE, encoding="utf-8"))

cropEntries = cropsraw["Changes"][0]["Entries"]
objEntries = objsraw["Changes"][0]["Entries"]

for seedID, cropData in cropEntries.items():
    if cropData["RegrowDays"] < 0:
        seedPrice = objEntries[seedID]["Price"]
        harvestItem = cropData["HarvestItemID"]
        if harvestItem in objEntries:
            cropPrice = objEntries[harvestItem]["Price"]
        else:
            cropPrice = vanillaobjs[harvestItem]["Price"]
        if seedPrice >= cropPrice:
            print("{} price is greater or equal to {} price".format(seedID, harvestItem))
        elif seedPrice / cropPrice > 0.95:
            print("{} price is almost as much as {} price".format(seedID, harvestItem))
