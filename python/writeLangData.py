import os
import json
import pyjson5


def writeLanguageData(i18n, dstDir, npcLang):
    comments = {"AdzukiBeans.DisplayName": "\t//crops.json - Crops\n",
                "AdzukiBeanStarter.Displayname": "\n\t//Crops.json - Seeds and starters\n",
                "AcaiBerry.DisplayName": "\n\t//Trees.json - Tree Produce\n",
                "AcaiSapling.Displayname": "\n\t//Trees.json - Tree Saplings\n",
                "Airgetlam.Displayname": "\n\t//Weapons.json - Weapons\n",
                "6-Below.DisplayName": "\n\t//Artisan.json - Artisan goods\n",
                "AnpuScarecrow.DisplayName": "\n\t//Artisan.json - BigCraftables\n",
                "Amanra.DisplayName": "\n\t//NPCS - AMANRA\n",
                "Astrid.DisplayName": "\n\t//NPCS - ASTRID\n",
                "Coyote.DisplayName": "\n\t//NPCS - COYOTE\n",
                "Mephisto.DisplayName": "\n\t//NPCS - MEPHISTO\n",
                "Puck.DisplayName": "\n\t//NPCS - PUCK\n",
                "Shuck.DisplayName": "\n\t//NPCS - SHUCK\n",
                "Xolotl.DisplayName": "\n\t//NPCS - XOLOTL\n",
                "Amanra.ShopDialogue": "\n\t//Shops.json - Shops\n",
                "AdoboSeasoning.RecipeName": "\n\t//Artisan.json - Cooking Recipes\n",
                "BlanchingPowder.RecipeName": "\n\t//Artisan.json - Crafting Recipes\n",
                "Amanra.Introduction.MailText": "\n\t//Mail.json - Mail\n",
                }
    if not os.path.exists("{}i18n".format(dstDir)):
        os.mkdir("{}i18n".format(dstDir))
    # get the npc language file
    npcData = pyjson5.load(open(npcLang, encoding="utf-8"))
    for langKey, langData in i18n.items():
        if langKey == "en":
            outKey = "default"
        else:
            outKey = langKey
        outPath = "{}i18n/{}.json".format(dstDir, outKey)
        if outKey == "default":
            for k, v in npcData.items():
                langData[k] = v
        # outData = json.dumps(langData, indent=4)
        with open(outPath, 'w', encoding='utf-8') as f:
            json.dump(langData, f, indent=4, ensure_ascii=False)
        # interleave the comments
        with open(outPath, 'r+', encoding="utf-8") as fd:
            contents = fd.readlines()
            for index, line in enumerate(contents):
                for needle, newtext in comments.items():
                    if needle in line and newtext not in contents[index - 1]:
                        contents.insert(index, newtext)
                        break
            fd.seek(0)
            fd.writelines(contents)
    print("i18n data written to {}".format("{}i18n".format(dstDir)))
