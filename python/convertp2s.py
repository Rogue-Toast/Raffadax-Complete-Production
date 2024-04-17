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

INFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/RFX Produce to Sapling - 4.1/ProducerRules.json"
OUTFILE = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/trees.json"
VANILLAOBJECTS = pyjson5.load(open("vanillaObjects.json"))
NAMERE = r"[^a-zA-Z0-9_\.]"
QUALITYSTRINGS = [{"Postfix": "Normal", "Quantity": 1, "Tag": "quality_none"},
                  {"Postfix": "Silver", "Quantity": 2, "Tag": "quality_silver"},
                  {"Postfix": "Gold", "Quantity": 3, "Tag": "quality_gold"},
                  {"Postfix": "Iridium", "Quantity": 4, "Tag": "quality_iridium"}]


def convertData(filepath: str):
    jsonData = pyjson5.load(open(filepath, encoding="utf-8"))
    outData = {"Changes": []}
    quantityNode = {"LogName": "Raffadax Produce to Sapling",
                    "Action": "EditData",
                    "Target": "Data/Machines",
                    "TargetField": ["(BC)25", "OutputRules"],
                    "Entries": {},
                    "MoveEntries": [],
                    "When": {"SeedMakerSaplings": "More Saplings"}}
    qualityNode = {"LogName": "Raffadax Produce to Sapling",
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
            # edit the object and add to qualityNode
            qtyRule = copy.deepcopy(quantityNode["Entries"][ruleId])
            outitem = {"ItemId": "(O){}".format(translateName(rule["OutputIdentifier"])),
                       "Id": translateName(rule["OutputIdentifier"]),
                       "CopyQuality": True}
            qtyRule["OutputItem"] = [outitem]
            qualityNode["Entries"][ruleId] = qtyRule
            qualityNode["MoveEntries"].append(me)
    outData["Changes"].append(quantityNode)
    outData["Changes"].append(qualityNode)
    return outData


def translateName(instr: str):
    if instr in VANILLAOBJECTS or isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    newRules = convertData(INFILE)
    tempOutFile = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/assets/data/saplingmachines.json"
    with open(tempOutFile, 'w', encoding='utf-8') as f:
        json.dump(newRules, f, indent=4, ensure_ascii=False)

    # Append to trees.json
    # existingTreeData = pyjson5.load(open(OUTFILE, encoding="utf-8"))
    # for changeNode in newRules["Changes"]:
    #     existingTreeData["Changes"].append(changeNode)
    # with open(OUTFILE, 'w', encoding='utf-8') as f:
    #     json.dump(newRules, f, indent=4, ensure_ascii=False)
