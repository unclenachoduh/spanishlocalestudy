# template_generate.py
# USAGE: python3 edit_template.py moz / python3 edit_template.py ms

import json, string, operator, re, sys

from nltk.tokenize import word_tokenize as tk

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
|    LANGUAGE TEMPLATE SCRIPT          |
|                                      |
| Generate templates, showing          |
| differences between translations.    |
|                                      |
+--------------------------------------+
''')

print(
'''
+-------------------+
| INITIALIZE SYSTEM |
+-------------------+
''')

all_data = ""
langs = []

if sys.argv[1] == "moz":
	# JSON FILE LOCATION
	all_data = "cleaned_json/perfect_data.json"
	langs = ["es", "es-AR", "es-CL", "es-MX"]
elif sys.argv[1] == "ms":
	all_data = "MS_cleaned_json/perfect_data.json"
	langs = ["es", "es-MX"]



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

		templates = {}
		templatecounts = {}

		templatecounts2 = {}


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
		raw_templates_count = 0
		for key in keys:

			total_keys_count += 1

			if key in data2:

				total_shared_count += 1

				str1 = data1[key][lang1]
				str2 = data2[key][lang2]

				### TOKENIZE AND LOWER
				str1 = ' '.join(tk(str1)).lower()
				str2 = ' '.join(tk(str2)).lower()

				if str1 == str2:
					perfect_matches_count += 1
					continue

				raw_templates_count += 1

				# Tokenize and remove punctuation
				table = str.maketrans('', '', string.punctuation)
				atemp = [w.translate(table) for w in tk(str1)]
				btemp = [w.translate(table) for w in tk(str2)]

				# remove empty words (punctuation)
				a = []
				b = []
				for item in atemp:
					if item != '':
						a.append(item)

				for item in btemp:
					if item != '':
						b.append(item)

				if a == b:
					continue

				### Collect all grams that exist in both strings

				blocks = []

				front = 0
				while front <= len(a):

					back = front

					while back <= len(a):


						length = back - front

						bfront = 0
						bback = bfront + length

						while bback <= len(b):

							if a[front:back] == b[bfront:bback] and a[front:back] != []:
								blocks.append([length, front, back, a[front:back], bfront, bback])

							bfront += 1
							bback += 1

						back += 1

					front += 1


				### Sort ~BLOCKS~ by size

				blocks = sorted(blocks, key=operator.itemgetter(0), reverse=True)



				### Create templates


				for block in blocks:

					if a[block[1]:block[2]] == block[3] and b[block[4]:block[5]] == block[3]:

						ind = block[1]

						while ind < block[2]:
							a[ind] = "__"
							ind += 1

						ind = block[4]

						while ind < block[5]:
							b[ind] = "__"
							ind += 1

				newa = " ".join(a)

				newa = re.sub("(__ )+", "__ ", newa)
				newa = re.sub("( __)+", " __", newa)

				newb = " ".join(b)

				newb = re.sub("(__ )+", "__ ", newb)
				newb = re.sub("( __)+", " __", newb)

				keyname = newa + " | " + newb

				if newa == "__ __" and newb == "__ __":

					keyname = "SYNTAX | SYNTAX"

				if newa == newb:

					keyname = "SYNTAX | SYNTAX"

				if newa.lower() == newb.lower() and keyname != "SYNTAX | SYNTAX":
					keyname = "Capitalization | Capitalization"

				keyname = keyname.lower()

				if keyname not in templates:
					templates[keyname] = [str1 + " | " + str2]
					templatecounts[keyname] = 1
				else:
					templates[keyname].append(str1 + " | " + str2)
					templatecounts[keyname] += 1

				front, back = keyname.split(" | ") 

				temppartsf = front.split("__")
				temppartsb = back.split("__")

				countrealwordsf = 0
				countrealwordsb = 0

				fword = ""
				bword = ""

				for word in temppartsf:
					if re.search('[a-zA-Z]', word):
						countrealwordsf += 1
						fword = word.strip()

				for word in temppartsb:
					if re.search('[a-zA-Z]', word):
						countrealwordsb +=1
						bword = word.strip()

				if countrealwordsf == 1 and countrealwordsb == 1 and fword != bword:

					keyname = fword + " | " + bword

				if keyname not in templatecounts2:
					templatecounts2[keyname] = 1
				else:
					templatecounts2[keyname] += 1


		print("String IDs:", total_keys_count)
		print("Shared IDs:", total_shared_count)
		print("Matches:", perfect_matches_count)
		print("Templates:", raw_templates_count, total_shared_count - perfect_matches_count)



		if lang1 != lang2:
			sorted_d = sorted(templatecounts2.items(), key=operator.itemgetter(1), reverse=True)

			print(lang1, "to", lang2)

			oneway = []
			bidi = []

			for change in sorted_d:
				if change[0].count("|") > 1:
					print("problem")
				else:
					front, back = change[0].split(" | ")

					if back + " | " + front in templatecounts2:
						bidi.append(change)
					else:
						oneway.append(change)

			consistent_changes = 0
			consistent_change_templates = 0

			i = 0
			occ = oneway[i][1]
			while occ > 1 and i < len(oneway):

				print(str(i+1) + "\t" + str(oneway[i][1]) + "\t" + oneway[i][0])

				i+= 1
				occ = oneway[i + 1][1]
				consistent_changes += oneway[i][1]
				consistent_change_templates += 1

			print()

			i = 0
			while (i < 50 and i < len(bidi)) or bidi[i][1] > 1:

				print(str(i+1) + "\t" + str(bidi[i][1]) + "\t" + bidi[i][0])

				i+= 1

			print()

			oneway_total = 0
			bidi_total = 0


			for entry in oneway:
				oneway_total += entry[1]
			for entry in bidi:
				bidi_total += entry[1]

			print("TOTAL SEGMENTS:", oneway_total + bidi_total)
			print("TOTAL TEMPLATES:", len(oneway) + len(bidi))
			print("Unique Changes | Templates:", len(oneway), "| Segments:", oneway_total )
			print("Inconsistent Changes | Templates:", len(bidi), "| Segments:", bidi_total )
			print("CONSISTENT CHANGES| Templates:", consistent_change_templates, " | Segments:", consistent_changes)
			print()
