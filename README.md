# The Spanish Locale Study 

An analysis of linguistic similarity between Spanish locale variants in Mozilla translation files.

**By Kekoa Riggin**

Read the full report [here](report.md)  
Presented at the [#LocWorldWide43](https://locworld.com/events/locworldwide43-virtual-event/) conference as ["How Similar Are Your Spanish Locales: A Data-driven Analysis"](https://locworld.com/sessions/how-similar-are-your-spanish-localizations-a-data-driven-analysis/)

## How to Run

There are scripts for Mozilla's translation memories and Microsoft's My Visual Studio Translation and UI Strings Glossaries located in the [src](src/) folder. To run scripts for MMicrosoft data, replace `moz` argument with `ms`.

1. Put translation data in `src` folder.
	1. For Mozilla data: Get TMX files from [https://transvision.mozfr.org/](https://transvision.mozfr.org/). Save files with naming convention `mozilla_en-US_es-AR.tmx` in a folder called `moz_tmx`.
 	2. Get CSV files for Translation and UI Strings Glossaries from [My Visual Studio downloads](https://my.visualstudio.com/downloads). Save all files to folders with naming convention `es-mx_MS`.
2. `python3 tojson_moz.py` or `python3 tojson_ms.py` to convert the translation files to json files (performs some data cleaning).
3. `python3 perfect.py moz` to get perfect matches and create json files for non-perfect matches.
4. `python3 diff_baseline.py moz` to get a baseline BLEU score (X to X Locale).
5. `python3 max_distance.py moz` to get a baseline poor BLEU score (Source to Target).
6. `python3 edit_distance.py moz` to get the BLEU score between locales (X to Y Locale).
7. `python3 template_generate.py moz` to generate language templates.

**Requirements:**  
1. Python 3.x
2. NLTK Tokenize
3. NLTK BLEU


