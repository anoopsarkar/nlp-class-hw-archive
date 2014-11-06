#!/usr/bin/env python
import optparse, sys, os
from collections import namedtuple

optparser = optparse.OptionParser()
optparser.add_option("-n", "--nbest", dest="nbest", default=os.path.join("data", "train.nbest"), help="N-best file")
(opts, _) = optparser.parse_args()

for line in open(opts.nbest):
  (i, sentence, features) = line.strip().split("|||")
  features = [float(h) for h in features.strip().split()]
  w = [1.0/len(features) for _ in xrange(len(features))]
  break

print "\n".join([str(weight) for weight in w])
