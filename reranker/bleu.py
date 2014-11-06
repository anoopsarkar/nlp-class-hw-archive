import math
from collections import Counter

# Collect BLEU-relevant statistics for a single sentence/reference pair.
# Return value is a generator yielding:
# (c, r, numerator1, denominator1, ... numerator4, denominator4)
# Summing the columns across calls to this function on an entire corpus will
# produce a vector of statistics that can be used to compute BLEU (below)
def bleu_stats(sentence, reference):
  yield len(sentence)
  yield len(reference)
  for n in xrange(1,5):
    s_ngrams = Counter([tuple(sentence[i:i+n]) for i in xrange(len(sentence)+1-n)])
    r_ngrams = Counter([tuple(reference[i:i+n]) for i in xrange(len(reference)+1-n)])
    yield max([sum((s_ngrams & r_ngrams).values()), 0])
    yield max([len(sentence)+1-n, 0])

# Compute BLEU from collected statistics obtained by call(s) to bleu_stats
def bleu(stats):
  if len(filter(lambda x: x==0, stats)) > 0:
    return 0
  (c, r) = stats[:2]
  bleu_prec = sum([math.log(float(x)/y) for x,y in zip(stats[2::2],stats[3::2])])
  return math.exp(min([0, 1-float(r)/c]) + 0.25 * bleu_prec)

# A modification of BLEU that returns a positive value even when some 
# higher-order precisions are zero. From Liang et al. 2006 (Footnote 5):
# http://aclweb.org/anthology-new/P/P06/P06-1096.pdf
def smoothed_bleu(stats):
  return sum([bleu(stats[:2+2*i])/math.pow(2,4-i+1) for i in xrange(1,5)])
