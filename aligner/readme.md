
# Word Alignment, Homework 3

You will be developing your aligner on the French-English data which
is the default language pair for the following python programs.

## Training phase

    python default.py -n 10000 > dice.a

## Check your alignment file

    python check-alignments.py -i dice.a

Ignore the following warning:

    WARNING:root:WARNING (check-alignments.py): bitext is longer than alignment

## Score your alignment file

    python score-alignments.py -i dice.a

## Do it all at once

    python default.py -n 10000 | python check-alignments.py | python score-alignments.py

## Leaderboard

In this homework, you will be developing your aligner on French-English
data, but you will be uploading your alignment file for the provided
German-English data. To upload the alignment using `default.py`:

    python default.py -p europarl -f de -n 10000 > output.a

Then upload the file `output.a` to the leaderboard on
[sfu-nlp-class.appspot.com](https://sfu-nlp-class.appspot.com)

OR

    python perc.py -m default.model | python score-chunks.py

## Options

    python default.py -h

This shows the different options you can use in your training
algorithm implementation.  In particular the -n option will let you
run your algorithm for less or more iterations to let your code run
faster with less accuracy or slower with more accuracy. Please use
the -n option in your code so that we are able to run your code
with different number of iterations.

