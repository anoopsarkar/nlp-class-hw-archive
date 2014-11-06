#!/usr/bin/env python
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/test.nbest", help="Data filename prefix (default=data)")
(opts, _) = optparser.parse_args()

nbests = []
for line in open(opts.input):
  (i, sentence, _) = line.strip().split("|||")
  if len(nbests) <= int(i):
    nbests.append(set())
  nbests[int(i)].add(sentence.strip())

translations = [line.strip() for line in sys.stdin]

if len(nbests) != len(translations):
  print "Error: file contains %d translations. Expected %d." % (len(translations), len(nbests))
  sys.exit(1)

for i, (translation, nbest) in enumerate(zip(translations, nbests)):
  if translation not in nbest:
    print "Error: the translation of sentence %d is not in the n-best list:\n  %s\n" % (i, translation)
    sys.exit(1)
