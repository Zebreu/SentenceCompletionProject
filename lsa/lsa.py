'''
Latent Semantic Analysis for sentence completion

Created on 2013-11-24

@author: Sebastien Ouellet sebouel@gmail.com
'''
import numpy
import math
import scipy.sparse.linalg
import scipy.stats
#import pickle
import os
import sys
import itertools
import datetime
from sklearn import preprocessing


class Lsa:
    def __init__(self):
        self.dictionary = {}
        
    def parse_documents(self, documents, count=False):
        """ Builds a dictionary of words encountered and in which sentences they are found """
        documents = [document.split(" ") for document in documents if len(document.split(" ")) > 1] # Minimum length of sentence
        self.number_documents = len(documents)
        self.total_words = 0
        for index,document in enumerate(documents):
            words = document
            for word in words:
                self.total_words += 1
                if count:
                    if word in self.dictionary:
                        self.dictionary[word] += 1
                    else:
                        self.dictionary[word] = 1
                else:
                    if word in self.dictionary:
                        self.dictionary[word].append(index)
                    else:
                        self.dictionary[word] = [index]
        if count:
            print self.total_words, "total words"
            self.total_words = float(self.total_words)
            print "Normalization"
            for word in self.dictionary.keys():
                self.dictionary[word] = self.dictionary[word]/self.total_words
        
    
    def build_count_matrix(self, common_threshold = 100): # common_threshold argument is useless for now
        """ Builds a matrix Words*Sentences from the dictionary """
        self.repeated_words = [word for word in self.dictionary.keys() if (len(self.dictionary[word])>5)]# and len(self.dictionary[word]) < self.number_documents*common_threshold)] # Min and max number of occurrences
        #print len(self.repeated_words)
        #print self.number_documents
        #print len(self.dictionary["the"])
        #self.repeated_words = [word for word in self.repeated_words if word != ""] # Otherwise it always contains an empty string
        self.count_matrix = scipy.sparse.lil_matrix((len(self.repeated_words),self.number_documents))
        #self.count_matrix = numpy.zeros((len(self.repeated_words),self.number_documents))
        length = len(self.repeated_words)
        print "Started at", str(datetime.datetime.now())
        for index,word in enumerate(self.repeated_words):            
            pretty_counter(index,length)
            for document in self.dictionary[word]:
                self.count_matrix[index,document] += 1
        print "Ended at", str(datetime.datetime.now())
        #self.count_matrix = self.count_matrix.tocsc()
    
    def train(self, documents):
        self.parse_documents(documents)
        print "Dictionary size:", len(self.dictionary.keys())
        self.build_count_matrix()
        print "Reduced dictionary size:", len(self.repeated_words)
        print "Number of sentences:", self.number_documents
        
    def weighting_tfidf(self):
        """ Term frequency/Inverse document frequency weighting
            Measures how common a term is across a sentence and how common it is across all documents """
        del self.dictionary # Memory management
        # Note: Could sum rows and columns on the fly to save memory
        column_sums = numpy.array(self.count_matrix.sum(axis=0))[0]
        #row_sums = numpy.sum(self.count_matrix > 0, axis=1)
        row_sums = numpy.array(self.count_matrix.astype("bool").astype("float32").sum(axis=1)).T[0]
        temp_matrix = self.count_matrix.tocoo()
        length = len(temp_matrix.data)
        print "Data entries to weight:", length
        number_documents_float = float(self.number_documents)
        counter = 0.0
        print "Started at", str(datetime.datetime.now())
        for row,column,value in itertools.izip(temp_matrix.row, temp_matrix.col, temp_matrix.data):
            #pretty_counter(counter, length)
            tf = value/column_sums[column]
            #print row_sums[row]
            #print number_documents_float/row_sums[row]
            idf = math.log(number_documents_float/row_sums[row])
            self.count_matrix[row,column] = tf*idf
            counter += 1.0
        print "Ended at", str(datetime.datetime.now())
        """
        for row in xrange(self.count_matrix.shape[0]):
            for column in xrange(self.count_matrix.shape[1]):
                tf = self.count_matrix[row,column]/column_sums[column]
                idf = math.log((float(self.number_documents))/row_sums[row])
                self.count_matrix[row,column] = tf*idf
        """
    def reduce_dimensionality(self, trim = 250):
        """ Trims down matrices to only use a small number of important dimensions """
        print "Started at", str(datetime.datetime.now())
        self.words_u, self.singular_values, self.documents_vt = scipy.sparse.linalg.svds(self.count_matrix, trim)
        print "Ended at", str(datetime.datetime.now())
        #self.words_u, self.singular_values, self.documents_vt = scipy.linalg.svd(self.count_matrix)
        print self.words_u.shape, self.singular_values.shape
        del self.documents_vt # Memory management
        self.word_vectors = numpy.dot(self.words_u,numpy.diag(self.singular_values))


def pretty_counter(i,length):
    sys.stdout.flush()
    sys.stdout.write("\r"+str(round(float(i)/length,3))+"%")
        
def cosine_similarity(word1, word2):
    """ Returns a value between -1 (opposite semantic properties) and 1 (identical properties) """
    return numpy.dot(word1,word2)/(numpy.linalg.norm(word1)*numpy.linalg.norm(word2))

def average_score(sentence, position,lsa, sigma):
    """ Scores a sentence by computing the average similarity between the target word and the other words """
    score = 0
    sentence = sentence.replace("\n","")
    words = sentence.split(" ")
    del words[0] # ID of the sentence
    target = lsa.repeated_words.index(words[position])
    target = lsa.word_vectors[target]
    #print words[position]
    del(words[position])
    for word in words:
        score += cosine_similarity(target, lsa.word_vectors[lsa.repeated_words.index(word)])
    score = score/(len(words)+1)
    return score

def unigram_weighting(lsa, words):
    unigrams = preprocessing.scale(numpy.array([lsa.dictionary[word] for word in words]))
    denominator = numpy.exp(unigrams).sum()
    unigrams = [numpy.e**unigram/denominator for unigram in unigrams]
    weights = [1.0/unigram for unigram in unigrams]
    return weights

def not_gaussian_score(sentence, position, lsa, sigma):
    """ Scores a sentence with weighted similarities, a wide gaussian centered on the target word """
    score = 0
    sentence = sentence.replace("\n","")
    words = sentence.split(" ")
    del words[0] # ID of the sentence
    target = lsa.repeated_words.index(words[position])
    target = lsa.word_vectors[target]
    #print words[position]
    del(words[position])
    gaussian = scipy.stats.norm(position,sigma) # Standard deviation could change, (len(words)) dependent #(250<300, 5)
    unigram_weights = unigram_weighting(lsa, words)
    for i,word in enumerate(words):
        weight = gaussian.pdf(i-position)
        score += unigram_weights[i]*weight*(cosine_similarity(target, lsa.word_vectors[lsa.repeated_words.index(word)]))
    score = score/(len(words)+1)
    return score     

def gaussian_score(sentence, position, lsa, sigma):
	""" Scores a sentence with weighted similarities, a wide gaussian centered on the target word """
	score = 0
	sentence = sentence.replace("\n","")
	words = sentence.split(" ")
	del words[0] # ID of the sentence
	target = lsa.repeated_words.index(words[position])
	target = lsa.word_vectors[target]
	#print words[position]
	del(words[position])
	gaussian = scipy.stats.norm(position,sigma) # Standard deviation could change, (len(words)) dependent #(250<300, 5)
	for i,word in enumerate(words):
		weight = gaussian.pdf(i-position)
		score += weight*(cosine_similarity(target, lsa.word_vectors[lsa.repeated_words.index(word)]))
	score = score/(len(words)+1)
	return score	 

def test_sentences(sentences, lsa, sigma, score = gaussian_score):
    """ Returns the scores for sentences, testing whether they are semantically compatible """
    position = 0
    for word1, word2 in zip(sentences[0].split(" ")[1:],sentences[1].split(" ")[1:]):
        if word1 == word2:
            position += 1
        else:
            break
        
    return [score(sentence, position, lsa, sigma) for sentence in sentences]

def test_whole(lsa, data = None, sigma = 4.5):
    sentences = []
    answers = []
    answer_dictionary = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
    with open("holmes_questions.txt") as openedfile:
        counter = 0
        question = []
        for line in openedfile:
            if counter == 5:
                sentences.append(question)
                question = [line]
                counter = 1
            else:
                question.append(line)
                counter += 1
    sentences.append(question)
    print len(sentences), "sets of sentences"

    with open("holmes_answers.txt") as openedfile:
        for line in openedfile:
            answer = line.split(" ")[0][-2]
            answers.append(answer_dictionary[answer])
    
    predictions = []
    for i,question in enumerate(sentences):
        pretty_counter(i,len(answers))
        predictions.append(test_sentences(question, lsa, sigma))
        #print predictions[-1], answers[i]
    #numpy.save("predictions", numpy.array(predictions))
    performance = 0
    for i,prediction in enumerate(predictions):
        answer = numpy.argmax(prediction)
        if answer == answers[i]:
            performance += 1
    #numpy.savetxt("LSApredictions",predictions)
    print
    print float(performance)/i
    return float(performance)/i

def read_files():
    filenames = os.listdir("training")
    sentences = []
    for filename in filenames:
        if filename[-4:] == ".txt":
            with open(os.path.join("training",filename)) as openedfile:
                #print filename
                sentences.extend([line.replace("\n","") for line in openedfile])
    return sentences

def main():
    
    filenames = os.listdir("training")
    """
    with open("2TALE10.TXT") as openedfile:
        text = text.append(openedfile.read())
        # Preprocessing    
        text = text.replace("\n"," ")
        text = text.replace(",","")
        text = text.replace('"',"")
        # To do: lowercase, digits, punctuation
        sentences = text.split(".")
        sentences = [sentence.strip() for sentence in sentences]
        sentences = sentences[100:1800]
        sentences = [sentence for sentence in sentences if len(sentence)>0]
    """
    sentences = []
    for filename in filenames:
        if filename[-4:] == ".txt":
            with open(os.path.join("training",filename)) as openedfile:
                #print filename
                sentences.extend([line.replace("\n","") for line in openedfile])
         
    # LSA
    lsa = Lsa()
    print "Parsing sentences"
    lsa.train(sentences)
    #numpy.save("pre_tfidf", lsa.count_matrix)
    #pre_weighting = open("pre_weighting.sav","wb")
    #pickle.dump(lsa.count_matrix, pre_weighting)
    #pre_weighting.close()
    print "Weighting"
    lsa.weighting_tfidf()
    #numpy.save("pre_svd", lsa.count_matrix)
    #pre_svd = open("pre_svd.sav","wb")
    #pickle.dump(lsa.count_matrix, pre_svd)
    #pre_svd.close()
    print "Decomposition"
    lsa.reduce_dimensionality()
    #print lsa.count_matrix
    #print lsa.words_u, lsa.singular_values, lsa.documents_vt
    #print lsa.repeated_words
    
    """
    y = lsa.repeated_words.index("widow")
    g= lsa.repeated_words.index("weapons")
    t= lsa.repeated_words.index("hair")
    
    word1= lsa.word_vectors[y]
    word2= lsa.word_vectors[g]
    word3= lsa.word_vectors[t]
    
    print cosine_similarity(word1, word2)
    print cosine_similarity(word1, word3)
    """
    numpy.save("word_vectors_new_250", lsa.word_vectors)
    numpy.save("word_table_new_250", lsa.repeated_words)
    test_whole(lsa)
    return lsa
    
def loading():
    lsa = Lsa()
    lsa.count_matrix = numpy.load("pre_tfidf.sav.npy")
    lsa.weighting_tfidf()
    #matrix_file = open("pre_weighting.sav","rb")
    #matrix = pickle.load(matrix_file)
    #matrix_file.close()
    
    
if __name__ == "__main__":
    #loading()
    main()