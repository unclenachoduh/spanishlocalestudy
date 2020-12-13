import json, sys

from nltk.tokenize import word_tokenize

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
|        PERECT MATCHES SCRIPT         |
|                                      |
| Find perfect matches (char-for-char) |
| matches between all locale variants  |
|                                      |
| Remove all perfect matches from data |
| set.                                 |
|                                      |
| Find all perfect matches between     |
| locale variants locale-to-locale.    |
|                                      |
+--------------------------------------+
''')

print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')

# JSON FILE LOCATION
location = ""
langs = []

if sys.argv[1] == "moz":
	langs = ["es", "es-AR", "es-CL", "es-MX"]
	location = "cleaned_json/"
elif sys.argv[1] == "ms":
	langs = ["es", "es-MX"]
	location = "MS_cleaned_json/"



for lang1 in langs:

	percents = []


	for lang2 in langs:


		if lang1 == lang2:
			continue


		# Load JSON file as dictionary
		data1_temp = json.loads(open(location + lang1 + ".json").read())
		data2_temp = json.loads(open(location + lang2 + ".json").read())

		data1 = data1_temp["data"]
		data2 = data2_temp["data"]

		keys = data1.keys()

		perfect_matches_count = 0
		total_shared_count = 0
		total_keys_count = 0
		for key in keys:

			if key in data2:

				string1 = data1[key][lang1]
				string2 = data2[key][lang2]

				### TOKENIZE AND LOWER
				string1 = ' '.join(word_tokenize(string1)).lower()
				string2 = ' '.join(word_tokenize(string2)).lower()

				if string1 == string2:

					perfect_matches_count += 1

				total_shared_count += 1

			total_keys_count += 1


		print()
		print(lang1, lang2)
		print("PERFECT MATCHES:", perfect_matches_count)
		print("SHARED:", total_shared_count)
		print("TOTAL:", total_keys_count)
		
		percent = perfect_matches_count / total_shared_count
		print("PERCENT:", percent)

		percents.append(percent)

	average = sum(percents) / len(percents)
	print()
	print(lang1, "AVERAGE:", average)

