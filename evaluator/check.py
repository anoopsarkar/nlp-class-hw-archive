#!/usr/bin/env python
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/hyp1-hyp2-ref", help="Input file (default data/train.hyp1-hyp2-ref)")
(opts, args) = optparser.parse_args()
input = open(opts.input)

for (n, (f_e_r, y)) in enumerate(zip(input, sys.stdin)):
  try:
    ny = int(y);
    if ny < -1 or ny > 1:
      sys.stderr.write("ERROR (%s): Sentence %d predicted judgment %d is invalid\n" % (sys.argv[0],n,ny))
      sys.exit(1)
    pass
  except (Exception):
    sys.stderr.write("ERROR (%s) line %d is not formatted correctly:\n  %s" % (sys.argv[0],n,y))
    sys.stderr.write("Lines can contain only tokens {0,1,-1}\n")
    sys.exit(1)
  sys.stdout.write(y)

warned = False
for y in (sys.stdin):
  if not warned:
    sys.stderr.write("WARNING (%s): prediction file is longer than input\n" % sys.argv[0])
    warned = True
  sys.stdout.write(y)

try:
  if (input.next()):
    sys.stderr.write("WARNING (%s): input is longer than prediction file\n" % sys.argv[0])
except (StopIteration):
  pass

