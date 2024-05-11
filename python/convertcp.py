import copy
import json
import pprint
import pyjson5
from unidecode import unidecode
from PIL import Image

OLDFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[CP] NPCs/content.json"
OBJFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/Objects.json"
LANGFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/i18n/default.json"
VANILLAOBJ = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
oldchanges = pyjson5.load(open(OLDFILE, encoding="utf-8"))
vids = {}
for k, v in VANILLAOBJ.items():
    vids[v] = k


def translateObjectEdits():
    keyTrans = {"2": "Edibility",
                "5": "Description"}
    i18n = {}
    changeList = []
    for change in oldchanges["Changes"]:
        if "Target" in change and change["Target"] == "Data/ObjectInformation":
            newchange = {"Action": "EditData",
                         "Target": "Data/Objects",
                         "Fields": {}}
            for objId, fieldData in change["Fields"].items():
                for fieldKey, fieldStr in fieldData.items():
                    if fieldKey == "2":
                        outStr = int(fieldStr)
                    else:
                        itemName = vids[objId].replace(" ", "")
                        outStr = "{{{{i18n:{}.Description}}}}".format(itemName)
                        i18n["{}.Description".format(itemName)] = fieldStr
                    newchange["Fields"][objId] = {keyTrans[fieldKey]: outStr}
            changeList.append(newchange)
    return(changeList, i18n)


def translateSpriteEdits():
    objectChanges = []
    newImages = {}
    oldSrc = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[CP] NPCs/"
    outFile = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/textures/vanillasprites.png"
    x = y = 0
    for change in oldchanges["Changes"]:
        if change["Action"] == "EditImage":
            newchange = copy.deepcopy(change)
            newImages[newchange["FromFile"]] = {"X": x, "Y": y}
            objectName = newchange["FromFile"].split("/")[1].rsplit("_", 1)[0].replace("_", " ").title()
            newchange["LogName"] = "Raffadax Vanilla Sprite - {}".format(objectName)
            newchange["FromFile"] = "assets/textures/vanillasprites.png"
            newchange["FromArea"]["X"] = x
            newchange["FromArea"]["Y"] = y
            objectChanges.append(newchange)
            if x == 64:
                x = 0
                y += 16
            else:
                x += 16
    imgHeight = y + 16
    imgWidth = 80
    base = Image.new("RGBA", (imgWidth, imgHeight))
    for imgpath, coords in newImages.items():
        img = Image.open("{}{}".format(oldSrc, imgpath))
        x = coords["X"]
        y = coords["Y"]
        base.paste(img, (x, y))
    base.save(outFile)
    return objectChanges


def buildCPData():
    objectChanges, langChanges = translateObjectEdits()
    imageChanges = translateSpriteEdits()
    langOut = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/cpdefault.json"
    with open(langOut, 'w', encoding="utf-8") as f:
        json.dump(langChanges, f, indent=4, ensure_ascii=False)
    return [objectChanges, imageChanges]


if __name__ == "__main__":
    buildCPData()
