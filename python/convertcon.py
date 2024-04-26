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
        if "Onyx" in nodeName or "Sapphire" in nodeName:
            on.CountTowards = "OtherGems"
            maxChance = 0.003  # vanilla gem spawn rate
        else:
            maxChance = 0.029  # vanilla ore node spawn rate
        for olr in node["oreLevelRanges"]:
            if olr["maxLevel"] > 249:
                maxLevel = "-999"
            else:
                maxLevel = olr["maxLevel"]
            spawn = {"Floors": "{}/{}".format(olr["minLevel"], maxLevel),
                     "SpawnFrequency": min(maxChance, int((olr["spawnChanceMult"] * node["spawnChance"]) * 1000) / 1000),
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
