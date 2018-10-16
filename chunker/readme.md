
# Phrasal Chunking

## Setup

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

## Training phase

    python3 default.py > default.model

## Testing and Evaluation phase

    python3 perc.py -m default.model > output
    python3 score-chunks.py < output

OR

    python3 perc.py -m default.model | python3 score-chunks.py

## Options

    python3 default.py -h

This shows the different options you can use in your training
algorithm implementation.  In particular the -n option will let you
run your algorithm for less or more iterations to let your code run
faster with less accuracy or slower with more accuracy. You must
implement the -n option in your code so that we are able to run
your code with different number of iterations.

