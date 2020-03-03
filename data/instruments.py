from os import listdir
from os.path import isfile, join
from collections import Counter

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

mono = Counter()
poly = Counter()
drums = Counter()

for fname in onlyfiles:
	with open(fname, 'r') as f:
		lst = json.load(f)
		mono += Counter(lst['mono'])
		poly += Counter(lst['poly'])
		drums += Counter(lst['drums'])

print(mono)
print(poly)
print(drums)

with open("./out/mono.json", 'w') as f:
	json.dump(dict(mono), f)

with open("./out/poly.json", 'w') as f:
	json.dump(dict(poly), f)

with open("./out/drums.json", 'w') as f:
	json.dump(dict(drums), f)

