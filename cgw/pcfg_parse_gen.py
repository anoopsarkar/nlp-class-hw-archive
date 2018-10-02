# Author: Anoop Sarkar <anoop _at_ sfu.ca>
# Do not distribute this code to anybody
# without permission from the author

# pylint: disable=C0301,C0111,C0103,C0325
# pylint: disable=R1702,R0912,R0902,R0913,R0914,R0915

import sys
import math
import random
from operator import itemgetter

# class Unseen: provides lexical rules for unseen words
#
class Unseen:

    # list of part of speech tags for unseen words

    def __init__(self, filename):
        self.postags = None
        self.total = None
        self.most_likely_tag = None
        self.total = 0
        self.postags = {}
        for _line in open(filename, 'r'):
            _line = _line[:-1]
            (count, tag) = _line.split()
            if tag in self.postags:
                raise ValueError("each postag should occur exactly once")
            self.postags[tag] = int(count)
            self.total += int(count)
        self.compute_log_prob()

    def compute_log_prob(self):
        for tag in self.postags:
            self.postags[tag] = math.log(self.postags[tag] / self.total, 2)

    def tags_for_unseen(self):
        for tag in self.postags:
            yield (tag, self.postags[tag])

    def get_most_likely_tag(self):
        if self.most_likely_tag is None:
            (self.most_likely_tag, _) = sorted(self.postags.items(),
                                               key=itemgetter(1)).pop()
        return self.most_likely_tag

# end of class Unseen

# class Pcfg:
# Implements a non-strict Chomsky Normal Form probabilitic context free grammar
# can have rules of the form A -> B C, A -> B (hence non-strict), or A -> a
# A, B, C are non-terminals, a are terminals
#
# Format of the file for a rule lhs -> left right with its count is:
# count lhs left [right]
# the log_prob for each rule is computed on demand
#
class Pcfg:

    # read in the file containing the weighted context-free grammar
    # the prob for each rule is computed on the fly based on the weights
    # normalized by the lhs symbol as per the usual definition of PCFGs
    def __init__(self, filelist, startsym='TOP', allowed_words_file='allowed_words.txt', verbose=0):
        self.startsym = startsym
        self.allowed_words = set(line.strip() for line in open(allowed_words_file))
        self.verbose = verbose
        self.last_rule = -1
        # each rule is indexed by a number i, where
        # rule[i] = (lhs, (left, right), count, log_prob)
        self.rules = {}

        # forward index from lhs to list of rule numbers
        self.lhs_rules = {}

        # reverse index from (left,right) to a rule index
        self.rhs = {}

        # total count over all rhs for each lhs in the pcfg
        self.lhs_count = {}
        self.lhs_total_count = 0

        # special symbol to mark a unary rule A -> B which is written as A -> B <Unary>
        self.unary = '<Unary>'

        for filename in filelist:
            print("#reading grammar file: {}".format(filename), file=sys.stderr)
            linenum = 0
            for _line in open(filename, 'r'):
                linenum += 1
                if _line.find('#') != -1:
                    _line = _line[:_line.find('#')] # strip comments
                _line = _line.strip()
                if _line == "":
                    continue
                f = _line.split()
                if len(f) > 4:
                    # only CNF rules allowed
                    raise ValueError("Error: >2 symbols in right hand side at line %d: %s"
                                     % (linenum, ' '.join(f)))
                if len(f) < 3:
                    # empty rules not allowed
                    raise ValueError("Error: unexpected line at line %d: %s"
                                     % (linenum, ' '.join(f)))
                # count lhs left [right]
                try:
                    count = int(f[0])
                except ValueError:
                    raise ValueError("Rule must be COUNT LHS RHS. Found {}".format(" ".join(f)))
                (count, lhs, left) = (count, f[1], f[2])
                if len(f) < 4:
                    right = self.unary
                else:
                    right = f[3]
                if lhs == left and right == self.unary:
                    print("#Ignored cycle {} -> {}".format(lhs, left), file=sys.stderr)
                    continue
                self.last_rule += 1
                self.rules[self.last_rule] = (lhs, (left, right), count, None)

                if self.verbose > 1:
                    print("Rule: {}".format(self.rules[self.last_rule]), file=sys.stderr)

                if lhs in self.lhs_rules:
                    self.lhs_rules[lhs].append(self.last_rule)
                else:
                    self.lhs_rules[lhs] = [self.last_rule]

                if (left, right) in self.rhs:
                    self.rhs[left, right].append(self.last_rule)
                else:
                    self.rhs[left, right] = [self.last_rule]

                if lhs in self.lhs_count:
                    self.lhs_count[lhs] += count
                else:
                    self.lhs_count[lhs] = count
                self.lhs_total_count += count

    # computes the log_prob of a rule using the counts collected for each lhs
    # it caches the value into the rules table after computing the probabiilty
    # for each rule
    def get_log_prob(self, rule_number):
        if rule_number in self.rules:
            (lhs, rhs, count, log_prob) = self.rules[rule_number]
            if log_prob is not None:
                return log_prob
            log_prob = math.log(count / self.lhs_count[lhs], 2)
            self.rules[rule_number] = (lhs, rhs, count, log_prob)
        else:
            raise ValueError("rule number %d not found" % rule_number)
        return log_prob

    def get_rule(self, rule_number):
        log_prob = self.get_log_prob(rule_number)
        if log_prob is None:
            raise ValueError("rule has no log_prob: {}".format(self.rules[rule_number]))
        return self.rules[rule_number]

    def rule_iterator(self, left, right):
        if (left, right) in self.rhs:
            for rule_number in self.rhs[left, right]:
                yield rule_number
        else:
            return

    # returns the prior probability of a nonTerminal
    def get_prior(self, lhs):
        if lhs in self.lhs_count:
            return math.log(self.lhs_count[lhs] / self.lhs_total_count, 2)
        raise ValueError("%s: missing lhs" % lhs)

    def __str__(self):
        output = ""
        for _i in range(0, self.last_rule+1):
            log_prob = self.get_log_prob(_i)
            (lhs, (left, right), count, log_prob) = self.rules[_i]
            output += " ".join([lhs, left, right, str(count), str(log_prob), "\n"])
        for _i in self.lhs_count:
            if self.verbose:
                print("#Prior: {} {}".format(_i, self.get_prior(_i)), file=sys.stderr)
        return output

# end of class Pcfg

# class PcfgGenerator contains the functions that allow sampling
# of derivations from a PCFG. The output can be either the strings
# or the trees.
#
# There is a small chance that the generator function will not
# terminate. To make sure this outcome is avoided we use a limit
# on how unlikely the generated derivation should be. If during
# generation we go below this limit on the probability we stop
# and restart the generation process.
class PcfgGenerator:

    def __init__(self, _gram, verbose=0, limit=1e-300):
        self.gram = None # PCFG to be used by the generator
        self.verbose = verbose
        self.restart_limit = None # can be set using the constructor
        self.restart_limit = limit
        self.gram = _gram
        # num_samples is the number of sampled words from allowed_words
        # if the grammar produces entirely invalid sentence
        self.num_samples = 1
        random.seed()

    def flatten_tree(self, tree):
        sentence = []
        if isinstance(tree, tuple):
            (_, left_tree, right_tree) = tree
            for n in (self.flatten_tree(left_tree), self.flatten_tree(right_tree)):
                sentence.extend(n)
        else:
            if tree is not self.gram.unary:
                sentence = [tree]
        return sentence

    def check_allowed(self, sentence):
        if not sentence:
            print("ERROR: sampled sentence is empty", file=sys.stderr)
            return random.sample(self.gram.allowed_words, self.num_samples)
        new_sentence = []
        for w in sentence:
            if w not in self.gram.allowed_words:
                print("ERROR: word {} was sampled but is not allowed".format(w), file=sys.stderr)
                new_sentence.append(random.sample(self.gram.allowed_words, 1)[0])
            else:
                new_sentence.append(w)
        assert(len(new_sentence) == len(sentence))
        return new_sentence

    def generate(self, parsetree=False):
        try:
            rule = self.gen_pick_one(self.gram.startsym)
        except ValueError:
            return random.sample(self.gram.allowed_words, self.num_samples)
        if self.verbose:
            print("#getrule: {}".format(self.gram.get_rule(rule)), file=sys.stderr)
        try:
            gen_tree = self.gen_from_rule(rule)
        except ValueError:
            return random.sample(self.gram.allowed_words, self.num_samples)
        return gen_tree if parsetree else self.check_allowed(self.flatten_tree(gen_tree))

    def gen_pick_one(self, lhs):
        r = random.random()
        if self.verbose:
            print("#random number: {}".format(r), file=sys.stderr)
        output_log_prob = math.log(r, 2)
        accumulator = 0.0
        rule_picked = None
        for r in self.gram.lhs_rules[lhs]:
            if self.verbose:
                print("#getrule: {}".format(self.gram.get_rule(r)), file=sys.stderr)
            log_prob = self.gram.get_log_prob(r)
            # convert to prob from log_prob in order to add with accumulator
            prob = math.pow(2, log_prob)
            if output_log_prob < math.log(prob + accumulator, 2):
                rule_picked = r
                break
            else:
                accumulator += prob
        if rule_picked is None:
            raise ValueError("no rule found for %s" % lhs)
        if self.verbose:
            print("#picked rule %d: %s" % (rule_picked, self.gram.rules[rule_picked]), file=sys.stderr)
        return rule_picked

    def get_yield(self, sym):
        return sym if sym not in self.gram.lhs_rules else self.gen_from_rule(self.gen_pick_one(sym))

    def gen_from_rule(self, rule_number):
        (lhs, (left, right), _, _) = self.gram.rules[rule_number]
        if self.verbose:
            print("#%s -> %s %s" % (lhs, left, right), file=sys.stderr)
        left_tree = self.get_yield(left)
        right_tree = self.gram.unary if right is self.gram.unary else self.get_yield(right)
        return (lhs, left_tree, right_tree)

# class CkyParse contains the main parsing routines
# including routines for printing out the best tree and pruning
#
class CkyParse:

    def __init__(self, _gram, verbose=0, use_prior=True, use_pruning=True, beamsize=0.0001, unseen_file="unseen.tags"):
        self.gram = _gram # PCFG to be used by the grammar
        self.verbose = verbose
        if unseen_file != "":
            self.unseen = Unseen(unseen_file)
        else:
            self.unseen = None
        self.use_prior = use_prior
        self.use_pruning = use_pruning
        self.beam = math.log(float(beamsize), 2)
        self.chart = None # chart data structure to be used by the parser
        self._NINF = float('1e-323') # 64 bit double underflows for math.log(1e-324)
        self._LOG_NINF = math.log(self._NINF, 2)

    def prune(self, i, j):
        if not self.use_pruning:
            return 0
        num_pruned = 0
        if (i, j) in self.chart:
            tbl = self.chart[i, j]
            max_log_prob = self._LOG_NINF
            best_lhs = None

            for lhs in tbl.keys():
                (log_prob, back_pointer) = tbl[lhs]
                max_log_prob = max(log_prob, max_log_prob)
                if max_log_prob == log_prob:
                    best_lhs = lhs

            new_table = {}
            if self.use_prior:
                lowest = max_log_prob + self.beam + self.gram.get_prior(best_lhs)
            else:
                lowest = max_log_prob + self.beam
            for lhs in tbl.keys():
                (log_prob, back_pointer) = tbl[lhs]
                save_log_prob = log_prob
                if self.use_prior:
                    log_prob += self.gram.get_prior(lhs)
                if log_prob < lowest:
                    if self.verbose:
                        print("#pruning: {} {} {} {} {}".format(i, j, lhs, log_prob, lowest),
                              file=sys.stderr)
                    num_pruned += 1
                    continue
                new_table[lhs] = (save_log_prob, back_pointer)
            self.chart[i, j] = new_table
        return num_pruned

    def insert(self, i, j, lhs, log_prob, back_pointer):
        if (i, j) in self.chart:
            if lhs in self.chart[i, j]:
                prev_log_prob = self.chart_get_log_prob(i, j, lhs)
                if log_prob < prev_log_prob:
                    return False
        else:
            self.chart[i, j] = {}
        self.chart[i, j][lhs] = (log_prob, back_pointer)
        if self.verbose:
            print("#inserted: {} {} {} {}".format(i, j, lhs, log_prob), file=sys.stderr)
        return True

    def handle_unary_rules(self, i, j):
        # we have to allow for the fact that B -> C might lead
        # to another rule A -> B for the same span
        unary_list = [entry for entry in self.chart_entry(i, j)]
        for rhs in unary_list:
            rhs_log_prob = self.chart_get_log_prob(i, j, rhs)
            for rule_number in self.gram.rule_iterator(rhs, self.gram.unary):
                (lhs, _, _, log_prob) = self.gram.get_rule(rule_number)
                # rhs == left
                if lhs == rhs:
                    raise ValueError("Found a cycle", lhs, "->", rhs)
                back_pointer = (-1, rhs, self.gram.unary)
                if self.verbose:
                    print("log_prob: {} rhs_log_prob: {}".format(log_prob, rhs_log_prob), file=sys.stderr)
                if self.insert(i, j, lhs, log_prob + rhs_log_prob, back_pointer):
                    unary_list.append(lhs)

    def chart_entry(self, i, j):
        if (i, j) in self.chart:
            for item in self.chart[i, j].keys():
                yield item
        else:
            return

    def chart_get_log_prob(self, i, j, lhs):
        if (i, j) in self.chart:
            # Each entry in the chart for i, j is a hash table with key lhs
            # and value equals the tuple (log_prob, back_pointer)
            # This function returns the first element of the tuple
            return self.chart[i, j][lhs][0]
        raise ValueError("Could not find {}, {} in chart".format(i, j))

    def parse(self, input_sent):
        # chart has max size len(input_sent)*len(input_sent)
        # each entry in the chart is a hashtable with
        # key=lhs and value=(log_prob, back_pointer)
        self.chart = {}
        num_pruned = 0

        # insert all rules of type NonTerminal -> terminal
        # where terminal matches some word in the input_sent
        for (i, word) in enumerate(input_sent):
            j = i+1
            if (word, self.gram.unary) in self.gram.rhs:
                for rule_number in self.gram.rhs[(word, self.gram.unary)]:
                    (lhs, _, _, log_prob) = self.gram.get_rule(rule_number)
                    self.insert(i, j, lhs, log_prob, None)
            else:
                print("#using unseen part of speech for {}".format(word), file=sys.stderr)
                if self.unseen is None:
                    raise ValueError("cannot find terminal symbol", word)
                else:
                    for (tag, log_prob) in self.unseen.tags_for_unseen():
                        self.insert(i, j, tag, log_prob, None)
            self.handle_unary_rules(i, j)

        # do not prune lexical rules
        # recursively insert nonterminal lhs
        # for rule lhs -> left right into chart[(i, j)]
        # if left belongs to the chart for span i,k
        # and right belongs to the chart for span k, j
        N = len(input_sent)+1
        for j in range(2, N):
            for i in range(j-2, -1, -1):
                # handle the case for the binary branching rules lhs -> left right
                for k in range(i+1, j):
                    # handle the unary rules lhs -> rhs
                    for left in self.chart_entry(i, k):
                        for right in self.chart_entry(k, j):
                            left_log_prob = self.chart_get_log_prob(i, k, left)
                            right_log_prob = self.chart_get_log_prob(k, j, right)
                            for rule_number in self.gram.rule_iterator(left, right):
                                (lhs, _, _, log_prob) = self.gram.get_rule(rule_number)
                                back_pointer = (k, left, right)
                                self.insert(i, j, lhs,
                                            log_prob + left_log_prob + right_log_prob,
                                            back_pointer)
                # handle the unary rules lhs -> rhs
                self.handle_unary_rules(i, j)
                # prune each span
                num_pruned += self.prune(i, j)
        if self.verbose:
            print("#number of items pruned: {}".format(num_pruned), file=sys.stderr)

        sent_log_prob = self._LOG_NINF
        N = len(input_sent)
        if (0, N) in self.chart:
            if self.gram.startsym in self.chart[0, N]:
                (sent_log_prob, back_pointer) = self.chart[0, N][self.gram.startsym]
        if self.verbose:
            print("#sentence log prob = {}".format(sent_log_prob), file=sys.stderr)
        return sent_log_prob

    # default_tree provides a parse tree for input_sent w0,..,wN-1 when
    # the parser is unable to find a valid parse (no start symbol in
    # span 0, N). The default parse is simply the start symbol with
    # N children:
    # (TOP (P0 w0) (P1 w1) ... (PN-1 wN-1))
    # where Pi is the most likely part of speech tag for that word
    # from training data.
    # If the word is unknown it receives the most likely tag from
    # training (across all words).
    # if the Unseen class does not return a tag default_tree uses
    # a default part of speech tag X.
    def default_tree(self, input_sent):
        tag = "X" if self.unseen is None else self.unseen.get_most_likely_tag()
        taggedInput = map(lambda z: "(" + tag + " " + z + ")", input_sent)
        return "(" + self.gram.startsym + " " + " ".join(taggedInput) + ")"

    # best_tree returns the most likely parse
    # if there was a parse there must be a start symbol S in span 0, N
    # then the best parse looks like (S (A ...) (B ...)) for some
    # A in span 0,k and B in span k,N; the function extract_best_tree
    # recursively fills in the trees under the start symbol S
    def best_tree(self, input_sent):
        N = len(input_sent)
        startsym = self.gram.startsym
        if (0, N) in self.chart:
            if startsym in self.chart[0, N]:
                return self.extract_best_tree(input_sent, 0, N, startsym)
        print("#No parses found for: {}".format(" ".join(input_sent)), file=sys.stderr)
        return self.default_tree(input_sent)

    # extract_best_tree uses back_pointers to recursively find the
    # best parse top-down:
    # for each span i, j and non-terminal A (sym below), the parsing
    # algorithm has recorded the best path to that non-terminal A
    # using the back_pointer (k, left_sym, right_sym) which means
    # there is a rule A -> left_sym right_sym and that left_sym spans
    # i,k and right_sym spans k, j. Recursively calling extract_best_tree
    # on spans i,k,left_sym and k, j, right_sym will provide the necessary
    # parts to fill in the dotted parts in the tree:
    # (A (left_sym ...) (right_sym ...))
    # the parser records k == -1 when it inserts a unary rule:
    # A -> left_sym <Unary>
    # so a single recursive call to extract_best_tree fills in the
    # dotted parts of the tree:
    # (A (left_sym ...))
    def extract_best_tree(self, input_sent, i, j, sym):
        if (i, j) in self.chart:
            if sym in self.chart[i, j]:
                (_, back_pointer) = self.chart[i, j][sym]
                if back_pointer is None:
                    return "(" + sym + " " + input_sent[i] + ")"
                (k, left_sym, right_sym) = back_pointer
                if k == -1:
                    # unary rule
                    left_tree = self.extract_best_tree(input_sent, i, j, left_sym)
                    right_tree = ""
                else:
                    # binary rule
                    left_tree = self.extract_best_tree(input_sent, i, k, left_sym)
                    right_tree = self.extract_best_tree(input_sent, k, j, right_sym)
                return "(" + sym + " " + left_tree + " " + right_tree + ")"
        raise ValueError("cannot find span:", i, j, sym)

    def parse_sentences(self, sentences):
        corpus_cross_entropy = self._LOG_NINF
        corpus_len = 0
        total_log_prob = None
        parses = []
        for sent in sentences:
            sent = sent.strip()
            input_sent = sent.split()
            length = len(input_sent)
            if length <= 0:
                continue
            if sent[0] == '#':
                if self.verbose:
                    print("#skipping comment line in input_sent: {}".format(sent), file=sys.stderr)
                continue
            corpus_len += length
            print("#parsing: {}".format(input_sent), file=sys.stderr)
            try:
                sent_log_prob = self.parse(input_sent)
                best_tree = self.best_tree(input_sent)
            except ValueError:
                print("#No parses found for: {}".format(" ".join(input_sent)), file=sys.stderr)
                sent_log_prob = self._LOG_NINF
                best_tree = self.default_tree(input_sent)
            total_log_prob = sent_log_prob if total_log_prob is None else total_log_prob + sent_log_prob
            parses.append(best_tree)
            print(best_tree)
        if corpus_len:
            corpus_cross_entropy = total_log_prob / corpus_len
            print("#-cross entropy (bits/word): %g" % corpus_cross_entropy, file=sys.stderr)
        return (corpus_cross_entropy, parses)

    def parse_file(self, filename):
        parses = []
        with open(filename, 'r') as fh:
            parses = self.parse_stream(fh)
        return parses

    def parse_stream(self, handle):
        if self.verbose:
            print("parsing from stream: {}".format(handle), file=sys.stderr)
        sentences = []
        for line in handle:
            line = line.strip()
            sentences.append(line)
        parses = self.parse_sentences(sentences)
        return parses

# end of class CkyParse

if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='count', default=0,
                           help="verbose output")
    argparser.add_argument("-s", "--startsymbol", dest="startsym", type=str, default="TOP",
                           help="start symbol")
    argparser.add_argument("-i", "--parse", dest="parse_mode", action="store_true",
                           help="parsing mode; takes sentence and produces parse if possible")
    argparser.add_argument("-o", "--generate", dest="generate_mode", action="store_true",
                           help="generate mode; takes grammar and produces sentences if possible")
    argparser.add_argument("-n", "--numsentences", dest="num_sentences", type=int, default=20,
                           help="number of sentences to generate; in --generate mode")
    argparser.add_argument("-r", "--prior", dest="use_prior", action="store_false",
                           help="use prior for pruning")
    argparser.add_argument("-p", "--pruning", dest="use_pruning", action="store_false",
                           help="use prior for pruning")
    argparser.add_argument("-u", "--unseentags", dest="unseen_file", type=str, default="",
                           help="unseen tags filename")
    argparser.add_argument("-b", "--beam", dest="beam", type=float, default=0.0001,
                           help="use prior for pruning")
    argparser.add_argument("-a", "--allowedwords", dest="allowed_words_file", type=str,
                           default="allowed_words.txt",
                           help="only use this list of words when parsing and generating")
    argparser.add_argument("-g", "--grammars", nargs=argparse.ONE_OR_MORE, dest="grammar_files",
                           type=str, default=["S1.gr", "S2.gr", "Vocab.gr"],
                           help="list of grammar files; typically: S1.gr S2.gr Vocab.gr")

    args = argparser.parse_args()

    if args.parse_mode == args.generate_mode == False:
        print("ERROR: -i / --parse and -o / --generate cannot both be false", file=sys.stderr)
        argparser.print_help(sys.stderr)
        sys.exit(2)

    if not args.grammar_files:
        print("ERROR: grammar files required", file=sys.stderr)
        argparser.print_help(sys.stderr)
        sys.exit(2)

    if not args.allowed_words_file:
        print("ERROR: allowed words filename required", file=sys.stderr)
        argparser.print_help(sys.stderr)
        sys.exit(2)

    if args.verbose:
        print("#verbose level: {}".format(args.verbose), file=sys.stderr)
        print("#mode: {}".format("parse" if args.parse_mode else "generate"), file=sys.stderr)
        print("#grammar: {}".format(" ".join(args.grammar_files)), file=sys.stderr)

    gram = Pcfg(args.grammar_files, args.startsym, args.allowed_words_file, args.verbose)
    #print(gram)

    if args.generate_mode:
        gen = PcfgGenerator(gram, args.verbose)
        for _ in range(args.num_sentences):
            print(" ".join(gen.generate()))

    if args.parse_mode:
        parser = CkyParse(gram, args.verbose, args.use_prior, args.use_pruning, args.beam, args.unseen_file)
        parser.parse_stream(sys.stdin)
