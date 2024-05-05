import copy
import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode
from writeLangData import writeLanguageData

SRCFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[MFM] Raffadax/mail.json"
SRCI18N = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[MFM] Raffadax/i18n/default.json"
OUTDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data"
SRCIMGDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/NPCs - deprecated/[MFM] Raffadax/"
OUTIMGDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/textures"
vanillaObjects = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
vanillaBC = pyjson5.load(open("vanillaBigCraftables.json", encoding="utf-8"))
NAMERE = r"[^a-zA-Z0-9_\.]"
TEXTCOLORS = {"-1": "red",
              "0": "black",
              "1": "cyan",
              "2": "red",
              "3": "blue",
              "4": "white",
              "5": "orange",
              "6": "green",
              "7": "cyan",
              "8": "gray"}
oldTrans = pyjson5.load(open(SRCI18N, encoding="utf-8"))


def convertMail():
    mailData = pyjson5.load(open(SRCFILE))
    newMail = {"Changes": []}
    newTriggers = {"Changes": []}
    newLoads = []
    # Mail
    mchangeNode = {"LogName": "Raffadax Mail",
                   "Action": "EditData",
                   "Target": "Data/Mail",
                   "Entries": {}
                   }
    # triggeractions
    tchangeNode = {"LogName": "Raffadax Mail Triggers",
                   "Action": "EditData",
                   "Target": "Data/TriggerActions",
                   "Entries": {}}
    # image loads
    lchangeNode = {"LogName": "Raffadax Mail Backgrounds",
                   "Action": "Load",
                   "Target": "Mods/{{ModId}}/MailBackgrounds/",
                   "FromFile": "assets/textures/Mail/"}
    i18n = {}
    for mi in mailData:
        # build the mail string
        mailID = "Raffadax.RCP_" + mi["Id"]
        textcolorstr = ""
        if "TextColor" in mi:
            textcolor = TEXTCOLORS[str(mi["TextColor"])]
            textcolorstr = " [textcolor {}]".format(textcolor)
        text = "{{{{i18n:{}.MailText}}}}".format(mi["Id"])
        i18n["{}.MailText".format(mi["Id"])] = oldTrans[mi["Text"]]
        title = "{{{{i18n:{}.MailTitle}}}}".format(mi["Id"])
        i18n["{}.MailTitle".format(mi["Id"])] = oldTrans[mi["Title"]]
        attStrs = []
        if "Attachments" in mi and mi["Attachments"]:
            for att in mi["Attachments"]:
                if att["Type"] == "Object":
                    attStr = "%item object {} {}%%".format(translateName(att["Name"]), int(att["Stack"]))
                    attStrs.append(attStr)
        if "Recipe" in mi:
            attStr = "%item craftingRecipe {} %%".format(translateName(mi["Recipe"]))
            attStrs.append(attStr)
        if "LetterBG" in mi and mi["LetterBG"]:
            bg = mi["LetterBG"]
            bgName = bg.split(".")[0]
            bgStr = "[letterbg Mods/Raffadax.RCP/MailBackgrounds/{} 0]".format(bgName)
            # background to loads
            newLoad = lchangeNode.copy()
            newLoad["Target"] += bgName
            newLoad["FromFile"] += bg
            newLoads.append(newLoad)
        else:
            bg = mi["WhichBG"]
            bgStr = "[letterbg {}]".format(bg)
        mailStr = "{} {}{} {}[#]{}".format(text, bgStr, textcolorstr, " ".join(attStrs), title)
        mchangeNode["Entries"][mailID] = mailStr
        # triggers
        if "FriendshipConditions" in mi:
            cStrings = []
            triggerID = "{{ModId}}" + mailID + "_trigger"
            tEntry = {"Id": triggerID,
                      "Trigger": "DayStarted",
                      "Condition": "",
                      "Actions": ["AddMail Current {}".format(mailID)]}
            for fc in mi["FriendshipConditions"]:
                if fc["NpcName"] in ["Amanra", "Astrid", "Coyote", "Mephisto", "Puck", "Shuck", "Xolotl"]:
                    npc = "{{{{{}}}}}".format(fc["NpcName"])
                else:
                    npc = fc["NpcName"]
                cs = "PLAYER_HEARTS Current {} {}".format(npc, fc["FriendshipLevel"])
                cStrings.append(cs)
            tEntry["Condition"] = ", ".join(cStrings)
            tchangeNode["Entries"][triggerID] = tEntry
    # copy i18n
    newMail["Changes"].append(mchangeNode)
    newTriggers["Changes"].append(tchangeNode)
    return [newMail, newLoads, newTriggers, i18n]


def translateName(instr: str):
    if instr in vanillaObjects:
        return vanillaObjects[instr]
    elif instr in vanillaBC:
        return vanillaBC[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


def buildMail():
    OUTDIR = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data"
    mailData, loadData, triggerData, i18n = convertMail()

    mailout = "{}/Mail.json".format(OUTDIR)
    with open(mailout, 'w', encoding='utf-8') as f:
        json.dump(mailData, f, indent=4, ensure_ascii=False)

    loadOut = "{}/LoadData.json".format(OUTDIR)
    existingLoadData = pyjson5.load(open(loadOut, encoding="utf-8"))
    for change in loadData:
        if change not in existingLoadData["Changes"]:
            existingLoadData["Changes"].append(change)
    with open(loadOut, 'w', encoding='utf-8') as f:
        json.dump(existingLoadData, f, indent=4, ensure_ascii=False)

    triggersOut = "{}/TriggerActions.json".format(OUTDIR)
    with open(triggersOut, 'w', encoding='utf-8') as f:
        json.dump(triggerData, f, indent=4, ensure_ascii=False)

    langOut = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/maildefault.json"
    with open(langOut, 'w', encoding="utf-8") as f:
        json.dump(i18n, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    mailData, loadData, triggerData, i18n = convertMail()

    mailout = "{}/Mail.json".format(OUTDIR)
    with open(mailout, 'w', encoding='utf-8') as f:
        json.dump(mailData, f, indent=4, ensure_ascii=False)

    loadOut = "{}/LoadData.json".format(OUTDIR)
    existingLoadData = pyjson5.load(open(loadOut, encoding="utf-8"))
    for change in loadData:
        if change not in existingLoadData["Changes"]:
            existingLoadData["Changes"].append(change)
    with open(loadOut, 'w', encoding='utf-8') as f:
        json.dump(existingLoadData, f, indent=4, ensure_ascii=False)

    triggersOut = "{}/TriggerActions.json".format(OUTDIR)
    with open(triggersOut, 'w', encoding='utf-8') as f:
        json.dump(triggerData, f, indent=4, ensure_ascii=False)

    langOut = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/maildefault.json"
    with open(langOut, 'w', encoding="utf-8") as f:
        json.dump(i18n, f, indent=4, ensure_ascii=False)
    MAINI18N = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/i18n/default.json"
    mainTrans = pyjson5.load(open(MAINI18N, encoding="utf-8"))

    npcLang = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/npcdefault.json"
    langDir = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/"
    writeLanguageData(mainTrans, langDir, npcLang)
