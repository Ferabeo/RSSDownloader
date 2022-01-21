import json


def readJsonFile(file):
    with open(file, 'r', encoding='utf-8') as json_file:
        return json.loads(json_file.read() or '{}')


def writeJsonFile(file, data):
    with open(file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
