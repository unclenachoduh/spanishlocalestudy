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
| Microsoft translation glossaries    |
| and write out data to JSON files.   |
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

top = '''PERMISSION NOTICE

The Microsoft “Terms of Use” (available at the www.microsoft.com website) govern all glossary terms in this document (“Glossary Terms”).  The following supplemental terms and conditions also apply.  If there is any conflict between the Terms of Use and the following terms and conditions, the following terms and conditions will take
Precedence over the Terms of Use.
         
1. No part of the Glossary Terms may be reproduced, adapted, distributed, or transmitted in any form or by any means, electronic, mechanical, or otherwise, including photocopying and entry into an information storage and/or retrieval system, for any purpose without the prior express consent of Microsoft Corporation. 

2. You may use the Glossary Terms in the development of any application software and you may also use the Glossary Terms for personal or non-commercial purposes only without the prior written consent of Microsoft Corporation, and only if all copies contain this Permission Notice and the Microsoft copyright notice in the Terms of Use.         
                                                                                                                                
3. You are not permitted to make any modifications, deletions or additions to the Glossary Terms.
 
4. Except as expressly set forth above, Microsoft’s publication of the Glossary Terms does not grant any rights to use, distribute, or implement any technology or intellectual property rights. All rights not expressly granted herein are expressly reserved by Microsoft.
"Source Term",,"Translation",,"String Category",,"Platform",,"Product",,"Version"
'''


def dictToJSON(det, directory):
    tojson = json.dumps(det, indent=2, sort_keys=True)
    output = open(directory + det["language"] + '.json', 'w')
    output.write(tojson)


def getDetails(pathname, language):


    # Dictionary of all translation units
    entries = {}

    segmentids = {}

    for file in os.listdir(pathname):
        textn = open(pathname+"/"+file)

        try:
            text = textn.read()
        except UnicodeDecodeError:
            continue

        text = text.replace(top, '')

        lines = text.split("\n")

        for line in lines:

            if line != "":
                parts = line.split(",,")

                newparts = []

                for part in parts:
                    newparts.append(part[1:-1])

                sourcestring = newparts[0]
                targetstring = newparts[1]
                
                source = "en-US" 
                entryid = file + "_" + sourcestring

                entries[entryid] = {source: sourcestring, language : targetstring} 

                if entryid not in segmentids:
                    segmentids[entryid] = 1
                else: 
                    segmentids[entryid] += 1 


    ids = segmentids.keys()

    duplicate_ids = []

    idscount = 0

    for item in entries:
        if segmentids[item] > 1:
            duplicate_ids.append(item)
            
        idscount += 1

    cleaned_entries = entries.keys()
        
    print(language, "SEGMENTS:", idscount, "|", "DUPLICATES:", len(duplicate_ids), "|", "Accepted Entries (Correct Format):", len(cleaned_entries))
    
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

        if source not in dictsource:
            dictsource[source] = [data[key][language]]
        elif source in dictsource:
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
            if x not in uniquedupes:
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
        if key in keepkeys:
            entries[key] = packet["data"][key]
            segcount += 1
        else:
            skippedCount +=1

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

        if countpresent ==2:
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

    print("JUNK COUNT:", junkCount)
    return junkIDs, junkCount






#######################
#### MAIN FUNCTION ####

## LOAD RESOURCES FROM TMX ##
##
#
# TMX File locations
esardir = 'es-ar_MS'
esdir = 'es-es_MS'
esmxdir = 'es-mx_MS'
esusdir = 'es-us_MS'

filenames = []


for name in os.listdir(esdir):
    if name in os.listdir(esmxdir):
        print(name)

espacket = getDetails(esdir, "es")
esjunkids, esjunkcount = findJunkStrings(espacket)

esmxpacket = getDetails(esmxdir, "es-MX")
esmxjunkids, esmxjunkcount = findJunkStrings(esmxpacket)

# Remove Junk Strings

junkids = {}

for key in esjunkids:
    junkids[key] = 1
for key in esmxjunkids:
    junkids[key] = 1

print("JUNK STRINGS:", len(junkids.keys()))

# Remove strings that are not translated by any language
print("REMOVE NONTRANSLATEABLE STRINGS")
esnotrans = getnontranslate(espacket)
esmxnotrans = getnontranslate(esmxpacket)

# Get list of nontranslated string ids
sharednontranslatedstrings, allnontranslatedstrings = getnontranslateids([esnotrans, esmxnotrans])

# Remove nontranslated strings from packets
espacket = removenontranslate(espacket, sharednontranslatedstrings)
esmxpacket = removenontranslate(esmxpacket, sharednontranslatedstrings)

# Remove all strings that are not translated in one or more locale variants
espacket = removenontranslate(espacket, allnontranslatedstrings)
esmxpacket = removenontranslate(esmxpacket, allnontranslatedstrings)

# Remove JUNK
print()
print("REMOVE JUNK")
espacket = removeByID(espacket, junkids)
esmxpacket = removeByID(esmxpacket, junkids)

# Get duplicate details: variants of duplicates (source), dict of IDs of duplicates (source)
esdupedata, esdupekeys, esonlydupes = getDuplicateSource(espacket)
esmxdupedata, esmxdupekeys, esmxonlydupes = getDuplicateSource(esmxpacket)

## Write duplicates to file
##
#
print("WRITE DUPLICATE SOURCE DICTIONARY TO FILE ON")

# print(esdupedata.keys())

outputDirectory = "MS_cleaned_json/"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

duplicate_data = esonlydupes

tojson = json.dumps(duplicate_data, indent=2, sort_keys=True)
output = open(outputDirectory + 'es_dupe.json', 'w')
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
esmxpacket = removeByID(esmxpacket, esmxdupekeys)

# Check number of segments per language
print()
print("SEGMENTS PER LANGUAGE")
print("es SEGMENTS:   ", espacket["segcount"])
print("es-MX SEGMENTS:", esmxpacket["segcount"])

# Find segment ids shared by all languages
sharedids = collectTheWholeSet([espacket, esmxpacket])

# Remove segments with identical source strings
print("REMOVE NON-SHARED SEGMENTS")
espacket = keepByID(espacket, sharedids)
esmxpacket = keepByID(esmxpacket, sharedids)
print()

# Check number of segments per language
print()
print("SEGMENTS PER LANGUAGE")
print("es SEGMENTS:   ", espacket["segcount"])
print("es-MX SEGMENTS:", esmxpacket["segcount"])


outputDirectory = "MS_cleaned_json/"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

# Dict to JSON file
dictToJSON(espacket, outputDirectory)
dictToJSON(esmxpacket, outputDirectory)
