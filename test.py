import json

with open('data.json', 'r') as data:

    d = json.load(data)

final = {}

final['courses'] = d
final['metadata'] =  {
      "version": "0.0.1",
      "processed": True,
      "author": "Denali Schlesinger",
      "contact": "dsch28@bu.edu",
      "year": 2025
}

with open('final.json', 'w') as fj:

    json.dump(final, fj)