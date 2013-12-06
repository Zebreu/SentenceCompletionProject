import os
import string
import re

def sentence_per_line(text):
    """takes an input file and outputs a file where each line contains one sentence

    - Seb: Also removes license talk

    Keyword arguments:
    text -- text to process
    """

    textOutput = ""
    end_tag = "*END*"
    has_seen_end_tag = False

    end_end_tag = "End of The Project Gutenberg Etext"

    current_line = ""
    for line in text:
        # print line
        if has_seen_end_tag:
            line = line.replace("?", ".")
            line = line.replace("!", ".")
            if '.' in line:
                line = line.split('.')
                line[-1] = line[-1].strip('\n\r')
                if current_line:
                    current_line += " " + line[0]
                else:
                    current_line = line[0]
                textOutput += current_line.strip() + '\n'
                for i in range(1, len(line) - 1):
                    textOutput += line[i].strip() + '\n'
                current_line = line[-1]
            elif end_end_tag in line:
                pass
            else:
                line = line.strip('\n\r')
                if current_line:
                    current_line += " " + line
                else:
                    current_line = line
        else:
            if end_tag in line:
                has_seen_end_tag = True

    return textOutput.split('\n')

def remove_determiner(text):
    """remove determiners from an input file and put the result in an output file

    Keyword arguments:
    text -- text to process
    """
    deterOutput = []
    for line in text:
        determiners = ['a', 'an', 'another', 'any', 'both', 'each', 'either', 'every', 'neither', 'that', 'the',
                       'these', 'this', 'those']
        line = [word for word in line.split() if word not in determiners]
        deterOutput.append(" ".join(line))
    return deterOutput


def remove_uppercase(text):
    """switch to lowercase letters the content of an input file and put the result in an output file

    Keyword arguments:
    text -- text to process
    """
    lowerOutput = []
    for line in text:
        lowerOutput.append(line.lower())
    return lowerOutput

def remove_numbers(text):
	numOutput = []
	for line in text:
		numOutput.append(re.sub("[0-9]+", "7", line))
	return numOutput

def remove_punctuation(text):
    """remove all punctuation from an input file and put the result in an output file

    Keyword arguments:
    text -- text to process
    """
    puncOutput = []
    for line in text:
        line = line.translate(string.maketrans("",""), string.punctuation)
        puncOutput.append(line)
    return puncOutput

def remove_spaces(text):
	spacesOutput = []
	for line in text:
		while(line.find("  ") != -1):
			line = line.replace("  ", " ")
		spacesOutput.append(line)
	return spacesOutput

def line_identifiers(text):
    identifiers = []
    for line in text:
        if len(line) >= 1:
            identifiers.append("<s> " + line + " </s>")
    return identifiers

if __name__ == "__main__":
    train_set = ""
    os.chdir("Holmes_Training_Data/")
    for novel in os.listdir("."):
        if novel != "preprocessed":
            with open(novel) as nov:
                print "preprocessing: ", nov.name
                train_set += '\n'.join(line_identifiers(remove_spaces(remove_determiner(remove_numbers(remove_punctuation(remove_uppercase(sentence_per_line(nov))))))))
    train_set = train_set.replace('\n', ' ')
    with open("preprocessed/train_set_deter.txt", 'w') as out:
		out.write(train_set)
        