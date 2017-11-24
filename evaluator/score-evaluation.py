#!/usr/bin/env python
import optparse
import sys

optparser = optparse.OptionParser()
optparser.add_option("-i", "--input", dest="input", default="data/hyp1-hyp2-ref", help="Input file (default data/train.hyp1-hyp2-ref)")
optparser.add_option("-t", "--truth", dest="truth", default="data/dev.answers", help="Human judgements (default=data/train.answers)")
(opts, args) = optparser.parse_args()

(right, wrong) = (0.0,0.0)
conf = [[0,0,0] for i in xrange(3)]
for (i, (f_e_r, sg, sy)) in enumerate(zip(open(opts.input), open(opts.truth), sys.stdin)):
  (g, y) = (int(sg), int(sy))
  conf[g + 1][y + 1] += 1
  if g == y:
    right += 1
  else:
    wrong += 1

acc = right / (right + wrong)

sys.stderr.write("\t  Pred. y=-1\ty=0\ty=1\n")
for (true_y, c) in enumerate(conf):
  sys.stderr.write("True y=%2d\t" % (true_y - 1))
  sys.stderr.write("%d\t%d\t%d\n" % tuple(c))
sys.stderr.write("\n")

sys.stdout.write("Accuracy = %f\n" % acc)
for _ in (sys.stdin): # avoid pipe error
  pass
