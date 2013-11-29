from optparse import OptionParser
import re
import string
import sys
from lib.stemming.porter2 import stem
import nltk
import os

def sentence_per_line(input_path, output_path):
    """takes an input file and outputs a file where each line contains one sentence
    
    - Seb: Also removes license talk

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """

    end_tag = "*END*" 
    has_seen_end_tag = False

    end_end_tag = "End of The Project Gutenberg Etext"

    sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    current_line = ""
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            if not has_seen_end_tag:
                if end_tag not in line:
                    continue
                else:
                    has_seen_end_tag = True
                    continue
            if end_end_tag in line:
                continue
            if not line.strip():  # remove empty lines
                continue

            sentences = sent_tokenizer.tokenize(line)
            if current_line:
                sentences[0] = current_line + " " + sentences[0].strip()
                current_line = ""
            for i in range(len(sentences)-1):
                out.write(sentences[i].strip() + '\n')
            if sentences[-1].strip()[-1] in ['.', '?', '!']:
                out.write(sentences[-1].strip() + '\n')
                current_line = ""
            else:
                if current_line:
                    current_line = current_line + " " + sentences[-1].strip()
                else:
                    current_line = sentences[-1].strip()


def remove_uppercase(input_path, output_path):
    """switch to lowercase letters the content of an input file and put the result in an output file

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            out.write(line.lower())


def remove_names(input_path, output_path):
    """replace proper names from an input file with the word 'John'

    Warning:
    Is very likely not to work well if any filter besides sentence_per_line is applied before this one

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            line = nltk.word_tokenize(line)
            tagged_line = nltk.pos_tag(line)
            line_names_removed = [word if tag not in ['NNP', 'NNPS', 'PRP', 'PRP$'] else 'John'
                                  for word, tag in tagged_line]
            line_names_removed = " ".join(line_names_removed)
            #tokenization caused words like won't/can't to be replaced by wo n't/ca n't,
            #the following line fixes it
            line_names_removed = re.sub(r"([\w]+) n't", r"\1n't", line_names_removed)
            out.write(line_names_removed+'\n')


def remove_determiner(input_path, output_path):
    """remove determiners from an input file and put the result in an output file

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            determiners = ['a', 'an', 'another', 'any', 'both', 'each', 'either', 'every', 'neither', 'that', 'the',
                           'these', 'this', 'those']
            line = [word for word in line.split() if word not in determiners]
            out.write(" ".join(line)+'\n')


def remove_numbers(input_path, output_path):
    """replace all numbers from an input file with a dummy number "7" and put the result in an output file

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            line = re.sub("[0-9]+", "7", line)
            out.write(line)


def remove_punctuation(input_path, output_path):
    """remove all punctuation from an input file and put the result in an output file

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            line = line.translate(None, string.punctuation)
            out.write(line)


def filter_stem(input_path, output_path):
    """filter every word so that only the stem remains

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            line = " ".join([stem(word) for word in line.split()])
            out.write(line+'\n')

PIPELINE = {'sentence_per_line': sentence_per_line, 'remove_uppercase': remove_uppercase, 'remove_names': remove_names,
            'remove_numbers': remove_numbers, 'remove_punctuation': remove_punctuation, 'filter_stem': filter_stem,
            'remove_determiner': remove_determiner}

if __name__ == "__main__":
    help_text = "This script allows preprocessing of datasets. Preprocessing operations are defined as filters.\n" \
                "Filters are independent, therefore you can apply any number of filters in any order you want.\n" \
                "Filters are passed as arguments to this script.\n" \
                "Supported filters are:\n" \
                "setence_per_line -- each line will contain a single sentence\n" \
                "remove_uppercase\n" \
                "remove_numbers -- replace each number with '7'\n" \
                "remove_punctuation\n" \
                "remove_names -- replace proper nouns and pronouns with word 'John'\n" \
                "remove_determiner\n" \
                "filter_stem -- reduce the words to their stem\n\n" \
                "Example usage: \npython preprocessing_pipeline.py -f input.txt sentence_per_line filter_stem"
    parser = OptionParser(usage=help_text)
    parser.add_option("-f", "--file", dest="file", help="use FILE as input")
    (options, args) = parser.parse_args()
    if not options.file:
        sys.exit('Error, no file was specified. Use -f to specify the file.')
    input_file = options.file

    all = False
    if input_file == "all":
        all = True

    if not all:
        for i, arg in enumerate(args):
            if arg not in PIPELINE:
                sys.exit('Error, %s is not a valid pipe name.' % arg)
            if i == 4:
                output_file = "%s_%s" % (options.file, "final.txt")
            else:
                output_file = "%s_%d" % (options.file, i)
            PIPELINE[arg](input_file, output_file)
            input_file = output_file
    else:
        filenames = os.listdir(".")
        for filename in filenames:
            if ".TXT" == filename[-4:]:
                print filename
                input_file = filename
                for i, arg in enumerate(args):
                    if arg not in PIPELINE:
                        sys.exit('Error, %s is not a valid pipe name.' % arg)
                    if i == len(args)-1:
                        output_file = "%s_%s" % ("zzz_"+filename, "final.txt")
                    else:
                        output_file = "%s_%d" % (filename, i)
                    PIPELINE[arg](input_file, output_file)
                    input_file = output_file