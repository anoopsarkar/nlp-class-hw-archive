Decipherment
============

Get started:

    git clone https://github.com/anoopsarkar/nlp-class-hw.git
    cd nlp-class-hw/decipher

## Install requirements 

    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

To use the pytorch code in `nlm.py` you should also do:

    pip3 install -r pytorch-requirements.txt

## Quick Start

Take a look at the Python notebook: `decipher.ipynb`

The file `data/cipher.txt` contains the ciphertext.

`mlstm_ns.pt`

## ngram Language Model

The ngram language model file is in `data/6-gram-wiki-char.lm.bz2`
and it is a character level LM trained using backoff smoothing.
The logprobs are in base 10.

The model file can be loaded and used for scoring arbitrary
subsequences using the code in `ngram.py`. To see how it works, run
it and examine the source:

    python3 ngram.py

The LM is in the file `data/6-gram-wiki-char.lm.bz2` which was
trained on the data in `data/default.wiki.txt.bz2`. Note that all
punctuations and spaces are stripped. The start of each sequence
is `<s>` and end of each sequence is `</s>`.

The file `ngram.py` contains some useful functions that will help you write
the `SCORE` function as needed by the beam search algorithm.

## Neural Language Model

Download the character neural LM model file from this link:

https://drive.google.com/open?id=1njgnNIAZHOR3-CVMYX7b-j9oQVTO1fIb

Save it to the `data` directory so that the file is available as
`data/mlstm_ns.pt`.

The neural LM model can be loaded and used for scoring sequences
using the code in `nlm.py`. To see how it works, run it and examine
the source:

    python3 nlm.py

The sequence scoring takes quite a bit longer than the ngram LM
especially on the CPU (when `cuda=False`). This is to be expected.
If you have access to a GPU then try with `cuda=True`. You should
see some speed improvement.

The logprob scores from the neural LM are not comparable to the
ngram LM, but they are internally consistent.

