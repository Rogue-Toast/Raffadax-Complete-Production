"""Amends Raffadax PFM data with new item IDs."""
import copy
import json
import os
import pprint
import re
from dataclasses import dataclass, field
from classes import Rule, PConfig

import pyjson5
from unidecode import unidecode

NAMERE = r"[^a-zA-Z0-9_\.]"
NEWIDS = pyjson5.load(open("newids.json", encoding="utf-8"))


def convertMachines(machineFile):
    newConfigs = []
    srcData = pyjson5.load(open(machineFile, encoding="utf-8"))
    for cfg in srcData:
        newCfg = PConfig()
        for k, v in cfg.items():
            if k == "ProducerName":
                newCfg.ProducerQualifiedItemId = "(BC)Raffadax.RCP_{}".format(re.sub(NAMERE, "", v))
            else:
                setattr(newCfg, k, v)
        newConfigs.append(newCfg.to_dict())
    return newConfigs


def convertRules(ruleFile, vo, vbc):
    newRules = []
    srcData = pyjson5.load(open(ruleFile, encoding="utf-8"))
    directImports = ["DelayedSounds", "FuelStack", "InputPriceBased",
                     "InputStack", "OutputPriceMultiplier", "OutputQuality",
                     "OutputStack", "PlacingAnimation",
                     "PlacingAnimationColorName"]
    for rule in srcData:
        newRule = Rule()
        if rule["ProducerName"] in vbc:
            newRule.ProducerQualifiedItemId = "(BC){}".format(vbc[rule["ProducerName"]])
        else:
            newRule.ProducerQualifiedItemId = "(BC){}".format(translateName(rule["ProducerName"], vo))
        if not rule["InputIdentifier"]:
            newRule.InputIdentifier = None
        else:
            newRule.InputIdentifier = translateName(rule["InputIdentifier"], vo)
        if "InputStack" in rule and rule["InputStack"] != 1:
            newRule.InputStack = int(rule["InputStack"])
        newRule.OutputIdentifier = translateName(rule["OutputIdentifier"], vo)
        if "Raffadax" in newRule.OutputIdentifier:
            strippedOI = unidecode(rule["OutputIdentifier"])
            newRule.OutputTranslationKey = "{}.DisplayName".format(re.sub(NAMERE, "", strippedOI))
        if "OutputStack" in rule and rule["OutputStack"] != 1:
            newRule.OutputStack = int(rule["OutputStack"])
        newRule.MinutesUntilReady = rule["MinutesUntilReady"]
        newRule.Sounds = rule["Sounds"]
        # optional fields
        if "AdditionalFuel" in rule:
            for oldItem, qty in rule["AdditionalFuel"].items():
                newItem = translateName(oldItem, vo)
                newRule.AdditionalFuel[newItem] = qty
        if "AdditionalOutputs" in rule:
            for ao in rule["AdditionalOutputs"]:
                newAO = ao.copy()
                newAO["OutputIdentifier"] = translateName(ao["OutputIdentifier"], vo)
                newRule.AdditionalOutputs.append(newAO)
        if "ExcludeIdentifiers" in rule:
            for i in rule["ExcludeIdentifiers"]:
                newRule.ExcludeIdentifiers.append(translateName(i, vo))
        if "FuelIdentifier" in rule:
            newRule.FuelIdentifier = translateName(rule["FuelIdentifier"], vo)
        if "FuelStack" in rule:
            newRule.FuelStack = int(rule["FuelStack"])
        if "keepInputQuality" in rule and rule["keepInputQuality"] and rule["ProducerName"] != "Seed Maker":  # Raff munges the case on this
            newRule.KeepInputQuality = True
        elif rule["ProducerName"] == "Seed Maker":
            newRule.KeepInputQuality = False
        for dk in directImports:
            if dk in rule:
                setattr(newRule, dk, rule[dk])
        newRules.append(newRule.to_dict())
        # duplicate furnace rules for Heavy Furnace
        if rule["ProducerName"] == "Furnace":
            hRule = copy.deepcopy(newRule)
            hRule.ProducerQualifiedItemId = "(BC)HeavyFurnace"
            hRule.InputStack = 5 * hRule.InputStack
            outMin = hRule.OutputStack * 5
            outMax = int(1.2 * outMin)
            hRule.OutputStack = outMin
            hRule.OutputMaxStack = outMax
            if "AdditionalFuel" in rule:
                for k, v in hRule.AdditionalFuel.items():
                    v = v * 5
            hRule.FuelStack = 3 * hRule.FuelStack
            newRules.append(hRule.to_dict())
    return newRules


def translateName(instr: str, vanillaObjects):
    if instr in vanillaObjects or isinstance(instr, int) or instr.isnumeric() or instr[1:].isnumeric():
        return instr
    elif instr in NEWIDS:
        newStr = NEWIDS[instr]
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out
    elif instr.endswith("_item"):  # context Tags
        return instr
    elif instr.endswith("-item"):  # misspelled context tags
        return instr.replace("-", "_")
    elif instr.startswith("-") and instr[1:].isnumeric():  # category
        return instr
    else:
        newStr = unidecode(instr)
        out = "Raffadax.RCP_{}".format(re.sub(NAMERE, "", newStr))
        return out


if __name__ == "__main__":
    ruleFile = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/Raffadax Artisan Assets/[PFM] Raffadax Production/ProducerRules.json"
    machineFile = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/Raffadax Artisan Assets/[PFM] Raffadax Production/ProducersConfig.json"
    vanillaObjects = pyjson5.load(open("vanillaObjects.json", encoding="utf-8"))
    vanillaBigObjects = pyjson5.load(open("vanillaBigCraftables.json", encoding="utf-8"))
    rulesOut = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[PFM] Raffadax Production/ProducerRules.json"
    cfgOut = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[PFM] Raffadax Production/ProducersConfig.json"

    newRules = convertRules(ruleFile, vanillaObjects, vanillaBigObjects)

    outJson = json.dumps(newRules, indent=4)
    with open(rulesOut, 'w') as f:
        f.write(outJson)

    newConfigs = convertMachines(machineFile)
    outCfgs = json.dumps(newConfigs, indent=4)
    with open(cfgOut, 'w') as f:
        f.write(outCfgs)
