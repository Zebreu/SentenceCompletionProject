from optparse import OptionParser
import shelve
import string

DATABASE_PATH = 'non_continuous_n_gram'


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

    Train the n-gram using file `f` as input. The trained result will be stored in `DATABASE_PATH`.db
    """
    database = shelve.open(DATABASE_PATH)
    with open(dataset) as f:
        for line in f:
            line = line.split()
            combinations = generate_combinations(line)
            for combination in combinations:
                key = string.join(combination)
                if key in database:
                    database[key] += 1
                else:
                    database[key] = 1
    database.close()


def print_database_content(sample_size=1000):
    """print a sample of size `sample_size` from the database
    """
    database = shelve.open(DATABASE_PATH)
    keys = database.keys()
    for i in range(sample_size):
        print '%s: %s' % (keys[i], database[keys[i]])

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="file", help="use FILE as input")
    (options, args) = parser.parse_args()
    train(options.file)
    print_database_content(20)