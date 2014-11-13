#!/usr/bin/env python
import optparse, sys, os
import bleu

optparser = optparse.OptionParser()
optparser.add_option("-r", "--reference", dest="reference", default=os.path.join("data", "test.en"), help="English reference sentences")
(opts,_) = optparser.parse_args()

ref = [line.strip().split() for line in open(opts.reference)]
system = [line.strip().split() for line in sys.stdin]

stats = [0 for i in xrange(10)]
for (r,s) in zip(ref, system):
  stats = [sum(scores) for scores in zip(stats, bleu.bleu_stats(s,r))]
print bleu.bleu(stats)
