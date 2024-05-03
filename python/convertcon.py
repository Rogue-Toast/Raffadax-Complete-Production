import json
import math
import os
import pprint
import re

import pyjson5
from PIL import Image
from unidecode import unidecode
from classes import OreNode

OLDPATH = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[CON] Raffadax Gems/custom_ore_nodes.json"
SPRITEOUT = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[IE] Raffadax Gems/assets/orenodes.png"
JSONOUT = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[IE] Raffadax Gems/assets/orenodes.json"
vanillaObjects = pyjson5.load(open("vanillaObjects.json"))
NAMERE = r"[^a-zA-Z0-9_\.]"
SPRITEINDICES = {"BBambooChestOre.png": 0,
                 "ClayOre.png": 1,
                 "ClayOre1.png": 2,
                 "CoalOre1.png": 3,
                 "CoalOre2.png": 4,
                 "EbonyChestOre.png": 5,
                 "GarbageOre.png": 6,
                 "GarbageOre1.png": 7,
                 "HardwoodChestOre.png": 8,
                 "MagnetOre.png": 9,
                 "MagnetOre1.png": 10,
                 "MythrilOre.png": 11,
                 "MythrilOre1.png": 12,
                 "NahcoliteOre.png": 13,
                 "OnyxOre.png": 14,
                 "OnyxOre1.png": 15,
                 "Rock_Salt.png": 16,
                 "Rock_Salt1.png": 17,
                 "SandalwoodChestOre.png": 18,
                 "SapphireOre.png": 19,
                 "SapphireOre1.png": 20,
                 "SilverOre.png": 21,
                 "SilverOre1.png": 22,
                 "TreasureChestOre.png": 23}


def buildSprites(spriteDict):
    imgHeight = 4 * 16
    imgWidth = 6 * 16
    imgdir = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[CON] Raffadax Gems/"
    base = Image.new("RGBA", (imgWidth, imgHeight))
    for path, idx in spriteDict.items():
        img = Image.open("{}{}".format(imgdir, path))
        x = (idx % 6) * 16
        y = math.floor(idx / 6) * 16
        base.paste(img, (x, y))
    base.save(SPRITEOUT)


def convertCon(fileIn: str):
    srcData = pyjson5.load(open(fileIn, encoding="utf-8"))
    outData = {"Changes": []}
    textures = {"LogName": "Raffadax Ore Node Textures",
                "Action": "Load",
                "Target": "Mods/{{ModId}}/OreNodes",
                "FromFile": "assets/orenodes.png"
                }
    outData["Changes"].append(textures)
    change = {"LogName": "Raffadax Item Extensions - Ore Nodes",
              "Action": "EditData",
              "Target": "Mods/mistyspring.ItemExtensions/Resources",
              "Entries": {}}
    sprites = {}
    for node in srcData["nodes"]:
        nodeName = "Raffadax.Gems_"
        nodeName += node["spritePath"].rsplit("\\")[1].rsplit(".")[0]
        nodeName += "L" + str(node["oreLevelRanges"][0]["minLevel"])
        on = OreNode()
        thisSprite = node["spritePath"].split("\\")[1]
        on.SpriteIndex = SPRITEINDICES[thisSprite]
        on.Texture = "Mods/{{ModId}}/OreNodes"
        spritePath = node["spritePath"].replace("\\", "/")
        if spritePath not in sprites:
            sprites[spritePath] = on.SpriteIndex
        on.Health = node["durability"]
        on.Exp = round(node["exp"] * node["oreLevelRanges"][0]["expMult"])
        if "Chest" in node["spritePath"]:
            on.Sound = "axchop"
            on.BreakingSound = "barrelBreak"
            on.Tool = "Any"
            on.Debris = "wood"
        else:
            on.Sound = "hammer"
            on.BreakingSound = "stoneCrack"
            on.Tool = "Pickaxe"
            on.Debris = "stone"
        firstItem = node["dropItems"][0]
        itemName = unidecode(firstItem["itemIdOrName"])
        if itemName in vanillaObjects:
            newName = "(O){}".format(vanillaObjects[itemName])
        else:
            newName = "(O)Raffadax.RCP_{}".format(re.sub(NAMERE, "", itemName))
        on.ItemDropped = newName
        on.MinDrops = firstItem["minAmount"]
        on.MaxDrops = firstItem["maxAmount"]
        oreLevels = [0.03, 0.06, 0.09]
        gemLevels = [0.003, 0.006, 0.009]
        if any(x in nodeName for x in ["Onyx", "Sapphire", "Treasure"]):
            on.CountTowards = "OtherGems"
        for olr in node["oreLevelRanges"]:
            if olr["maxLevel"] > 249:
                maxLevel = "77376, 77378/-999"
            else:
                maxLevel = olr["maxLevel"]
            originalFreq = int((olr["spawnChanceMult"] * node["spawnChance"]) * 1000) / 1000
            print(originalFreq)
            scaledNames = ["Hardwood", "Bamboo", "Ebony", "Sandalwood", "Salt", "Magnet", "Mythril"]
            constantNames = ["Nahcolite", "Coal", "Garbage", "Clay"]
            if originalFreq < 0.003:
                sf = 0.003
            elif any(x in nodeName for x in scaledNames):
                if originalFreq < 0.3:
                    sf = oreLevels[0]
                elif originalFreq < 0.9:
                    sf = oreLevels[1]
                else:
                    sf = oreLevels[2]
                # per discussion with Raff
                if "Magnet" in nodeName:
                    sf = sf * 2
                if "Mythril" in nodeName:
                    sf = sf * 3
            elif "Silver" in nodeName:
                sf = 0.12
            elif any(x in nodeName for x in constantNames):
                sf = oreLevels[1]
            elif olr["minLevel"] < 50:
                sf = gemLevels[0]
            elif olr["minLevel"] < 75:
                sf = gemLevels[1]
            else:
                sf = gemLevels[2]
            if olr["minLevel"] == 50:
                minLevel = 40
            elif olr["minLevel"] == 75:
                minLevel = 80
            else:
                minLevel = olr["minLevel"]
            spawn = {"Floors": "{}/{}".format(minLevel, maxLevel),
                     "SpawnFrequency": sf,
                     "Type": "All"}
            on.MineSpawns.append(spawn)
        if len(node["dropItems"]) > 1:
            for di in node["dropItems"][1:]:
                thisItem = unidecode(di["itemIdOrName"])
                if thisItem in vanillaObjects:
                    thisItem = "(O){}".format(vanillaObjects[thisItem])
                else:
                    thisItem = "(O)Raffadax.RCP_{}".format(re.sub(NAMERE, "", thisItem))
                ei = {"ItemId": thisItem,
                      "MinItems": di["minAmount"],
                      "MaxItems": di["maxAmount"],
                      "Chance": di["dropChance"] / 100}
                on.ExtraItems.append(ei)
        change["Entries"][nodeName] = on.to_dict()
    outData["Changes"].append(change)
    return [outData, sprites]


if __name__ == "__main__":
    newJson, sprites = convertCon(OLDPATH)
    buildSprites(sprites)
    print("Sprites saved to {}".format(SPRITEOUT))
    jsonData = json.dumps(newJson, indent=4)
    with open(JSONOUT, 'w') as f:
        f.write(jsonData)
    print("JSON saved to {}".format(JSONOUT))
