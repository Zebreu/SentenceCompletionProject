from optparse import OptionParser
import re
import string
import sys
from lib.stemming.porter2 import stem

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

    current_line = ""
    with open(input_path) as inp, open(output_path, 'w') as out:

        for line in inp:
            if has_seen_end_tag:
                line = line.replace("?",".")
                line = line.replace("!",".")
                if '.' in line:
                    line = line.split('.')
                    line[-1] = line[-1].strip('\n')
                    if current_line:
                        current_line += " " + line[0]
                    else:
                        current_line = line[0]
                    out.write(current_line.strip() + '\n')
                    for i in range(1, len(line)-1):
                        out.write(line[i].strip() + '\n')
                    current_line = line[-1]
                elif end_end_tag in line:
                    pass
                else:
                    line = line.strip('\n')
                    if current_line:
                        current_line += " " + line
                    else:
                        current_line = line
            else:
                if end_tag in line:
                    has_seen_end_tag = True

def remove_uppercase(input_path, output_path):
    """switch to lowercase letters the content of an input file and put the result in an output file

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    with open(input_path) as inp, open(output_path, 'w') as out:
        for line in inp:
            out.write(line.lower())


def remove_names(input_path, output_path):  # TODO
    pass


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
            'remove_numbers': remove_numbers, 'remove_punctuation': remove_punctuation, 'filter_stem': filter_stem}

if __name__ == "__main__":
    help_text = "This script allows preprocessing of datasets. Preprocessing operations are defined as filters.\n" \
                "Filters are independent, therefore you can apply any number of filters in any order you want.\n" \
                "Filters are passed as arguments to this script.\n" \
                "Supported filters are:\n" \
                "setence_per_line -- each line will contain a single sentence\n" \
                "remove_uppercase\n" \
                "remove_numbers -- replace each number with '7'\n" \
                "remove_punctuation\n" \
                "filter_stem -- reduce the words to their stem\n\n" \
                "Example usage: \npython preprocessing_pipeline.py -f input.txt sentence_per_line remove_numbers  filter_stem"
    parser = OptionParser(usage=help_text)
    parser.add_option("-f", "--file", dest="file", help="use FILE as input")
    (options, args) = parser.parse_args()
    if not options.file:
        sys.exit('Error, no file was specified. Use -f to specify the file.')
    input_file = options.file
    for i, arg in enumerate(args):
        if arg not in PIPELINE:
            sys.exit('Error, %s is not a valid pipe name.' % arg)
        output_file = "%s_%d" % (options.file, i)
        PIPELINE[arg](input_file, output_file)
        input_file = output_file