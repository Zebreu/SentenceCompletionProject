import collections


class ngram:

	def __init__(self, n):
		self.n = n

	def countOccurences(self, n, text, grams):
		if n == 1:
			self.ngrams = grams
		else:
			occurences = grams
			for i in range(len(text)-n+1):
				g = ' '.join(text[i:i+n])
				occurences.setdefault(g, 0)
				occurences[g] += 1
			self.countOccurences(n-1, text, occurences)

	def train(self, text):
		self.countOccurences(self.n, text.split(' '), {})

	def compute_prediction(self, sentences):
		probs = []
		
		for i, s in enumerate(sentences):
			sMinusOne = ' '.join(s.split(' ')[1:])
			sMinusTwo = ' '.join(s.split(' ')[2:])		
			# if s in self.ngram and sMinusOne in self.nMinusOnegram:
			# if s in self.ngram:
			# 	print s
			# 	# probs.append(float(self.ngram[s])/float(self.nMinusOnegram[sMinusOne]))
			# 	probs.append(self.bigrams[bigram] + 2.0 * self.nMinusOnegram[sMinusOne] + 3.0 * self.ngram[s])
			# else:
			# 	probs.append(0)
			if s in self.ngrams:
				fourgram = self.ngrams[s]
			else: 
				fourgram = 0

			if sMinusOne in self.ngrams:
				threegram = self.ngrams[sMinusOne]
			else: 
				threegram = 0

			if sMinusTwo in self.ngrams:
				bigram = self.ngrams[sMinusTwo]
			else: 
				bigram = 0

			probs.append(bigram + 2.0 * threegram + 3.0 * fourgram)
		return probs
