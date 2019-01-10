import json

def encodeDict(dict):
  return json.dumps(dict)

def decodeDict(str):
  return json.loads(str)
