import sys, bz2
from collections import namedtuple

# # A language model scores sequences, and must account
# # for both beginning and end of each sequence. Example API usage:
# lm = models.LM(filename)
# sentence = "This is a test ."
# lm_state = lm.begin() # initial state is always <s>
# logprob = 0.0
# for t in sentence:
#   (lm_state, logprob) = lm.score(lm_state, t)
#   logprob += logprob
# logprob += lm.end(lm_state) # transition to </s>, can also use lm.score(lm_state, "</s>")[1]
ngram_stats = namedtuple("ngram_stats", "logprob, backoff")
class LM:
    def __init__(self, filename):
        sys.stderr.write("Reading language model from %s...\n" % (filename,))
        self.table = {}
        for line in bz2.open(filename, 'rt'):
            entry = line.strip().split("\t")
            if len(entry) > 1 and entry[0] != "ngram":
                (logprob, ngram, backoff) = (float(entry[0]), tuple(entry[1].split()), float(entry[2] if len(entry)==3 else 0.0))
                self.table[ngram] = ngram_stats(logprob, backoff)

    def begin(self):
        return ("<s>",)

    def score(self, state, token):
        ngram = state + (token,)
        score = 0.0
        while len(ngram)> 0:
            if ngram in self.table:
                # Below, use -5 for a 6-gram LM and -2 for a trigram LM, etc.
                return (ngram[-5:], score + self.table[ngram].logprob)
            else: #backoff
                score += self.table[ngram[:-1]].backoff if len(ngram) > 1 else 0.0 
                ngram = ngram[1:]
        return ((), score - 99.0) # bad score for missing unigrams
    
    def end(self, state):
        return self.score(state, "</s>")[1]

if __name__ == '__main__':
    import sys, string

    def maybe_write(s):
        if True:
            print(s, file=sys.stderr)

    sequence = 'In a few cases, a multilingual artifact has been necessary to facilitate decipherment, the Rosetta Stone being the classic example. Statistical techniques provide another pathway to decipherment, as does the analysis of modern languages derived from ancient languages in which undeciphered texts are written. Archaeological and historical information is helpful in verifying hypothesized decipherments.'.translate(dict.fromkeys(map(ord, string.punctuation + ' '), None)).lower()
    print(sequence)
    #sequence = 'jasbklfhjasjkldhf'
    #sequence = 'this is the text.'

    lm = LM("6-gram-wiki-char.lm.bz2")
    lm_state = lm.begin()
    lm_logprob = 0.0 
    for token in list(sequence):
        maybe_write("state: {}".format(lm_state + (token,)))
        (lm_state, logprob) = lm.score(lm_state, token)
        lm_logprob += logprob
        maybe_write("logprob={}".format(logprob))
    lm_logprob += lm.end(lm_state)
    print("TOTAL LM LOGPROB: {}\n".format(lm_logprob), file=sys.stderr)


