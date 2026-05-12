import json
f = '/config/.config/obsidian/obsidian.json'
d = json.load(open(f))
d['vaults']['f13e8261f3d6f6bf']['open'] = False
json.dump(d, open(f, 'w'))
print("done:", d)
