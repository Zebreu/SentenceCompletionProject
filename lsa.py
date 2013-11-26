'''
Latent Semantic Analysis for sentence completion

Created on 2013-11-24

@author: Sebastien Ouellet sebouel@gmail.com
'''
import numpy
import math
import scipy.linalg
import pickle
import os

class Lsa:
    def __init__(self):
        self.dictionary = {}
        
    def parse_documents(self, documents):
        """ Builds a dictionary of words encountered and in which sentences they are found """
        self.number_documents = len(documents)
        for index,document in enumerate(documents):
            words = document.split(" ")
            for word in words:
                if word in self.dictionary:
                    self.dictionary[word].append(index)
                else:
                    self.dictionary[word] = [index]
    
    def build_count_matrix(self):
        """ Builds a matrix Words*Sentences from the dictionary """
        self.repeated_words = [word for word in self.dictionary.keys() if len(self.dictionary[word])>1]
        #self.repeated_words = [word for word in self.repeated_words if word != ""] # Otherwise it always contains an empty string
        self.count_matrix = numpy.zeros((len(self.repeated_words),self.number_documents))
        for index,word in enumerate(self.repeated_words):
            for document in self.dictionary[word]:
                self.count_matrix[index,document] += 1
    
    def train(self, documents):
        self.parse_documents(documents)
        self.build_count_matrix()
        
    def weighting_tfidf(self):
        """ Term frequency/Inverse document frequency weighting
            Measures how common a term is across a sentence and how common it is across all documents """
        column_sums = self.count_matrix.sum(axis=0)
        row_sums = numpy.sum(self.count_matrix > 0, axis=1)
        
        for row in xrange(self.count_matrix.shape[0]):
            for column in xrange(self.count_matrix.shape[1]):
                tf = self.count_matrix[row,column]/column_sums[column]
                idf = math.log((float(self.number_documents))/row_sums[row])
                self.count_matrix[row,column] = tf*idf
    
    def reduce_dimensionality(self):
        """ Trims down matrices to only use a small number of important dimensions """
        self.words_u, self.singular_values, self.documents_vt = scipy.linalg.svd(self.count_matrix)
        print self.words_u.shape, self.singular_values.shape, self.documents_vt.shape
        trim = 200 # Better: Mathematical approximation (given size of singular values) or validation of hyper-parameter
        self.word_vectors = numpy.dot(self.words_u[:,0:trim],numpy.diag(self.singular_values[0:trim]))
        
def cosine_similarity(word1, word2):
    """ Returns a value between -1 (opposite semantic properties) and 1 (identical properties) """
    return numpy.dot(word1,word2)/(numpy.linalg.norm(word1)*numpy.linalg.norm(word2))

def main():
    text = ""
    filenames = os.listdir(".")
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
            with open(filename) as openedfile:
                sentences.extend([line for line in openedfile])
                
    # LSA
    lsa = Lsa()
    lsa.train(sentences)
    lsa.weighting_tfidf()
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
    to_save = lsa.word_vectors
    
    pickle.dump(to_save,"word_vectors.sav")
    
    
if __name__ == "__main__":
    main()