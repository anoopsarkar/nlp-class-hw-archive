
# Machine Translation Reranking, Homework 5

You will be developing your reranker on French-English data which
is the default language pair for the following python programs.

## Reranking with default weights 

Use the default reranker simply produces uniform weights for
all features in the file `data/train.nbest`:

    python default.py > default.weights

The default simply ignores the training data. See below on how to
use the training data to learn weights.

You can use the default weights with the reranker program
provided to you:

    python rerank.py -w default.weights > default.output

The reranker code tries to predict the best translation for each
sentence in the file `data/test.nbest`. The output file contains
the best translations according to the weights provided to the
reranker.

## Score the output

Score the output using `score-reranker.py`:

    python score-reranker.py < default.output

This prints out the BLEU score for the output file by comparing it
with `data/test.en`. The score is for the first 250 sentences of
the 500 sentences in the test set. 

Do not use `test.nbest` or `test.en` in your implementation of
reranking or you will get a zero mark on this assignment. Using the
reference data in `test.en` we can obtain an oracle score (the best
possible BLEU score we can get by reranking). See below for how to
compute the oracle score.

You can do it all at once:

    python rerank.py -w default.weights | python score-reranker.py

## The oracle score

How much better can you get by reranking. The program `oracle.py`
uses the reference sentences to show you the upper bound in
the improvement.

    python oracle.py | python score-reranker.py

The oracle uses the references in `test.en` but your reranker cannot
use that information to learn the weights. Learn your weights
**only** on the training data.

## Your reranker

The program `default.py` simply ignores the training data:

* `train.nbest`: n-best lists for training
* `train.en`: target language references for learning how to rank the n-best list
* `train.fr`: source language sentences used as input to a decoder to create the n-best list

Your job is to use the training data to learn weights for all the
features in `train.nbest`. Then you can use your weights to produce
a better output using `rerank.py`:

    python rerank.py -w your-weights > your-output

You can then score your output in the same way as shown above:

    python score-reranker.py < your-output

## Leaderboard

You should upload the output of `rerank.py` using weights that you
learn by using `train.nbest` (n-best list for training), `train.en`
(the reference target language output for training) and `train.fr`
(the source language input for training) to the leaderboard on
[sfu-nlp-class.appspot.com](https://sfu-nlp-class.appspot.com).

The score will be almost identical to the local score reported by
`score-reranker.py` so please do not upload excessively to the
leaderboard. The leaderboard scores on all 500 sentences in
`data/test.nbest` while the local score is on the first 250 sentences.

## Options

    python default.py -h

This shows the different options you can use in your training
algorithm implementation.  

## Data

The data directory contains several files derived from a French-English
newswire translation task.

- `train.fr`: Training data consisting of French news text 
- `train.en`: Human translations of the French training data
- `train.nbest`: N-best machine translations of the French training data
- `test.fr`: 500 sentences of French test data
- `test.en`: Human translations of the first 250 sentences of the French test
- `test.nbest`: N-best machine translations of the French test data  


