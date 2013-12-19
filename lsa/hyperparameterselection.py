import numpy

import lsa

model = lsa.Lsa()

#sentences = lsa.read_files()

#model.parse_documents(sentences, count=True)

model.repeated_words = list(numpy.load("word_table_new_500.npy"))

word_vec = numpy.load("word_vectors_new_500.npy")

gauss_values = [3.3]#numpy.linspace(2,8,15)
dimensions = [450]

scores = []

for d in dimensions:
	for value in gauss_values:
		print value, d
		model.word_vectors = word_vec.T[0:d].T
		scores.append(lsa.test_whole(model, sigma = value))

#numpy.save("scores_500_average", numpy.array(scores))
print max(scores)
print dimensions[scores.index(max(scores))/len(gauss_values)], gauss_values[scores.index(max(scores))%len(gauss_values)]
