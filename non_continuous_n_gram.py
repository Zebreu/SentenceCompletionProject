from __future__ import division
from optparse import OptionParser
import os
import pickle
import re
import string
import sys

OPTIONS_PER_SENTENCE = 5
DATABASE = {}


def generate_combinations(l):
    """generate each possible combination of size 2 of the elements in the list `l`

    Return value:
    list of tuples of size 2 containing each generated combination
    """
    combinations = []
    for i in range(len(l)):
        for j in range(i, len(l)):
            combinations.append([l[i], l[j]])
    return combinations


def train(dataset):
    """train the n-gram using a file as input

    Keyword arguments:
    dataset -- file to read dataset from. Each line must contain one sentence.

    Train the n-gram using file `dataset` as input.
    """
    with open(dataset) as f:
        for line in f:
            line = line.split()
            combinations = generate_combinations(line)
            for combination in combinations:
                key = string.join(sorted(combination))
                if key in DATABASE:
                    DATABASE[key] += 1
                else:
                    DATABASE[key] = 1


def compute_score(option, words_in_sentence):
    score = 0
    for word in words_in_sentence:
        key = string.join(sorted((option, word)))
        if key in DATABASE:
            score += DATABASE[key]
    return score


def get_best_option(options, words_in_sentence):
    """returns the option from the list `options` which has the highest score for the words in `words_in_sentence`
    """
    best_score = 0
    best_option = None
    for option in options:
        score = compute_score(option, words_in_sentence)
        if score > best_score:
            best_score = score
            best_option = option
    return best_option


def get_predictions(test_data):
    """compute predictions for the test set given as argument
    """
    with open(test_data) as f:
        i = 0
        predictions = []
        options = []  # stores the different options possible for a single sentence
        for line in f:
            match = re.search('\[([\d\w\'\-,]+)\]', line)
            option = match.group(1)
            if i % OPTIONS_PER_SENTENCE == 0:
                options = [option]
                line = line.replace("[%s]" % option, "")  # remove fill word from sentence
                words_in_sentence = line.split()[1:]  # start from index 1 since 1st cell contains the question number
            elif i % OPTIONS_PER_SENTENCE == 4:
                options.append(option)
                best_option = get_best_option(options, words_in_sentence)
                predictions.append(best_option)
            else:
                options.append(option)
            i += 1
    return predictions


def verify_predictions(test_dataset_answers, predictions):
    good_predictions = 0
    with open(test_dataset_answers) as f:
        for i, line in enumerate(f):
            match = re.search('\[([\d\w\'\-,]+)\]', line)
            answer = match.group(1)
            if predictions[i] == answer:
                good_predictions += 1
    success_rate = good_predictions/len(predictions)
    return success_rate


def print_database_content(sample_size=1000):
    """print a sample of size `sample_size` from the database
    """
    keys = DATABASE.keys()
    for i in range(sample_size):
        print '%s: %s' % (keys[i], DATABASE[keys[i]])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file",
                      help="use FILE as input. If a directory is provided, every .txt file in the folder will be parsed")
    parser.add_option("-t", "--test_file", dest="test_file",
                      help="use TEST_FILE as test dataset to evaluate the result")
    (options, args) = parser.parse_args()
    if not options.file:
        sys.exit('Error, no file was specified. Use -f to specify the file.')
    if os.path.isdir(options.file):
        for root, dirs, files in os.walk(options.file):
            for f in files:
                if os.path.splitext(f)[1].lower() == '.txt':
                    print "processing %s..." % f
                    train(os.path.join(root, f))
        print "END OF TRAINING"
    elif os.path.isfile(options.file):
        train(options.file)
    else:
        sys.exit('Error, %s is not a valid file or directory.' % options.file)
    pickle.dump(DATABASE, open('database.pickle', 'w'))
    if options.test_file:
        predictions = get_predictions(options.test_file)
        test_dir, test_file = os.path.split(options.test_file)
        answer_file = os.path.join(test_dir, "answers_%s" % test_file)
        success_rate = verify_predictions(answer_file, predictions)
        print "success rate: %s" % success_rate