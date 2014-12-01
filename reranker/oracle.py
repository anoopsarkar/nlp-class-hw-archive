#!/usr/bin/env python
import optparse, sys, os
import bleu
from collections import namedtuple

translation_candidate = namedtuple("candidate", "sentence, scores, inverse_scores")
optparser = optparse.OptionParser()
optparser.add_option("-r", "--reference", dest="reference", default=os.path.join("data", "test.en"), help="English reference sentences")
optparser.add_option("-n", "--nbest", dest="nbest", default=os.path.join("data", "test.nbest"), help="N-best lists")
(opts,_) = optparser.parse_args()

ref = [line.strip().split() for line in open(opts.reference)]

nbests = []
for n, line in enumerate(open(opts.nbest)):
  (i, sentence, _) = line.strip().split("|||")
  (i, sentence) = (int(i), sentence.strip())
  if len(ref) <= i:
    break
  while len(nbests) <= i:
    nbests.append([])
  scores = tuple(bleu.bleu_stats(sentence.split(), ref[i]))
  inverse_scores = tuple([-x for x in scores])
  nbests[i].append(translation_candidate(sentence, scores, inverse_scores))
  if n % 2000 == 0:
    sys.stderr.write(".")

oracle = [nbest[0] for nbest in nbests]

stats = [0 for i in xrange(10)]
for candidate in oracle:
  stats = [sum(scores) for scores in zip(stats, candidate.scores)]

prev_score = 0
score = bleu.bleu(stats)

# greedy search for better oracle. For each sentence, choose the
# candidate translation that improves BLEU the most.
while score > prev_score:
  prev_score = score
  for i, nbest in enumerate(nbests): 
    for candidate in nbest:
      new_stats = [sum(scores) for scores in zip(stats, candidate.scores, oracle[i].inverse_scores)]
      new_score = bleu.bleu(new_stats)
      if new_score > score:
        score = new_score
        stats = new_stats
        oracle[i] = candidate

sys.stderr.write("\n")
for candidate in oracle:
  print candidate.sentence

