# helper_functions.py

from nltk.translate.bleu_score import corpus_bleu
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

def nltk_bleu_sentence(sent_a, sent_b):

	a = [word_tokenize(sent_1)]
	b = word_tokenize(sent_2)

	score = score = sentence_bleu([a], b)
	
	return score


def nltk_bleu_corpus(sents_a, sents_b):

	a = []
	b = []
	for candidate in sents_a:
		candidates = []
		for sent in candidate:
			candidates.append(word_tokenize(sent))

		a.append(candidates)

	for sent in sents_b:
		b.append(word_tokenize(sent))

	score = score = corpus_bleu(a, b)
	
	return score


if __name__ == '__main__':
	reference = ["this is a test string"]
	candidate = [["This is a test string", "this is a test string ."]]

	print(nltk_bleu_corpus(candidate, reference))