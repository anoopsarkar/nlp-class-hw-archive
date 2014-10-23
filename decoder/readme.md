
# Machine Translation Decoding, Homework 4

You will be developing your decoder on French-English data which
is the default language pair for the following python programs.

## Decoding phase

Use the default decoder (which does not reorder words between source
and target) to produce an output translation for the input sentences
in `data/input`

    python default.py > output

You can expand the search space for the the decoder by expanding
the number of items considered in beam search: using the `-s` option:

    python default.py -s 10 > output

## Score the decoder output

How much worse is the output produced by your decoder compared to
the best **reachable** translation according to the model? The
program `score-decoder.py` can be used to score the decoder output:

    python score-decoder.py < output

The output shows the total log probability (language model and
translation model) for each translation in your output and the total
average log probability over all sentence pairs:

    SENTENCE PAIR:
    ( la motion est adoptée , et le rapport est adopté . )
    ( motions deemed adopted , and the report agreed to )
    TOTAL LM LOGPROB: -14.709625
    ...........
    TOTAL TM LOGPROB: 0.410658

You can see a much more detailed output by changing the value of
the verbosity flag `-v`:

    python score-decoder.py -v 2 < output

## Do it all at once

    python default.py -s 100 | python score-decoder.py

## Leaderboard

You should upload the output file produced by your decoder to the
leaderboard on
[sfu-nlp-class.appspot.com](https://sfu-nlp-class.appspot.com).

The score will be identical to the local score reported by
`score-decoder.py` so please do not upload excessively to the
leaderboard.

## Options

    python default.py -h

This shows the different options you can use in your training
algorithm implementation.  

