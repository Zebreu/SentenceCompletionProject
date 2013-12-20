import collections

class ngram:

	def __init__(self, n):
		self.n = n

	def countOccurences(self, n, text, grams):
		if n == 0:
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
		self.V = len(dict((k, v) for k, v in self.ngrams.iteritems() if len(k) == 1))

	def compute_prediction(self, sentences, ngramType=1):
		probs = []

		for i, s in enumerate(sentences):
			sMinusOne = ' '.join(s.split(' ')[1:])
			sMinusTwo = ' '.join(s.split(' ')[2:])		
			previousWords = ' '.join(s.split(' ')[:-1])

			if len(s.split(' ')) == 3:
				sMinusTwo = sMinusOne
				sMinusOne = s

			if s in self.ngrams:
				fourgram = self.ngrams[s]
			else: 
				fourgram = 0

			if sMinusOne in self.ngrams:
				threegram = self.ngrams[sMinusOne]
			else: 
				threegram = 0

			# Types:
			# - 1: classic n-grams
			# - 2: model from report
			# - 3: Laplace smoothing
			# - 4: Good-turing smoothing
			if ngramType == 1:				
				if previousWords in self.ngrams:
					histgram = self.ngrams[previousWords]
					probs.append(float(fourgram)/float(histgram))
				else:
					probs.append(0)	
			elif ngramType == 2:
				if sMinusTwo in self.ngrams:
					bigram = self.ngrams[sMinusTwo]
				else: 
					bigram = 0

				probs.append(bigram + 2.0 * threegram + 3.0 * fourgram)
			elif ngramType == 3:
				if previousWords in self.ngrams:
					histgram = self.ngrams[previousWords]
				else:
					histgram = 0					
				probs.append((float(fourgram) + 1)/(float(histgram) + self.V))
			elif ngramType == 4:
				if s in self.ngrams:
					c = self.ngrams[s]
					n_cplus1 = len([k for (k, v) in self.ngrams.iteritems() if v == (c + 1)])
					n_c = len([k for (k, v) in self.ngrams.iteritems() if v == c])
					occurs_once = (c + 1) *  n_cplus1 / n_c
				else:
					occurs_once = len([k for (k, v) in self.ngrams.iteritems() if v == 1])

				probs.append(occurs_once / len([k for (k, v) in self.ngrams.iteritems() if len(k.split(' ')) == len(s.split(' '))])) 
			else:
				print "Wrong type"
			
		return probs
