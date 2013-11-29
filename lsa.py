'''
Latent Semantic Analysis for sentence completion

Created on 2013-11-24

@author: Sebastien Ouellet sebouel@gmail.com
'''
import numpy
import math
import scipy.sparse.linalg
#import pickle
import os
import sys
import itertools

class Lsa:
    def __init__(self):
        self.dictionary = {}
        
    def parse_documents(self, documents):
        """ Builds a dictionary of words encountered and in which sentences they are found """
        #self.number_documents = len(documents)
        self.number_documents = 0
        for index,document in enumerate(documents):
            words = document.split(" ")
            if len(words) > 0:
                self.number_documents += 1
                for word in words:
                    if word in self.dictionary:
                        self.dictionary[word].append(index)
                    else:
                        self.dictionary[word] = [index]
                    
        
    
    def build_count_matrix(self, common_threshold = 100): # common_threshold argument is useless for now
        """ Builds a matrix Words*Sentences from the dictionary """
        self.repeated_words = [word for word in self.dictionary.keys() if (len(self.dictionary[word])>1)]# and len(self.dictionary[word]) < self.number_documents*common_threshold)]
        #print len(self.repeated_words)
        #print self.number_documents
        #print len(self.dictionary["the"])
        #self.repeated_words = [word for word in self.repeated_words if word != ""] # Otherwise it always contains an empty string
        self.count_matrix = scipy.sparse.lil_matrix((len(self.repeated_words),self.number_documents))
        #self.count_matrix = numpy.zeros((len(self.repeated_words),self.number_documents))
        length = len(self.repeated_words)
        for index,word in enumerate(self.repeated_words):
            sys.stdout.flush()
            sys.stdout.write("\r"+str(round(float(index)/length,3))+"%")
            for document in self.dictionary[word]:
                self.count_matrix[index,document] += 1

        #self.count_matrix = self.count_matrix.tocsc()
    
    def train(self, documents):
        self.parse_documents(documents)
        print "Dictionary size:", len(self.dictionary.keys())
        self.build_count_matrix()
        print ""
        print "Reduced dictionary size:", len(self.repeated_words)
        print "Number of sentences:", self.number_documents
        print ""
        
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
        for row,column,value in itertools.izip(temp_matrix.row, temp_matrix.col, temp_matrix.data):
            sys.stdout.flush()
            sys.stdout.write("\r"+str(round(counter/length,3))+"%")
            tf = value/column_sums[column]
            #print row_sums[row]
            #print number_documents_float/row_sums[row]
            idf = math.log(number_documents_float/row_sums[row])
            self.count_matrix[row,column] = tf*idf
            counter += 1.0
        """
        for row in xrange(self.count_matrix.shape[0]):
            for column in xrange(self.count_matrix.shape[1]):
                tf = self.count_matrix[row,column]/column_sums[column]
                idf = math.log((float(self.number_documents))/row_sums[row])
                self.count_matrix[row,column] = tf*idf
        """
    def reduce_dimensionality(self):
        """ Trims down matrices to only use a small number of important dimensions """
        trim = 200 # Better: Mathematical approximation (given size of singular values) or validation of hyper-parameter
        self.words_u, self.singular_values, self.documents_vt = scipy.sparse.linalg.svds(self.count_matrix, trim)
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

def score_average(sentence, position,lsa):
    """ Score a sentence by computing the average similarity between the target word and the other words """
    score = 0
    sentence = sentence.replace("\n","")
    words = sentence.split(" ")
    del words[0]
    target = lsa.repeated_words.index(words[position])
    target = lsa.word_vectors[target]
    del(words[position])
    for word in words:
        score += cosine_similarity(target, lsa.word_vectors[lsa.repeated_words.index(word)])
    score = score/(len(words)+1)
    return score

def test_sentences(sentences, lsa, score = score_average):
    """ Returns the scores for sentences, testing whether they are semantically compatible """
    position = 0
    for word1, word2 in zip(sentences[0],sentences[1]):
        if word1 == word2:
            position += 1
        else:
            break
        
    return [score(sentence, position, lsa) for sentence in sentences]

def test_whole(lsa, data = None):
    sentences = []
    answers = []
    answer_dictionary = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
    with open("holmes_questions.txt") as openedfile:
        counter = 0
        question = []
        for line in openedfile:
            if counter == 4:
                sentences.append(question)
                question = []
                counter = 0
            else:
                question.append(line)
                counter += 1
    with open("holmes_answers.txt") as openedfile:
        for line in openedfile:
            answer = line.split(" ")[0][-2]
            answers.append(answer_dictionary[answer])
        
    print len(answers)
    print len(sentences)
    predictions = []
    for i,question in enumerate(sentences):
        print i
        predictions.append(test_sentences(question, lsa))
    
    #numpy.save("predictions", numpy.array(predictions))
    performance = 0
    for i,prediction in enumerate(predictions):
        answer = numpy.argmax(prediction)
        if answer == answers[i]:
            performance += 1
    print "Tested", i, "questions"
    print float(performance)/i

def read_files():
    filenames = os.listdir("training")
    sentences = []
    for filename in filenames:
        if filename[-4:] == ".txt":
            with open(os.path.join("training",filename)) as openedfile:
                #print filename
                sentences.extend([line for line in openedfile])
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
                sentences.extend([line for line in openedfile])
         
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
    numpy.save("word_vectors", lsa.word_vectors)
    
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