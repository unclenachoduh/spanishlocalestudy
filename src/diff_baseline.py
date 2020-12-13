# diff_baseline.py
# USAGE: python3 diff_baseline.py moz / python3 diff_baseline.py ms

import json, sys

from helper_functions import nltk_bleu_corpus

from nltk.tokenize import word_tokenize

def isJunkString(segment):

	alphacount = sum(char.isalpha() for char in segment)

	if alphacount < 2:
		return True

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
		else:
			curatedWords.append(word)

	curatedSegment = '+'.join(curatedWords)

	curatedAlphaCount = sum(char.isalpha() for char in curatedSegment)



	if alphacount < len(segment)/2:
		return True
	elif curatedAlphaCount < len(curatedSegment)/2:
		return True

	return False


def sim(data, lang):

	candidate = []
	reference = []

	accepted = 0

	for x in data:

		if isJunkString(x) == False:

			translations = data[x]
			base = translations.pop()

			### TOKENIZE AND LOWER
			base = ' '.join(word_tokenize(base)).lower()

			reference.append(base)

			matchCount = 0

			candidates = []
			for y in translations:
				y = ' '.join(word_tokenize(y)).lower()
				candidates.append(y)

				if y == base:
					matchCount += 1

			if matchCount != len(candidates):
				candidates = list(filter((base).__ne__, candidates))



			candidate.append(candidates)

			accepted += 1

	print(len(candidate), len(reference))
	score = nltk_bleu_corpus(candidate, reference)

	print("LOCALE:", lang)
	print("BLEU:", score)
	print("SEG IDs:", accepted)


if __name__ == "__main__":

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
+--------------------------------------+
|    EDIT DISTANCE BASELINE SCRIPT     |
|                                      |
| Measure the distance between         |
| translation variations within the    |
| same locale variant, using segments  |
| that were removed as duplicates by   |
| source text.                         |
|                                      |
+--------------------------------------+
''')

	print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')

	if sys.argv[1] == "moz":
		print("LOAD DATA")
		# JSON FILE LOCATION
		es_data = "cleaned_json/es_dupe.json"
		esar_data = "cleaned_json/es-AR_dupe.json"
		escl_data = "cleaned_json/es-CL_dupe.json"
		esmx_data = "cleaned_json/es-MX_dupe.json"

		# Load JSON file as dictionary
		esdata = json.loads(open(es_data).read())
		esardata = json.loads(open(esar_data).read())
		escldata = json.loads(open(escl_data).read())
		esmxdata = json.loads(open(esmx_data).read())

		print("es", len(esdata))
		print("es-AR", len(esardata))
		print("es-CL", len(escldata))
		print("es-MX", len(esmxdata))

		print()
		sim(esdata, "es")
		sim(esardata, "es-AR")
		sim(escldata, "es-CL")
		sim(esmxdata, "es-MX")

	elif sys.argv[1] == "ms":

		print("LOAD DATA")
		# JSON FILE LOCATION
		es_data = "MS_cleaned_json/es_dupe.json"
		esmx_data = "MS_cleaned_json/es-MX_dupe.json"

		# Load JSON file as dictionary
		esdata = json.loads(open(es_data).read())
		esmxdata = json.loads(open(esmx_data).read())

		print("es", len(esdata))
		print("es-MX", len(esmxdata))

		print()
		sim(esdata, "es")
		sim(esmxdata, "es-MX")

