
# Phrasal Chunking, Homework 2

## Training phase

    python default.py > default.model

## Testing and Evaluation phase

    python perc.py -m default.model > output
    python score-chunks.py < output

Then upload the file `output` to the leaderboard on sfu-nlp-class.appspot.com

OR

    python perc.py -m default.model | python score-chunks.py

