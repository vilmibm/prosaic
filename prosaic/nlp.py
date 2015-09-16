#   This program is part of prosaic.

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
from functools import partial
import re
import sys
from os.path import join, expanduser, exists
import nltk
from prosaic.util import match, invert, first, compose

# We have to pause our imports, here, to do some NLTK prep. We can't import
# certain things until we've downloaded raw corpora and other data, so we do so
# here:
NLTK_DATA_PATH = join(expanduser('~'), 'nltk_data')
NLTK_DATA = ['punkt',
             'maxent_ne_chunker',
             'cmudict',
             'words',
             'maxent_treebank_pos_tagger',]

if not exists(NLTK_DATA_PATH):
    for datum in NLTK_DATA:
        nltk.download(datum)

from nltk.stem.snowball import EnglishStemmer
import nltk.chunk as chunk
from nltk.corpus import cmudict

# Set up some state that we'll use in the functions throughout this file:
# TODO consider making a class that has modular stemmer/tokenizer
stemmer = EnglishStemmer()
tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
cmudict_dict = cmudict.dict()

# Some useful regexes:
vowel_re = re.compile("[aeiouAEIOU]")
vowel_phoneme_re = re.compile("AA|AE|AH|AO|AW|AY|EH|EY|ER|IH|IY|OW|OY|UH|UW")
punctuation_tag_re = re.compile("^[^a-zA-Z]+$")

# Helper predicates:
is_vowel = partial(match, vowel_re)
is_vowel_phoneme = partial(match, vowel_phoneme_re)
is_punctuation_tag = partial(match, punctuation_tag_re)
is_alphanumeric_tag = invert(is_punctuation_tag)

def word_to_phonemes(word):
    result = cmudict_dict.get(word.lower(), None)
    if result is None:
        # TODO I don't really like this. Should at least return None.
        return []
    else:
        return first(result)

stem_word = lambda word: stemmer.stem(word)
sentences = lambda raw_text: tokenizer.tokenize(raw_text)
word_to_chars = lambda w: list(w)

def tag(sentence_string):
    tokenized_words = nltk.word_tokenize(sentence_string)
    return nltk.pos_tag(tokenized_words)

def sentence_to_stems(tagged_sentences):
    stemmed = map(compose(stem_word, first), tagged_sentences)
    return list(stemmed)
