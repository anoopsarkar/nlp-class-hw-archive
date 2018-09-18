import sys

def check_sample(sentences, allowed_words):
    found_bad_words = False
    for words in map(lambda x: x.split(), sentences):
        bad_words = list(filter(lambda x: x not in allowed_words, words))
        if bad_words:
            print("#ERROR: the following words are not allowed: {}".format(bad_words), file=sys.stderr)
            found_bad_words = True
        else:
            print("{}".format(" ".join(words)))
    if not found_bad_words:
        print("#file only has allowed words", file=sys.stderr)

if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='count', default=0,
                           help="verbose output")
    argparser.add_argument("-i", "--samplefile", dest="sample_file", type=str,
                           default="sample.txt", help="sampled sentences")
    argparser.add_argument("-a", "--allowedwords", dest="allowed_words_file", type=str,
                           default="allowed_words.txt",
                           help="use this list of words to check sampled sentences")
    args = argparser.parse_args()
    allowed_words = set(line.strip() for line in open(args.allowed_words_file))
    sentences = set(line.strip() for line in open(args.sample_file))
    check_sample(sentences, allowed_words)
