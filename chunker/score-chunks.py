from __future__ import division
import optparse, sys, codecs, re, logging
from collections import Counter, defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-t", "--testfile", dest="testfile", default=None, help="output from your chunker program")
optparser.add_option("-r", "--referencefile", dest="referencefile", default="reference", help="reference chunking")
optparser.add_option("-n", "--numfeatures", dest="numfeats", default=2, help="number of features, default is two: word and POS tag")
optparser.add_option("-c", "--conlleval", action="store_true", dest="conlleval", default=False, help="behave like the conlleval perl script with a single testfile input that includes the true label followed by the predicted label as the last two columns of input in testfile or sys.stdin")
optparser.add_option("-b", "--boundary", dest="boundary", default="-X-", help="boundary label that can be used to mark the end of a sentence")
optparser.add_option("-l", "--logfile", dest="logfile", default=None, help="log file name")
optparser.add_option("-o", "--outsidelabel", dest="outside", default="O", help="chunk tag for words outside any labeled chunk")
#optparser.add_option("-a", "--addrawtag", action="store_true", dest="raw", default=False, help="raw input: add B- as prefix to every token tag")
(opts, _) = optparser.parse_args()
numfeats = int(opts.numfeats)
if opts.logfile is not None:
    logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.INFO)

conlleval_error_msg = """
change number of features using -n, line does not have correct number of fields: expecting conlleval format, number of features:%d\n%s
"""

test_error_msg = """
change number of features using -n, line does not have correct number of fields: not expecting conlleval format, number of features:%d\n%s
"""

allChunks = '__ALL__'

def readTestFile(handle):
    contents = re.sub(r'\n\s*\n', r'\n\n', handle.read())
    contents = contents.rstrip()
    testContents = defaultdict(list)
    referenceContents = defaultdict(list)
    for (i,sentence) in enumerate(contents.split('\n\n')):
        for line in sentence.split('\n'):
            info = line.strip().split()
            if len(info) < 1:
                continue
            if info[0] == opts.boundary:
                if opts.conlleval:
                    info = [ opts.boundary, opts.boundary, opts.outside, opts.outside ]
                else:
                    info = [ opts.boundary, opts.boundary, opts.outside ]
            if opts.conlleval:
                if len(info) != numfeats + 2:
                    raise ValueError(conlleval_error_msg % (numfeats,line))
                testContents[i].append( (info[0], info[len(info)-1]) )
                referenceContents[i].append( (info[0], info[len(info)-2]) )
            else:
                if len(info) != int(opts.numfeats) + 1:
                    raise ValueError(test_error_msg % (numfeats,line))
                testContents[i].append( (info[0], info[len(info)-1]) )
        if len(testContents[i]) == 0:
            raise ValueError("zero length sentence found: %s" % (sentence))
        else:
            (lastWord, lastTag) = testContents[i][len(testContents[i])-1]
            if lastTag != 'O':
                if opts.conlleval:
                    testContents[i].append( (opts.boundary, 'O') )
                    referenceContents[i].append( (opts.boundary, 'O') )
                else:
                    testContents[i].append( (opts.boundary, 'O') )
    return (testContents, referenceContents)

def collectSpans(output):
    startChunk = { 
        'BB': True,
        'IB': True,
        'OB': True,
        'OI': True,
        'OE': True,
        'EE': True,
        'EI': True,
        '[': True,
        ']': True,
        }
    endChunk = { 
        'BB': True,
        'BO': True,
        'IB': True,
        'IO': True,
        'EE': True,
        'EI': True,
        'EO': True,
        '[': True,
        ']': True,
        } 
    prevChunkTag = ''
    prevChunkType = ''
    startIndex = 0
    endIndex = 0
    insideChunk = False
    spans = defaultdict(set)
    for (i, (word,label)) in enumerate(output):
        if label == 'O':
            endIndex = i
            if insideChunk:
                spans[allChunks].add( (startIndex, endIndex, prevChunkType) )
                spans[prevChunkType].add( (startIndex, endIndex) )
                logging.info("%d:%d:%s:%s" % (startIndex, endIndex, prevChunkType, output[startIndex:endIndex]))
            prevChunkTag = 'O'
            prevChunkType = 'O'
            startIndex = i
            insideChunk = False
            #spans[allChunks].add( (startIndex, endIndex+1, prevChunkType) )
            #spans[prevChunkType].add( (startIndex, endIndex+1) )
            logging.info("%d:%d:%s:%s" % (startIndex, endIndex+1, prevChunkType, output[startIndex:endIndex+1]))
        else:
            (chunkTag, chunkType) = label.split('-')
            if insideChunk and (prevChunkType != chunkType or prevChunkTag + chunkTag in endChunk):
                endIndex = i
                spans[allChunks].add( (startIndex, endIndex, prevChunkType) )
                spans[prevChunkType].add( (startIndex, endIndex) )
                logging.info("%d:%d:%s:%s" % (startIndex, endIndex, prevChunkType, output[startIndex:endIndex]))
                insideChunk = False
            if prevChunkType == '' or prevChunkType != chunkType or prevChunkTag + chunkTag in startChunk:
                startIndex = i
                endIndex = i
                insideChunk = True
            prevChunkTag = chunkTag
            prevChunkType = chunkType
        endIndex = i
    return spans

#def precision(reference, test):
#    if len(test) == 0:
#        return 0.
#    else:
#        logging.info("reference: %s" % reference)
#        logging.info("test: %s" % test)
#        logging.info("reference & test: %s" % (reference & test))
#        return float(len(reference & test)) / len(test)
#
#def recall(reference, test):
#    if len(reference) == 0:
#        return 0.
#    else:
#        return float(len(reference & test)) / len(reference)
#
#def fmeasure(reference, test, alpha=0.5):
#    p = precision(reference, test)
#    r = recall(reference, test)
#    if p == 0. or r == 0.:
#        return (0.,0.,0.)
#    return (p, r, (1.0/(alpha/p + (1-alpha)/r)))

if opts.testfile is None:
    (test, reference) = readTestFile(sys.stdin)
else:
    with open(opts.testfile) as f:
        (test, reference) = readTestFile(f)

if not opts.conlleval:
    with open(opts.referencefile) as f:
        (reference, _) = readTestFile(f)

if len(test.keys()) != len(reference.keys()):
    raise ValueError("Error: output and reference do not have identical number of lines")

def corpus_fmeasure(reference, test):
    sentScore = defaultdict(Counter)
    for (i,j) in zip(test.keys(), reference.keys()):
        testSpans = collectSpans(test[i])
        referenceSpans = collectSpans(reference[j]) 
        if allChunks not in testSpans:
            raise ValueError("could not find any spans in test data:\n%s" % (test[i]))
        if allChunks not in referenceSpans:
            raise ValueError("could not find any spans in reference data:\n%s" % (reference[j]))
        for key in testSpans.keys():
            intersection = referenceSpans[key] & testSpans[key]
            sentScore[key].update(correct=len(intersection), numGuessed=len(testSpans[key]), numCorrect=len(referenceSpans[key]))
    for key in sorted(sentScore.keys()):
        precision = sentScore[key]['correct']/sentScore[key]['numGuessed']
        recall = sentScore[key]['correct']/sentScore[key]['numCorrect']
        fmeasure = (2*precision*recall/(precision+recall))
        print "%17s: precision: %6.2f%% recall: %6.2f%% FB1: %6.2f" %  (key, precision*100., recall*100., fmeasure*100.)
    return fmeasure*100.

print "Overall Score: %.2f" % corpus_fmeasure(reference, test)

