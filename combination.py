"""
Combines many algorithms 

"""

import pickle
import numpy
#from sklearn import preprocessing
#import random

"""
def softmax(array):
	denominator = numpy.exp(preprocessing.scale(array)).sum()
	return numpy.array([numpy.e**result/denominator for result in array])
"""

def main():
	answers = []
	answer_dictionary = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
	with open("holmes_answers.txt") as openedfile:
		for line in openedfile:
			answer = line.split(" ")[0][-2]
			answers.append(answer_dictionary[answer])
	answers = numpy.array(answers)

	lsa = numpy.load("LSApredictions.npy")
	hybrid = numpy.load("scores_sg_hs_640_win10_min5_epo5.npy")
	with open("array.pickle") as f:
		nonc = numpy.array(pickle.load(f))
	#print (numpy.argmax(nonc,axis=1) == answers).sum()/float(len(answers))
	#print lsa.shape, hybrid.shape, nonc.shape

	#weights = softmax(numpy.array([0.441, 0.567, 0.376]))
	models = [lsa, hybrid, nonc]

	print "Skip-gram or not"
	performance = 0
	for i,answer in enumerate(answers):
		scores = []
		for model in range(3):
			current = models[model][i]

			best = current.argmax()
			best_confidence = current.max()
			current[best] = current.min()-1
			less = current.argmax()
			less_confidence = current.max()
			scores.append((best_confidence-less_confidence, best))

		if scores[1][0] < 0.002:
			del scores[1]
			scores.sort()
			prediction = scores[-1][1]
		else:
			prediction = scores[1][1]
		if prediction == answer:
			performance += 1
	print performance/float(len(answers))

	"""
	print "Addition des vecteurs de probabilites"	
	performance = 0
	for i,answer in enumerate(answers):
		prediction = numpy.zeros(5)
		for model in range(3):
			if model < 2:
				prediction += weights[model]*softmax(models[model][i])
			else:
				prediction += weights[model]*models[model][i]
		if prediction.argmax() == answer:
			performance += 1
	print performance/float(len(answers))
	


	print "Addition de votes"
	vote_weights = [0.67, 0.58, 0.29, 0.10, 0.08]
	performance = 0
	votes_predictions = numpy.zeros((1040,5))
	for i,answer in enumerate(answers):
		prediction = numpy.zeros(5)
		for j,model in enumerate(models):
			votes = range(1,6)
			votes.reverse()
			for k,vote in enumerate(votes):
				#print model[i]*10000
				prediction[model[i].argmax()] += vote_weights[k]*weights[j]*vote#vote 
				model[i][model[i].argmax()] = model[i].min()-1.0

		if prediction.argmax() == answer:
			performance += 1
		votes_predictions[i] = prediction
	
	#print (votes_predictions > 14).sum()
	print performance/float(len(answers))

	

	print "Choix de celui le plus confiant"
	performance = 0
	for i,answer in enumerate(answers):
		scores = []
		for model in range(3):
			if model < 2:
				current = softmax(models[model][i])
			else:
				current = models[model][i]

			best = current.argmax()
			best_confidence = current.max()
			current[best] = current.min()-1
			less = current.argmax()
			less_confidence = current.max()
			scores.append((best_confidence-less_confidence, best))

		scores.sort()
		prediction = scores[-1][1]
		if prediction == answer:
			performance += 1
	print performance/float(len(answers))

	
	three = []
	for i, answer in enumerate(answers):
		predictions = []
		for model in models:
			predictions.append(model[i].argmax())
		if answer not in predictions:
			three.append(i)

	print len(three)
	print three
	"""	

if __name__ == "__main__":
	main()