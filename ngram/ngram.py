import collections

class ngram:

	def __init__(self, n):
		self.n = n

	def countOccurences(self, n, text, grams):
		if n == 1:
			self.ngrams = grams
		else:
			occurences = grams
			for i in range(len(text)):
				g = ' '.join(text[i:i+n])
				occurences.setdefault(g, 0)
				occurences[g] += 1
			self.countOccurences(n-1, text, occurences)

	def train(self, text):
		self.countOccurences(self.n, text.split(' '), {})
		# self.V = len(dict((k, v) for k, v in self.ngrams.iteritems() if len(k) == 1))
		# self.ngrams = {k: v for k, v in self.ngrams.iteritems() if not (len(k.split(' ')) == 4 and v == 1)}
		# self.frequencies = {}
		# self.frequenciesPlusOne = {}
		# self.n_fourgrams = 0
		# self.n_trigrams = 0
		# self.n_bigrams = 0
		# for (k, v) in self.ngrams.iteritems():
		# 	if len(k.split(' ')) == 4:
		# 		self.n_fourgrams += 1
		# 		# self.n_fourgrams += v
		# 	elif len(k.split(' ')) == 3:
		# 		self.n_trigrams += 1
		# 		# self.n_trigrams += v
		# 	elif len(k.split(' ')) == 2:
		# 		self.n_bigrams += 1
		# 		# self.n_bigrams += v
		# 	self.frequencies.setdefault(v, 0)
		# 	self.frequencies[v] += 1
		# 	self.frequenciesPlusOne.setdefault(v + 1, 0)
		# 	self.frequenciesPlusOne[v + 1] += 1

		# self.N = 0
		# for (k, v) in self.ngrams.iteritems():
		# 	self.N += v * self.frequencies[v]



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
				trigram = self.ngrams[sMinusOne]
			else: 
				trigram = 0

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

				probs.append(bigram + 2.0 * trigram + 3.0 * fourgram)
			elif ngramType == 3:
				if previousWords in self.ngrams:
					histgram = self.ngrams[previousWords]
				else:
					histgram = 0					
				probs.append(float(fourgram + 1)/float(histgram + self.V))
			elif ngramType == 4:
				if s in self.ngrams:
					c = self.ngrams[s]
					# n_cplus1 = len([k for (k, v) in self.ngrams.iteritems() if v == (c + 1)])
					# n_c = len([k for (k, v) in self.ngrams.iteritems() if v == c])
					n_cplus1 = self.frequenciesPlusOne[c + 1]
					n_c = self.frequencies[c]
					occurs_once = (c + 1) *  n_cplus1 / n_c
				else:
					occurs_once = self.frequencies[1]

				# if len(s.split(' ')) == 4:
				# 	probs.append(float(occurs_once) / float(self.n_fourgrams))
				# elif len(s.split(' ')) == 3:
				# 	probs.append(float(occurs_once) / float(self.n_trigrams))
				# else:
				# 	probs.append(float(occurs_once) / float(self.n_bigrams))
				probs.append(float(occurs_once) / float(self.N))
			else:
				print "Wrong type"
					
		return probs
