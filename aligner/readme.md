
# Word Alignment, Homework 3

You will be developing your aligner on the French-English data which
is the default language pair for the following python programs.

## Training phase

Use the default Dice alignment to align the first 10,000 lines of
the training data.

    python default.py -n 10000 > dice.a

## Check your alignment file

    python check-alignments.py -i dice.a

Ignore the following warning:

    WARNING:root:WARNING (check-alignments.py): bitext is longer than alignment

## Score your alignment file

You will see the precision, recall and the alignment error rate
(AER) scores of your alignment. For precision and recall, the higher
the better. For AER the lower the better.

    python score-alignments.py -i dice.a

## Do it all at once

    python default.py -n 10000 | python check-alignments.py | python score-alignments.py

## Leaderboard

**Important: You need upload the alignments on German-English data
to the leaderboard**

In this homework, you will be developing your aligner on French-English
data, but you will be uploading your alignment file for the provided
German-English data. To upload the alignment using `default.py`:

    python default.py -p europarl -f de -n 10000 > output.a

When you develop your own aligner called `your-aligner.py` you have
to make sure you use the same command line arguments as `default.py`:

    python your-aligner.py -p europarl -f de -n 10000 > output.a

Then upload the file `output.a` to the leaderboard on
[sfu-nlp-class.appspot.com](https://sfu-nlp-class.appspot.com)

## Options

    python default.py -h

This shows the different options you can use in your training
algorithm implementation.  In particular the -n option will let you
run your algorithm on different number of sentence pairs so that
your code can run faster with less accuracy or slower with more
accuracy. You must use the -n option in your code so that we are
able to run your code with different data sizes.

