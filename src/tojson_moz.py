import json, sys, re, os

print(
'''
+---------------------------------------+
|       SPANISH LOCALE PROJECT          |
|                                       |
| Analyzing the linguistic variation    |
| in Mozilla TMX resources for variants |
| of Spanish localizations              |
|                                       |
| By Kekoa Riggin                       |
+---------------------------------------+
''')

print(
'''
+-------------------------------------+
| DATA COLLECTION AND CLEANING SCRIPT |
|                                     |
| Read translation segments from      |
| Mozilla TMX files and write out     |
| data to JSON files.                 |
|                                     |
| Removal of segements with identical |
| segment IDs, segements with         |
| identical source strings, and       |
| strings that can be easily          |
| identified as 'junk'                |
|                                     |
+-------------------------------------+
''')

print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')


def dictToJSON(det, directory):
	tojson = json.dumps(det, indent=2, sort_keys=True)
	output = open(directory + det["language"] + '.json', 'w')
	output.write(tojson)


def getDetails(fileref, language):

	filetext = open(fileref)

	# Processing status. off/ended : don't process, processing : tu
	status = "off"

	entrystatus = "new"

	line = filetext.readline().strip()

	segmentids = {}

	# Dictionary of all translation units
	entries = {}
	# temporary object with keys ID, LANG1, LANG2
	current = {}

	while line:

		line = line.strip() 
		line = re.sub("\n", "", line)

		if line  == "<body>":
			status = "processing"
	 
		if line == "</body>":
			status = "ended"        
			break 
		
		if status == "processing":

			# print(fileref, line)
			
			if line[0:10] == "<tu tuid=\"":
				parts = line.split("\"")
				if parts[1] not in segmentids:
					segmentids[parts[1]] = 1
				else:
					segmentids[parts[1]] = segmentids[parts[1]] + 1

				current["id"] = parts[1]

				entrystatus = 1

			elif entrystatus == 1:

				if "xml:lang" not in line or "><seg>" not in line or "</seg>" not in line:
					entrystatus = 4
				else:
					junk, cut = line.split("xml:lang=\"")

					lang, scraps = cut.split("\"><seg>")

					text, junk = scraps.split("</seg>")

					current[lang] = text

					entrystatus = 2

			elif entrystatus == 2:
				if "xml:lang" not in line or "><seg>" not in line or "</seg>" not in line:
					entrystatus = 4
				else:
					junk, cut = line.split("xml:lang=\"")

					lang, scraps = cut.split("\"><seg>")

					text, junk = scraps.split("</seg>")

					current[lang] = text

					entrystatus = 3

			elif entrystatus == 3:
				if line != "</tu>":
					print("ERROR")
				else:
					entries[current["id"]] = current

				current = {}

			elif entrystatus == 4:
				if line == "</tu>":
					entrystatus = "new"

		line = filetext.readline()
		
	ids = segmentids.keys()

	duplicate_ids = []

	idscount = 0

	for item in ids:
		if segmentids[item] > 1:
			print(item, segmentids[item])
			duplicate_ids.append(item)
			
		idscount += 1

	cleaned_entries = entries.keys()
		
	print(fileref, "SEGMENTS:", idscount, "|", "DUPLICATES:", len(duplicate_ids), "|", "Accepted Entries (Correct Format):", len(cleaned_entries))
	
	return {"language": language, "segcount": idscount, "dupes": duplicate_ids, "data": entries}
	
   
def getDuplicateSource(packet):

	data = packet["data"]

	language = packet["language"]

	keys = data.keys()

	dictsource = {}
	dupekeys = {}
	onlydupes = {}

	for key in keys:
		source = data[key]["en-US"]
		# print(source)

		if source not in dictsource:
			# print(key, source)
			dictsource[source] = [data[key][language]]
		elif source in dictsource:
			# print(key, source)
			temp = dictsource[source]
			temp.append(data[key][language])
			dictsource[source] = temp

			dupekeys[key] = 1

			onlydupes[source] = temp

	dupeswithvarsources = dupeChecker(dictsource, dupekeys, onlydupes)


	return dictsource, dupekeys, dupeswithvarsources


def dupeChecker(dupedata, dupekeys, onlydupes):
	dupeswithoutdupes = {}

	truedupesources = {}

	countrealdupes = 0
	for k in onlydupes.keys():
		uniquedupes = []
		for x in onlydupes[k]:

			uniquedupes.append(x)

		if len(uniquedupes) > 1:
			dupeswithoutdupes[k] = uniquedupes
			countrealdupes +=1

			truedupesources[k] = uniquedupes

	count = 0
	for k in dupeswithoutdupes.keys():
		count += 1

	print("DUPES:", len(dupekeys), "COUNT OF TRUE DUPES:", countrealdupes)

	return truedupesources


def removeByID(packet, removekeys):

	entries = {}
	segcount = 0

	skippedCount = 0


	for key in packet["data"]:
		if key not in removekeys:
			entries[key] = packet["data"][key]
			segcount += 1
		else:
			skippedCount +=1

	print(packet["language"], "REMOVED SEGMENTS:", skippedCount)

	return {"language": packet["language"], "segcount": segcount, "data": entries}


def keepByID(packet, keys):

	keepkeys = {}
	for key in keys:
		keepkeys[key] = 1

	entries = {}
	segcount = 0

	skippedCount = 0


	for key in packet["data"]:

		entries[key] = packet["data"][key]
		segcount += 1
		skippedCount = 0

	print(packet["language"], "REMOVED SEGMENTS:", skippedCount)

	return {"language": packet["language"], "segcount": segcount, "data": entries}


def collectTheWholeSet(packets):
	smallestpacket = {"segcount": sys.maxsize}
	for packet in packets:
		if packet["segcount"] < smallestpacket["segcount"]:
			smallestpacket = packet

	print()
	print("SMALLEST LANGUAGE:", smallestpacket["language"])
	print()

	AllSharedIDS = []

	for key in smallestpacket["data"].keys():
		countpresent = 0

		for packet in packets:
			if key in packet["data"]:
				countpresent += 1

		if countpresent ==5:
			AllSharedIDS.append(key)

	return AllSharedIDS


def getnontranslate(packet):

	nontranslatableids = []

	notranscount = 0
	for key in packet["data"].keys():
		if packet["data"][key]["en-US"] == packet["data"][key][packet["language"]]:
			notranscount += 1

			nontranslatableids.append(key)

	print(packet["language"], "NONTRANSLATE:", notranscount)

	return nontranslatableids

def getnontranslateids(notranslist):

	allnontransids = {}

	smallestcount = sys.maxsize
	smallest = []
	for nt in notranslist:
		if len(nt) < smallestcount:
			smallestcount = len(nt)
			smallest = nt

		for key in nt:
			allnontransids[key] = 1


	sharednontransids = []



	for key in smallest:

		nontranscount = 0
		for nt in notranslist:
			if key in nt:
				nontranscount +=1

		if nontranscount == 5:
			sharednontransids.append(key)

	print("NONTRANSLATEABLE AGREEMENT:", len(sharednontransids))

	return sharednontransids, allnontransids.keys()

def removenontranslate(packet, nontranslate):
	
	data = {}

	removedcount = 0

	for key in packet["data"].keys():
		if key not in nontranslate:
			data[key] = packet["data"][key]
		else:
			removedcount += 1

	print(len(packet["data"].keys()), "-", removedcount, "=", len(data.keys()))

	packet["data"] = data

	return packet


def findJunkStrings(packet):
	
	junkCount = 0

	junkIDs = []

	for key in packet['data'].keys():

		segment = packet['data'][key]["en-US"]

		alphacount = sum(char.isalpha() for char in segment)

		# alg for removing known garbage strings
		words = segment.split()

		curatedWords = []

		for word in words:

			wordAlphaCount = sum(char.isalpha() for char in word)

			if wordAlphaCount < len(word)/2:
				curatedWords.append("+"* len(word))
				i = 1
			elif len(word) - wordAlphaCount > 3:
				curatedWords.append("+"* len(word))
				i = 1
			elif re.match("\$\W*", word):
				curatedWords.append("+"* len(word))
				i = 1
			elif re.match("\-\W*", word):
				curatedWords.append("+"* len(word))
				i = 1
			else:
				curatedWords.append(word)

		curatedSegment = '+'.join(curatedWords)

		curatedAlphaCount = sum(char.isalpha() for char in curatedSegment)



		if alphacount < len(packet['data'][key]["en-US"])/2:
			junkCount += 1
			junkIDs.append(key)
		elif len(packet['data'][key]["en-US"]) < 2:
			junkCount += 1
			junkIDs.append(key)
		elif curatedAlphaCount < len(curatedSegment)/2:
			junkCount += 1
			junkIDs.append(key)

		# print(alphacount)

	print("JUNK COUNT:", junkCount)
	return junkIDs, junkCount




#######################
#### MAIN FUNCTION ####

## LOAD RESOURCES FROM TMX ##
##
#
# TMX File locations
es = "moz_tmx/mozilla_en-US_es.tmx"
esar = "moz_tmx/mozilla_en-US_es-AR.tmx"
escl = "moz_tmx/mozilla_en-US_es-CL.tmx"
eses = "moz_tmx/mozilla_en-US_es-ES.tmx"
esmx = "moz_tmx/mozilla_en-US_es-MX.tmx"

# Get basic details: count of TUs, duplicate TUs (ID), TUs **FROM TMX**
esdet = getDetails(es, "es")
esjunkids, esjunkcount = findJunkStrings(esdet)
#
esardet = getDetails(esar, "es-AR")
esarjunkids, esarjunkcount = findJunkStrings(esardet)
#
escldet = getDetails(escl, "es-CL")
escljunkids, escljunkcount = findJunkStrings(escldet)
#
esesdet = getDetails(eses, "es-ES")
esesjunkids, esesjunkcount = findJunkStrings(esesdet)
#
esmxdet = getDetails(esmx, "es-MX")
esmxjunkids, esmxjunkcount = findJunkStrings(esmxdet)
#
##
## LOAD RESOURCES FROM TMX ##

# Remove Junk Strings

junkids = {}

for key in esjunkids:
	junkids[key] = 1
for key in esarjunkids:
	junkids[key] = 1
for key in escljunkids:
	junkids[key] = 1
for key in esesjunkids:
	junkids[key] = 1
for key in esmxjunkids:
	junkids[key] = 1

print("JUNK STRINGS:", len(junkids.keys()))


# Remove strings that are not translated by any language
print("REMOVE NONTRANSLATEABLE STRINGS")
esnotrans = getnontranslate(esdet)
esarnotrans = getnontranslate(esardet)
esclnotrans = getnontranslate(escldet)
esesnotrans = getnontranslate(esesdet)
esmxnotrans = getnontranslate(esmxdet)

# Get list of nontranslated string ids
sharednontranslatedstrings, allnontranslatedstrings = getnontranslateids([esnotrans, esarnotrans, esclnotrans, esesnotrans, esmxnotrans])

# Remove nontranslated strings from packets
espacket = removenontranslate(esdet, sharednontranslatedstrings)
esarpacket = removenontranslate(esardet, sharednontranslatedstrings)
esclpacket = removenontranslate(escldet, sharednontranslatedstrings)
esespacket = removenontranslate(esesdet, sharednontranslatedstrings)
esmxpacket = removenontranslate(esmxdet, sharednontranslatedstrings)

# Remove all strings that are not translated in one or more locale variants
espacket = removenontranslate(espacket, allnontranslatedstrings)
esarpacket = removenontranslate(esarpacket, allnontranslatedstrings)
esclpacket = removenontranslate(esclpacket, allnontranslatedstrings)
esespacket = removenontranslate(esespacket, allnontranslatedstrings)
esmxpacket = removenontranslate(esmxpacket, allnontranslatedstrings)

# Remove JUNK
print()
print("REMOVE JUNK")
espacket = removeByID(espacket, junkids)
esarpacket = removeByID(esarpacket, junkids)
esclpacket = removeByID(esclpacket, junkids)
esespacket = removeByID(esespacket, junkids)
esmxpacket = removeByID(esmxpacket, junkids)

# Get duplicate details: variants of duplicates (source), dict of IDs of duplicates (source)
esdupedata, esdupekeys, esonlydupes = getDuplicateSource(espacket)
esardupedata, esardupekeys, esaronlydupes = getDuplicateSource(esarpacket)
escldupedata, escldupekeys, esclonlydupes = getDuplicateSource(esclpacket)
esesdupedata, esesdupekeys, esesonlydupes = getDuplicateSource(esespacket)
esmxdupedata, esmxdupekeys, esmxonlydupes = getDuplicateSource(esmxpacket)


# print(esmxonlydupes)
## Write duplicates to file
##
#
print("WRITE DUPLICATE SOURCE DICTIONARY TO FILE ON")

# print(esdupedata.keys())

outputDirectory = "cleaned_json/"
if not os.path.exists(outputDirectory):
	os.makedirs(outputDirectory)

duplicate_data = esesonlydupes

tojson = json.dumps(duplicate_data, indent=2, sort_keys=True)
output = open(outputDirectory + 'es_dupe.json', 'w')
output.write(tojson)

duplicate_data = esaronlydupes

tojson = json.dumps(duplicate_data, indent=2, sort_keys=True)
output = open(outputDirectory + 'es-AR_dupe.json', 'w')
output.write(tojson)

duplicate_data = esclonlydupes

tojson = json.dumps(duplicate_data, indent=2, sort_keys=True)
output = open(outputDirectory + 'es-CL_dupe.json', 'w')
output.write(tojson)

duplicate_data = esmxonlydupes

tojson = json.dumps(duplicate_data, indent=2, sort_keys=True)
output = open(outputDirectory + 'es-MX_dupe.json', 'w')
output.write(tojson)
#
##
## Write duplicates to file

# Remove segments with identical source strings
print()
print("REMOVE DUPLICATES")
espacket = removeByID(espacket, esdupekeys)
esarpacket = removeByID(esarpacket, esardupekeys)
esclpacket = removeByID(esclpacket, escldupekeys)
esespacket = removeByID(esespacket, esesdupekeys)
esmxpacket = removeByID(esmxpacket, esmxdupekeys)

# Check number of segments per language
print()
print("SEGMENTS PER LANGUAGE")
print("es SEGMENTS:   ", espacket["segcount"])
print("es-AR SEGMENTS:", esarpacket["segcount"])
print("es-CL SEGMENTS:", esclpacket["segcount"])
print("es-ES SEGMENTS:", esespacket["segcount"])
print("es-MX SEGMENTS:", esmxpacket["segcount"])

# Find segment ids shared by all languages
sharedids = collectTheWholeSet([espacket, esarpacket, esclpacket, esespacket, esmxpacket])

# Remove segments with identical source strings
print("REMOVE NON-SHARED SEGMENTS")
espacket = keepByID(espacket, sharedids)
esarpacket = keepByID(esarpacket, sharedids)
esclpacket = keepByID(esclpacket, sharedids)
esespacket = keepByID(esespacket, sharedids)
esmxpacket = keepByID(esmxpacket, sharedids)
print()

# Check number of segments per language
print()
print("SEGMENTS PER LANGUAGE")
print("es SEGMENTS:   ", espacket["segcount"])
print("es-AR SEGMENTS:", esarpacket["segcount"])
print("es-CL SEGMENTS:", esclpacket["segcount"])
print("es-ES SEGMENTS:", esespacket["segcount"])
print("es-MX SEGMENTS:", esmxpacket["segcount"])

# outputDirectory = "cleaned_json/"
outputDirectory = "cleaned_json/"
if not os.path.exists(outputDirectory):
	os.makedirs(outputDirectory)

# Dict to JSON file
dictToJSON(espacket, outputDirectory)
dictToJSON(esarpacket, outputDirectory)
dictToJSON(esclpacket, outputDirectory)
dictToJSON(esespacket, outputDirectory)
dictToJSON(esmxpacket, outputDirectory)
