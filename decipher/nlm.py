import torch
from torch.autograd import Variable
import models
import math
import sys
import string
from tqdm.autonotebook import tqdm
from collections import namedtuple
from multiprocessing import Queue, Process
import warnings

# Based on various pytorch forum posts and github issues this
# warnings can be safely ignored
warnings.filterwarnings("ignore", category=torch.serialization.SourceChangeWarning)

Model = namedtuple('Model', ['embed', 'rnn', 'states', 'hidden', 'last'])

def batchify(data, bsz=1):
    tokens = len(data.encode())
    ids = torch.LongTensor(tokens)
    token = 0
    for char in data.encode():
        ids[token] = char
        token += 1
    nbatch = ids.size(0) // bsz
    ids = ids.narrow(0, 0, nbatch * bsz)
    ids = ids.view(bsz, -1).t().contiguous()
    return ids

def make_cuda(state):
    if isinstance(state, tuple):
        return (state[0].cuda(), state[1].cuda())
    else:
        return state.cuda()

def prep_text(seed_text, cuda):
    text = batchify(seed_text)
    batch = Variable(text)
    if cuda:
        batch = batch.cuda()
    return text, batch

def load_model(filename, batch_size=1, cuda=False, layer=-1):
    print("Loading model {}..".format(filename), file=sys.stderr)
    checkpoint = torch.load(filename) if cuda else torch.load(filename, map_location=lambda storage, loc: storage)
    embed = checkpoint['embed']
    rnn = checkpoint['rnn']

    states = rnn.state0(batch_size)
    if isinstance(states, tuple):
        hidden, cell = states
    else:
        hidden = states
    last = hidden.size(0)-1
    if layer <= last and layer >= 0:
        last = layer

    if cuda:
        states = make_cuda(states)
        embed.cuda()
        rnn.cuda()

    print("Model on board!", file=sys.stderr)
    return Model(embed, rnn, states, hidden, last)

def rnn_states_output(text, batch, embed, rnn, states):
    for t in range(text.size(0)):
        emb = embed(batch[t])
        ni = (batch[t]).data[0]
        states, output = rnn(emb, states)
        if isinstance(states, tuple):
            hidden, cell = states
        else:
            hidden = states
    return ni, output, hidden

def llh_predict(output, k=5, cutoff=None):
    char_list = []
    llh_list = [] # log likelihood
    topv, topi = output.data.topk(k)
    for i in range(k):
        ni = topi[0][i]
        llh = topv[0][i]
        # prevent neg probs
        if llh < 0: break
        # where to cutoff if specified
        if cutoff is 'space':
            if chr(int(ni)) is ' ':
                break
            else:
                char_list.append(chr(int(ni)))
                llh_list.append(float(llh))

        elif cutoff is 'symbol':
            if chr(int(ni)).isalpha():
                char_list.append(chr(int(ni)))
                llh_list.append(float(llh))
            else: break
        else:
            char_list.append(chr(int(ni)))
            llh_list.append(float(llh))

    predictions = []
    for char, llh in zip(char_list, llh_list):
        predictions.append((char, llh))
    return predictions

def next_chars(c, cuda, model, k=5, cutoff=None):
    embed, rnn, states, hidden, last = model
    text, batch = prep_text(c, cuda)
    init_text, output, _ = rnn_states_output(text, batch, embed, rnn, states)
    llh_predictions = llh_predict(output, k, cutoff)
    return llh_predictions

def get_score(c, pred_dict):
    return pred_dict[c] if c in pred_dict else 99.0

def score_first(c, model, cuda=False):
    scores = { v : get_score(c, dict(next_chars(v, cuda, model, k=50))) for v in string.ascii_lowercase }
    return scores[min(scores, key=scores.get)]

def score_next(c, seq, model, cuda=False):
    return get_score(c, dict(next_chars(seq, cuda, model, k=50)))

def score_sequence(chars, model, cuda=False):
    if not chars:
        raise ValueError("Error: empty sequence")
    score = score_first(chars[0], model, cuda)
    seq = chars[0]
    for c in chars[1:]:
        score += score_next(c, seq, model, cuda)
        seq += c
    return -1*score

def score_sequence_progress(chars, model, cuda=False):
    if not chars:
        raise ValueError("Error: empty sequence")
    score = score_first(chars[0], model, cuda)
    seq = chars[0]
    print("Calculating score for \"{}\"".format(chars), file=sys.stderr)
    with tqdm(chars[1:], total=len(chars)-1) as pbar:
        pbar.set_description("Processing %s" % chars[0])
        for c in pbar:
            pbar.set_description("Processing %s" % c)
            score += score_next(c, seq, model, cuda)
            seq += c
    return -1*score
 
def clean_seq(sequence):
    return(sequence.translate(dict.fromkeys(map(ord, string.punctuation + ' '), None)).lower())

if __name__ == '__main__':
    model = load_model("data/mlstm_ns.pt", cuda=False)
    sequence = 'In a few cases, a multilingual artifact has been necessary to facilitate decipherment, the Rosetta Stone being the classic example. Statistical techniques provide another pathway to decipherment, as does the analysis of modern languages derived from ancient languages in which undeciphered texts are written. Archaeological and historical information is helpful in verifying hypothesized decipherments.'
    shorter_sequence = 'In a few cases, a multilingual artifact has been necessary.'
    s1 = 'zkxxuqxzpuq'
    s2 = 'thisisatest'
    print("score for \"{}\" = {}".format(s1, score_sequence(clean_seq(s1), model, cuda=False)))
    print("score for \"{}\" = {}".format(s2, score_sequence(clean_seq(s2), model, cuda=False)))
    print("score for \"{}\" = {}".format(shorter_sequence, score_sequence_progress(clean_seq(shorter_sequence), model, cuda=False)))
