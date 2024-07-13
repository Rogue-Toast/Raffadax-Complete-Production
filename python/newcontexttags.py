"""Converts New Context Tags.csv to NewContextTags.json

Json is used by convertja.py
"""
import csv
import json

outDict = {}
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
            elif tag:
                outDict[row[0]]["Tags"].append(tag)

with open("NewContextTags.json", 'w', encoding='utf-8') as f:
    json.dump(outDict, f, indent=4, ensure_ascii=False)
