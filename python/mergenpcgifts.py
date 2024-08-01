import pyjson5
import json
import pprint

npcNames = ["Amanra", "Astrid", "Coyote", "Mephisto", "Puck", "Shuck", "Xolotl"]


def getGiftBase(npcName):
    dirPath = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/Raffadax Complete Production alpha/[CP] Raffadax/assets/data/Characters/"
    filePath = dirPath + npcName + ".json"
    npcData = pyjson5.load(open(filePath, encoding="utf-8"))
    for change in npcData["Changes"]:
        if change["Target"] == "Data/NPCGiftTastes":
            giftBase = change
            break
    return giftBase


def appendJAData(npcName, giftBase):
    dirPath = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/Raffadax Complete Production alpha/[CP] Raffadax/assets/data/NPCGiftTastes/"
    filePath = dirPath + npcName + "gifts.json"
    npcData = pyjson5.load(open(filePath, encoding="utf-8"))
    baseVal = giftBase["Entries"]["{{" + npcName + "}}"]
    baseParts = baseVal.split("/")
    for change in npcData["Changes"]:
        for changeTO in change["TextOperations"]:
            targetSegment = changeTO["Target"][2]
            baseParts[targetSegment] += " " + changeTO["Value"]
    newBaseVal = "/".join(baseParts)
    giftBase["Entries"]["{{" + npcName + "}}"] = newBaseVal
    return giftBase


if __name__ == "__main__":
    for npc in npcNames:
        giftBase = getGiftBase(npc)
        jaData = appendJAData(npc, giftBase)
        outData = {"Changes": [jaData]}
        jsonData = json.dumps(outData, indent=4)
        dirPath = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/Raffadax Complete Production alpha/[CP] Raffadax/assets/data/NPCGiftTastes/"
        JSONOUT = dirPath + npc + "giftsnew.json"
        with open(JSONOUT, 'w') as f:
            f.write(jsonData)
        print("JSON saved to {}".format(JSONOUT))
