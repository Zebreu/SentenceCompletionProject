import ngram
import re
import string
from preprocess import *
import numpy as np

if __name__ == "__main__":
    model = ngram.ngram(4)
    # Train the model on text file preprocessed
    with open("Holmes_Training_Data/preprocessed/train_set_deter.txt", 'r') as train_set:
 		model.train(train_set.read())

    with open("Holmes.machine_format.questions.txt", 'r') as questions, open("Holmes.machine_format.answers.txt", 'r') as ans:
        # prepare questions for preprocessing
        questions = questions.read().split('\n')
        questions_set = '\n'.join(remove_spaces(remove_determiner(line_identifiers(remove_numbers(remove_punctuation(remove_uppercase(questions)))))))

        # format answers for easier comparison
        answers = ans.read().split('\n')

        # 
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

                # Retrieve de words needed for ngram
                line = questions_set.split('\n')[i - 1].split(' ')
                words = ' '.join(line[line.index(word) - 3 : line.index(word) + 1])
                sentences.append(words)
                words = ""
                if i%5 == 0:
                    if re.search("\[(.*)\]", answers[i/5 - 1]):
                        ans_word = re.search("\[(.*)\]", answers[i/5 - 1]).group(1)
                    else: 
                        ans_word = ""

                    # Check success
                    result = sentences[np.argmax(model.compute_prediction(sentences))]
                    if result.split(' ')[-1] == ans_word:
                        rights += 1
                    sentences = []
        print "Success rate: ", (rights * 100.0) / len(answers)