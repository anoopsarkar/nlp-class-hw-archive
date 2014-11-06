#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple

optparser = optparse.OptionParser()
optparser.add_option("-n", "--nbest", dest="nbest", default=os.path.join("data", "test.nbest"), help="N-best file")
optparser.add_option("-w", "--weight-file", dest="weights", default=None, help="Weight filename, or - for stdin (default=use uniform weights)")
(opts, _) = optparser.parse_args()

w = None
if opts.weights is not None:
  weights_file = sys.stdin if opts.weights is "-" else open(opts.weights)
  w = [float(line.strip()) for line in weights_file]

translation = namedtuple("translation", "english, score")
nbests = []
for line in open(opts.nbest):
  (i, sentence, features) = line.strip().split("|||")
  if len(nbests) <= int(i):
    nbests.append([])
  features = [float(h) for h in features.strip().split()]
  if w is None:
    w = [1.0/len(features) for _ in xrange(len(features))]
  nbests[int(i)].append(translation(sentence.strip(), sum([x*y for x,y in zip(w, features)])))

for nbest in nbests:
  print sorted(nbest, key=lambda x: -x.score)[0].english
