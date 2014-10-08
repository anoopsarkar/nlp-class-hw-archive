#!/usr/bin/env python
import optparse, sys, os, logging

optparser = optparse.OptionParser()
optparser.add_option("-d", "--datadir", dest="datadir", default="data", help="data directory (default=data)")
optparser.add_option("-p", "--prefix", dest="fileprefix", default="hansards", help="prefix of parallel data files (default=hansards)")
optparser.add_option("-e", "--english", dest="english", default="en", help="suffix of English (target language) filename (default=en)")
optparser.add_option("-f", "--french", dest="french", default="fr", help="suffix of French (source language) filename (default=fr)")
optparser.add_option("-l", "--logfile", dest="logfile", default=None, help="filename for logging output (default=None)")
optparser.add_option("-i", "--inputfile", dest="inputfile", default=None, help="input alignments file (default=sys.stdin)")
(opts, args) = optparser.parse_args()
f_data = file("%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.french))
e_data = file("%s.%s" % (os.path.join(opts.datadir, opts.fileprefix), opts.english))
    
if opts.logfile:
    logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.INFO)

inp = sys.stdin if opts.inputfile is None else file(opts.inputfile)

for (n, (f, e, a)) in enumerate(zip(f_data, e_data, inp)):
  size_f = len(f.strip().split())
  size_e = len(e.strip().split())
  try: 
    alignment = set([tuple(map(int, x.split("-"))) for x in a.strip().split()])
    for (i,j) in alignment:
      if (i>=size_f or j>size_e):
        logging.warning("WARNING (%s): Sentence %d, point (%d,%d) is not a valid link\n" % (sys.argv[0],n,i,j))
      pass
  except (Exception):
    logging.error("ERROR (%s) line %d is not formatted correctly:\n  %s" % (sys.argv[0],n,a))
    logging.error("Lines can contain only tokens \"i-j\", where i and j are integer indexes into the French and English sentences, respectively.\n")
    sys.exit(1)
  sys.stdout.write(a)

warned = False
for a in inp: 
  if not warned:
    logging.warning("WARNING (%s): alignment file is longer than bitext\n" % sys.argv[0])
    warned = True
  sys.stdout.write(a)

try:
  if f_data.next():
    logging.warning("WARNING (%s): bitext is longer than alignment\n" % sys.argv[0])
except StopIteration:
  pass
  
