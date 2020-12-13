# edit_distance.py
# USAGE: python3 edit_distance.py moz / python3 edit_distance.py ms

import json, sys

from helper_functions import nltk_bleu_corpus

from nltk.tokenize import word_tokenize

def sim(langs, location):

	print()
	print("AVERAGE EDIT DISTANCE AND MAX DIFF BETWEEN EDIT DISTANCE")
	for lang1 in langs:

		data1_label = location + lang1 + ".json" 
		data1_temp = json.loads(open(data1_label).read())

		data1 = data1_temp["data"]

		keys = data1.keys()
		print(lang1, "TOTAL SEGMENTS:", len(keys))

		scores = []
		scores_nomatch = []

		for lang2 in langs:

			accepted = 0
			accepted_nomatch = 0

			if lang1 == lang2:
				continue

			data2_label = location + lang2 + ".json" 
			data2_temp = json.loads(open(data2_label).read())
			data2 = data2_temp["data"]

			candidate = []
			reference = []

			candidate_nomatch = []
			reference_nomatch = []

			for key in keys:

				if key in data1 and key in data2:

					a = data1[key][lang1]
					b = data2[key][lang2]

					### TOKENIZE AND LOWER
					a = ' '.join(word_tokenize(a)).lower()
					b = ' '.join(word_tokenize(b)).lower()

					candidate.append([a])
					reference.append(b)
					accepted += 1

					if a != b:
						candidate_nomatch.append([a])
						reference_nomatch.append(b)
						accepted_nomatch += 1


			print()
			score = nltk_bleu_corpus(candidate, reference)

			print("LOCALE:", lang1, lang2)
			print("BLEU:", score)
			print("SEG IDs:", accepted)

			scores.append(score)

			print()
			print("NO PERFECT MATCHES")

			print(len(candidate_nomatch), len(reference_nomatch))
			score = nltk_bleu_corpus(candidate_nomatch, reference_nomatch)

			print("LOCALE:", lang1, lang2)
			print("BLEU:", score)
			print("SEG IDs:", accepted_nomatch)
			scores_nomatch.append(score)


		print()
		print(lang1, "AVERAGE SCORE:", sum(scores) / len(scores))
		print()
		print("NO PERFECT MATCHES")
		print(lang1, "AVERAGE SCORE:", sum(scores_nomatch) / len(scores_nomatch))


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
| translations of the same segment in  |
| different locale variants using      |
| BLEU score.                          |
|                                      |
+--------------------------------------+
''')

	print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')

	langs = []
	location = ""

	if sys.argv[1] == "moz":
		langs = ["es", "es-AR", "es-CL", "es-MX"]
		location = "cleaned_json/"
	elif sys.argv[1] == "ms":
		langs = ["es", "es-MX"]
		location = "MS_cleaned_json/"

	sim(langs, location)
