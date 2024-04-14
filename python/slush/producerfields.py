import pyjson5
import os
import pprint

FILENAME = "H:/Stardew Raffadax Update/Raffadax-Complete-Production/1.5.6 Files/Raffadax Artisan Assets/[PFM] Raffadax Production/ProducersConfig.json"


# get unique fields
ruleData = pyjson5.load(open(FILENAME, encoding="utf-8"))
fields = {}
machines = {}
for rule in ruleData:
    for k, v in rule.items():
        if k not in fields:
            fields[k] = 1
        else:
            fields[k] += 1
    # if rule["ProducerName"] not in machines:
    #     machines[rule["ProducerName"]] = "No fuel"
    # if "FuelIdentifier" in rule and rule["FuelIdentifier"]:
    #     machines[rule["ProducerName"]] = "Fuel"
pprint.pprint(fields)
# pprint.pprint(machines)
