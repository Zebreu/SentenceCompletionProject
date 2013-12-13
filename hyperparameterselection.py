import numpy

import lsa

model = lsa.Lsa()

model.repeated_words = list(numpy.load("word_table_new_300.npy"))

word_vec = numpy.load("word_vectors_new_300.npy")

gauss_values = numpy.linspace(1.5,7,15)
dimensions = range(210,290,5)

scores = []

for d in dimensions:
	for value in gauss_values:
		print value, d
		model.word_vectors = word_vec.T[0:d].T
		scores.append(lsa.test_whole(model, sigma = value))

numpy.save("scores", numpy.array(scores))
print max(scores)
print dimensions(scores.index(max(scores))/15), gauss_values(scores.index(max(scores))%15)
