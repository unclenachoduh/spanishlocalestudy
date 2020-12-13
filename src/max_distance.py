# max_distance.py
# USAGE: python3 max_distance.py moz / python3 max_distance.py ms

import json, sys

from helper_functions import nltk_bleu_corpus

from nltk.tokenize import word_tokenize


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
|         EDIT DISTANCE SCRIPT         |
|                                      |
| Measure the distance between         |
| source string and translation string |
| with BLEU score.                      |
|                                      |
+--------------------------------------+
''')

	print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')

	location = ""
	langs = []

	if sys.argv[1] == "moz":
		location = "cleaned_json/"
		langs = ["es", "es-AR", "es-CL", "es-MX"]
	elif sys.argv[1] == "ms":
		# JSON FILE LOCATION
		location = "MS_cleaned_json/"
		langs = ["es","es-MX"]

	print()
	print("AVERAGE EDIT DISTANCE FROM SOURCE")
	for lang in langs:
		# Load JSON file as dictionary
		all_data = location + lang + ".json"
		temp_data = json.loads(open(all_data).read())

		data = temp_data["data"]

		allKeys = data.keys()

		print("IMPORT DATA")
		print("TOTAL SEGMENTS:", len(allKeys))

		candidate = []
		reference = []

		accepted = 0

		for key in allKeys:

			a = data[key][lang]
			b = data[key]["en-US"]

			### TOKENIZE AND LOWER
			a = ' '.join(word_tokenize(a)).lower()
			b = ' '.join(word_tokenize(b)).lower()

			candidate.append([a])
			reference.append(b)
			accepted += 1

		score = nltk_bleu_corpus(candidate, reference)

		short = lang
		space = ""
		if len(short) < 5:
			space += "   "

		print(space + short, "- en-US:", score)
