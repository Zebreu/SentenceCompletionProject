import os
import string
import re
from stemming.porter2 import stem
import nltk

def sentence_per_line(text):
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
    textOutput = ""

    for line in text:
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

        line = line.replace("Mr.","")
        line = line.replace("Mrs.","")
        line = line.replace("Dr.","")
        sentences = sent_tokenizer.tokenize(line)
        if current_line:
            sentences[0] = current_line + " " + sentences[0].strip()
            current_line = ""
        for i in range(len(sentences)-1):
            textOutput += sentences[i].strip() + '\n'
        if sentences[-1].strip()[-1] in ['.', '?', '!']:
            textOutput += sentences[-1].strip() + '\n'
            current_line = ""
        else:
            if current_line:
                current_line = current_line + " " + sentences[-1].strip()
            else:
                current_line = sentences[-1].strip()

    return textOutput.split('\n')

def remove_determiner(text):
    """remove determiners from an input file and put the result in an output file

    Keyword arguments:
    text -- text to process
    """
    deterOutput = []
    for line in text:
        determiners = ["a","able","about","across","after","all",
                        "almost","also","am","among","an","and","any","are",
                        "as","at","be","because","been","but","by","can","cannot",
                        "could","dear","did","do","does","either","else","ever",
                        "every","for","from","get","got","had","has","have","he",
                        "her","him","his","how","however","i","if","in",
                        "into","is","it","its","just","least","let","like",
                        "may","me","might","most","must","my","neither",
                        "no","nor","not","of","off","often","on","only","or",
                        "other","our","own","rather","said","say","says","she",
                        "should","since","so","some","than","that","the","their",
                        "them","then","there","these","they","this","tis","to",
                        "too","twas","us","was","we","were","what","when",
                        "where","which","while","who","whom","why","will","with",
                        "would","yet","you","your"]
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

def remove_names(text):
    """replace proper names from an input file with the word 'John'

    Warning:
    Apply sentence_per_line and remove_determiner and remove_numbers before this one (and only those two), otherwise bad things will happen

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    names = []
    for line in text:
        words = line.split(" ")
        words[-1] = words[-1].replace("\n","")
        words = [word.strip() for word in words]
        line_names_removed = []
        for i,word in enumerate(words):
            if i == 0:
                line_names_removed.append(word)
                #Too aggressive right now
            elif word == "7":
                line_names_removed.append(word)
            elif word[0].islower():
                line_names_removed.append(word)
            else:
                line_names_removed.append("John")
        line_names_removed = " ".join(line_names_removed)
        names.append(line_names_removed)
    return names

def filter_stem(text):
    """filter every word so that only the stem remains

    Keyword arguments:
    input_path -- input file path
    output_path -- output file path
    """
    stems = []
    for line in text:
        line = " ".join([stem(word) for word in line.split()])
        stems.append(line)
    return stems

def preprocess(text, isTexts):
    if isTexts:
        textPreprocessed = line_identifiers(remove_spaces(filter_stem(remove_names(remove_numbers(remove_determiner(remove_punctuation(remove_uppercase(sentence_per_line(text)))))))))
    else:
        textPreprocessed = line_identifiers(remove_spaces(filter_stem(remove_names(remove_numbers(remove_determiner(remove_punctuation(remove_uppercase(text))))))))
    return textPreprocessed

if __name__ == "__main__":
    train_set = ""
    originalPath = os.getcwd()
    os.chdir("Holmes_Training_Data/")
    for novel in os.listdir("."):
        with open(novel) as nov:
            print "preprocessing: ", nov.name
            textPrepro = preprocess(nov, True)
            train_set += '\n'.join(textPrepro)
    train_set = train_set.replace('\n', ' ')
    os.chdir(originalPath)
    with open("preprocessed/train_set.txt", 'w') as out:
		out.write(train_set)

    with open("Holmes.lm_format.questions.txt", 'r') as questions, open("preprocessed/questions.txt", 'w') as out:
        out.write('\n'.join(preprocess(questions.read().replace("<s> ", "").replace(" </s>", "").split('\n'), False)))
    with open("Holmes.lm_format.answers.txt", 'r') as answers, open("preprocessed/answers.txt", 'w') as out:
        out.write('\n'.join(preprocess(answers.read().replace("<s> ", "").replace(" </s>", "").split('\n'), False)))
        