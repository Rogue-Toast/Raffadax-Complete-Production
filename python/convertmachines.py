"""Converts Raffadax Produce to Sapling to Content Patcher equivalents.

Run after convertja.py. Amends trees.json.
"""
import copy
import json
import os
import pprint
import re

import pyjson5
from unidecode import unidecode
from classes import CPRule

P2SFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/RFX Produce to Sapling - 4.1/ProducerRules.json"
OUTFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/trees.json"
CASKFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[CCM] Raffadax Wine/CaskData.json"
CRYSFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[CCM] Raffadax Gems/ClonersData.json"
MILLFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/[MT] Raffadax Mill/content.json"
VANILLAOBJECTS = pyjson5.load(open("vanillaObjects.json"))
NAMERE = r"[^a-zA-Z0-9_\.]"
QUALITYSTRINGS = [{"Postfix": "Normal", "Quantity": 1, "Tag": "quality_none"},
                  {"Postfix": "Silver", "Quantity": 2, "Tag": "quality_silver"},
                  {"Postfix": "Gold", "Quantity": 3, "Tag": "quality_gold"},
                  {"Postfix": "Iridium", "Quantity": 4, "Tag": "quality_iridium"}]


def convertCasks(filepath: str):
    jsonData = pyjson5.load(open(filepath, encoding="utf-8"))
    changeNode = {"LogName": "Raffadax Cask Rules",
                  "Action": "EditData",
                  "Target": "Data/Machines",
                  "TargetField": ["(BC)163", "OutputRules"],
                  "Entries": {},
                  "MoveEntries": []}
    for item, multiplier in jsonData.items():
        cleanName = unidecode(item)
        cleanName = re.sub(NAMERE, "", cleanName)
        newRule = CPRule()
        ruleId = "Raffadax.RCP_Cask_{}".format(cleanName)
        newRule.Id = ruleId
        trigger = {"Id": "ItemPlacedInMachine",
                   "Trigger": "ItemPlacedInMachine",
                   "RequiredItemId": "(O){}".format(translateName(cleanName)),
                   "RequiredCount": 1}
        newRule.Triggers.append(trigger)
        outitem = {"CustomData": {"AgingMultiplier": str(multiplier)},
                   "OutputMethod": "StardewValley.Objects.Cask, Stardew Valley: OutputCask"
                   }
        newRule.OutputItem.append(outitem)
        changeNode["Entries"][ruleId] = newRule.to_dict()
        me = {"ID": ruleId, "BeforeID": "Cheese"}
        changeNode["MoveEntries"].append(me)
    return changeNode


def convertCrystalarium(filepath: str):
    jsonData = pyjson5.load(open(filepath, encoding="utf-8"))
    changeNode = {"LogName": "Raffadax Crystalarium Rules",
                  "Action": "EditData",
                  "Target": "Data/Machines",
                  "TargetField": ["(BC)21", "OutputRules"],
                  "Entries": {},
                  "MoveEntries": []}
    for rule in jsonData:
        clData = rule["CloningData"]
        itemName = rule["Name"]
        clTime = clData[itemName]
        cleanName = unidecode(itemName)
        cleanName = re.sub(NAMERE, "", cleanName)
        newRule = CPRule()
        ruleId = "Raffadax.RCP_Crystalarium_{}".format(cleanName)
        newRule.Id = ruleId
        octrigger = {"Id": "OutputCollected",
                     "Trigger": "OutputCollected",
                     "RequiredCount": 1}
        newRule.Triggers.append(octrigger)
        pltrigger = {"Id": "ItemPlacedInMachine",
                     "Trigger": "ItemPlacedInMachine",
                     "RequiredItemId": "(O){}".format(translateName(itemName)),
                     "RequiredCount": 1}
        newRule.Triggers.append(pltrigger)
        outitem = {"ItemId": "(O){}".format(translateName(itemName)),
                   "Id": translateName(itemName)}
        newRule.OutputItem.append(outitem)
        newRule.MinutesUntilReady = int(clTime)
        changeNode["Entries"][ruleId] = newRule.to_dict()
        me = {"ID": ruleId, "BeforeID": "Default"}
        changeNode["MoveEntries"].append(me)
    return changeNode


def convertMill(filepath: str):
    jsonData = pyjson5.load(open(filepath, encoding="utf-8"))
    changeNode = {"LogName": "Raffadax Mill Rules",
                  "Action": "EditData",
                  "Target": "Data/Buildings",
                  "TargetField": ["Mill", "ItemConversions"],
                  "Entries": {},
                  "MoveEntries": []}
    for cv in jsonData:
        input = cv["InputId"]
        output = cv["Output"]["Id"]
        qty = cv["Output"]["Amount"]
        if isinstance(input, int) or input.isnumeric():
            input = str(input)
            tag = "id_o_{}".format(input)
        elif input.startswith("spacechase0"):
            input = input.rsplit(":", 1)[1]
            tag = "id_o_{}".format(translateName(input).lower())
        if output.startswith("spacechase0"):
            output = output.rsplit(":", 1)[1]
        ruleId = "Raffadax_Mill_{}".format(re.sub(NAMERE, "", unidecode(input)))
        outConv = {"Id": ruleId,
                   "RequiredTags": [tag],
                   "RequiredCount": 1,
                   "MaxDailyConversions": -1,
                   "SourceChest": "Input",
                   "DestinationChest": "Output",
                   "ProducedItems": [{"Id": "(O){}".format(translateName(output)),
                                      "ItemId": "(O){}".format(translateName(output)),
                                      "MinStack": qty
                                      }
                                     ]
                   }
        changeNode["Entries"][ruleId] = outConv
        me = {"ID": ruleId, "BeforeID": "Default_UnmilledRice"}
        changeNode["MoveEntries"].append(me)
    return changeNode


def convertSaplings(filepath: str):
    jsonData = pyjson5.load(open(filepath, encoding="utf-8"))
    outData = {"Changes": []}
    quantityNode = {"LogName": "Raffadax Produce to Sapling quantity mode",
                    "Action": "EditData",
                    "Target": "Data/Machines",
                    "TargetField": ["(BC)25", "OutputRules"],
                    "Entries": {},
                    "MoveEntries": [],
                    "When": {"SeedMakerSaplings": "More Saplings"}}
    qualityNode = {"LogName": "Raffadax Produce to Sapling quality mode",
                   "Action": "EditData",
                   "Target": "Data/Machines",
                   "TargetField": ["(BC)25", "OutputRules"],
                   "Entries": {},
                   "MoveEntries": [],
                   "When": {"SeedMakerSaplings": "Better Saplings"}}
    for rule in jsonData:
        # direct version
        cleanName = unidecode(rule["OutputIdentifier"])
        cleanName = re.sub(NAMERE, "", cleanName)
        cleanOutput = unidecode(rule["InputIdentifier"])
        cleanOutput = re.sub(NAMERE, "", cleanOutput)
        for ruleData in QUALITYSTRINGS:
            # separate rules for each quality
            newRule = CPRule()
            ruleId = "Raffadax.RCP_SeedMaker_{}_{}".format(cleanName, ruleData["Postfix"])
            newRule.Id = ruleId
            trigger = {"Id": "{}_{}".format(cleanOutput, ruleData["Postfix"]),
                       "Trigger": "ItemPlacedInMachine",
                       "RequiredItemId": "(O){}".format(translateName(rule["InputIdentifier"])),
                       "RequiredTags": [ruleData["Tag"]],
                       "RequiredCount": 1}
            newRule.Triggers.append(trigger)
            outitem = {"ItemId": "(O){}".format(translateName(rule["OutputIdentifier"])),
                       "Id": translateName(rule["OutputIdentifier"]),
                       "MinStack": ruleData["Quantity"],
                       "MaxStack": ruleData["Quantity"]}
            newRule.OutputItem.append(outitem)
            quantityNode["Entries"][ruleId] = newRule.to_dict()
            me = {"ID": ruleId, "BeforeID": "Default"}
            quantityNode["MoveEntries"].append(me)
        # Quality output only requires one rule
        qtyRule = CPRule()
        qtyruleId = "Raffadax.RCP_SeedMaker_{}".format(cleanName)
        qtyRule.Id = qtyruleId
        trigger = {"Id": "{}_{}".format(cleanOutput, ruleData["Postfix"]),
                   "Trigger": "ItemPlacedInMachine",
                   "RequiredItemId": "(O){}".format(translateName(rule["InputIdentifier"])),
                   "RequiredCount": 1}
        qtyRule.Triggers.append(trigger)
        outitem = {"ItemId": "(O){}".format(translateName(rule["OutputIdentifier"])),
                   "Id": translateName(rule["OutputIdentifier"]),
                   "CopyQuality": True}
        qtyRule.OutputItem.append(outitem)
        qualityNode["Entries"][qtyruleId] = qtyRule.to_dict()
        me = {"ID": qtyruleId, "BeforeID": "Default"}
        qualityNode["MoveEntries"].append(me)
    outData["Changes"].append(quantityNode)
    outData["Changes"].append(qualityNode)
    return outData


def translateName(instr: str):
    if instr in VANILLAOBJECTS:
        return VANILLAOBJECTS[instr]
    elif isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    saplingRules = convertSaplings(P2SFILE)

    caskRules = convertCasks(CASKFILE)
    saplingRules["Changes"].append(caskRules)

    crysRules = convertCrystalarium(CRYSFILE)
    saplingRules["Changes"].append(crysRules)

    millRules = convertMill(MILLFILE)
    saplingRules["Changes"].append(millRules)

    tempOutFile = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/machines.json"
    with open(tempOutFile, 'w', encoding='utf-8') as f:
        json.dump(saplingRules, f, indent=4, ensure_ascii=False)

    # Append to trees.json
    # existingTreeData = pyjson5.load(open(OUTFILE, encoding="utf-8"))
    # for changeNode in newRules["Changes"]:
    #     existingTreeData["Changes"].append(changeNode)
    # with open(OUTFILE, 'w', encoding='utf-8') as f:
    #     json.dump(newRules, f, indent=4, ensure_ascii=False)