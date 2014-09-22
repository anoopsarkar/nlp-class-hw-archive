from __future__ import division
import optparse, sys, codecs
from collections import defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-t", "--testfile", dest="testfile", default=None, help="Output from your segmenter program")
optparser.add_option("-r", "--referencefile", dest="referencefile", default="data/reference", help="Reference segmentation")
(opts, _) = optparser.parse_args()

if opts.testfile is None:
    test = list(sys.stdin)
else:
    with open(opts.testfile) as f:
        test = list(f)
with open(opts.referencefile) as f:
    reference = list(f)

if len(test) != len(reference):
    raise ValueError("Error: output and reference do not have identical number of lines")
