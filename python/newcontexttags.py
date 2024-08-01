"""Converts New Context Tags.csv to NewContextTags.json

Json is used by convertja.py
"""
import csv
import json
import pyjson5
import pprint

outDict = {}
ctDict = {}
with open("New Context Tags.csv", newline='\n') as csvfile:
    thisreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in thisreader:
        if row[0] == "ITEM NAME":
            continue
        # print(", ".join(row))
        outDict[row[0]] = {"Category": row[1],
                           "Type": row[2],
                           "Tags": []}
        for tag in row[3:]:
            if "," in tag:
                multiTags = tag.replace("\n", "").split(", ")
                # print(multiTags)
                outDict[row[0]]["Tags"] += multiTags
                for thisTag in multiTags:
                    if thisTag not in ctDict:
                        ctDict[thisTag] = [row[0]]
                    else:
                        ctDict[thisTag].append(row[0])
            elif tag:
                outDict[row[0]]["Tags"].append(tag)
                if tag not in ctDict:
                    ctDict[tag] = [row[0]]
                else:
                    ctDict[tag].append(row[0])

# with open("NewContextTags.json", 'w', encoding='utf-8') as f:
#     json.dump(outDict, f, indent=4, ensure_ascii=False)
i18n = pyjson5.load(open("H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.6 Files/[CP] Raffadax Test/i18n/default.json", encoding="utf-8"))
with open("TagsForMatrix.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    for k, v in ctDict.items():
        newrow = [k]
        for itemID in v:
            splitVal = itemID.split("_", 1)[1]
            i18nVal = splitVal + ".DisplayName"
            if i18nVal in i18n:
                itemName = i18n[i18nVal]
                newrow.append(itemName)
        writer.writerow(newrow)
