import ngram
import re
import string
from preprocess import *
from stemming.porter2 import stem
import nltk
import numpy as np

if __name__ == "__main__":
    model = ngram.ngram(3)
    # Train the model on text file preprocessed
    with open("preprocessed/train_set.txt", 'r') as train_set:
        model.train(train_set.read())

    with open("Holmes.machine_format.questions.txt", 'r') as questions_machine, \
    open("preprocessed/questions.txt", 'r') as questions_set, \
    open("Holmes.machine_format.answers.txt", 'r') as ans_machine, \
    open("preprocessed/answers.txt", 'r') as answers_set:
        # prepare questions for preprocessing
        questions = questions_machine.read().split('\n')

        # format answers for easier comparison
        answers = ans_machine.read().split('\n')

        questions_set = questions_set.read().split('\n')
        answers_set = answers_set.read().split('\n')

        i = 0
        sentences = []
        words = ""
        rights = 0
        for line in questions:
            i += 1
            if re.search("\[(.*)\]", line):
                # formating of the word to find
                word = re.search("\[(.*)\]", line).group(1)
                word = word.translate(string.maketrans("",""), string.punctuation).lower()
                word = re.sub("[0-9]+", "7", word)
                word = stem(word)

                # Retrieve the words needed for ngram
                line = questions_set[i - 1].split(' ')
                if line.index(word) > 2:
                    words = ' '.join(line[line.index(word) - 3 : line.index(word) + 1])
                else:
                    words = ' '.join(line[line.index(word) - line.index(word) : line.index(word) + 1])
                sentences.append(words)
                words = ""
                if i%5 == 0:
                    if re.search("\[(.*)\]", answers[i/5 - 1]):
                        ans_word = re.search("\[(.*)\]", answers[i/5 - 1]).group(1)
                        ans_word = ans_word.translate(string.maketrans("",""), string.punctuation).lower()
                        ans_word = re.sub("[0-9]+", "7", ans_word)
                        ans_word = stem(ans_word)
                    else: 
                        ans_word = ""

                    # Check success
                    print "Compute prediction for question", i/5
                    result = sentences[np.argmax(model.compute_prediction(sentences, 2))]

                    if result.split(' ')[-1] == ans_word:
                        rights += 1
                    sentences = []
        print len(answers) - 1, rights
        print "Success rate: ", (rights * 100.0) / (len(answers) - 1)