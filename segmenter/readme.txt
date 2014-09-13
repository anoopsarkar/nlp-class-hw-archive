
Run
---

python baseline.py | python score-segments.py

OR

python baseline.py > output
python score-segments.py -t output
rm output

Data
----

In the data directory, you are provided with counts collected from
training data which contained reference segmentations of Chinese
sentenes.

The format of the count_1w.txt and count_2w.txt is a tab separated key followed by a count:

__key__\t__count__

__key__ can be a single word as in count_1w or two words separated by a space as in count_2w.txt

For bigrams the probability of the first word in a sentence w can be looked up in count_2w.txt as

<S> w	Count

