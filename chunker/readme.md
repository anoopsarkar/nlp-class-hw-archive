
# Phrasal Chunking, Homework 2

## Training phase

    python default.py > default.model

## Testing and Evaluation phase

    python perc.py -m default.model > output
    python score-chunks.py < output

OR

    python perc.py -m default.model | python score-chunks.py

