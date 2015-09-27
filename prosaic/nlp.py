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
from itertools import takewhile, dropwhile
from functools import partial, lru_cache
import re
import sys
from os.path import join, expanduser, exists
import nltk
from prosaic.util import match, invert, first, compose, second, some, is_empty, last, find_first

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

DIVIDER_TAG = ':' # nltk uses this to tag for ; and :

# Set up some state that we'll use in the functions throughout this file:
# TODO consider making a class that has modular stemmer/tokenizer
stemmer = EnglishStemmer()
tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
cmudict_dict = cmudict.dict()

# Some useful regexes:
vowel_re = re.compile("[aeiouAEIOU]")
vowel_phoneme_re = re.compile("AA|AE|AH|AO|AW|AY|EH|EY|ER|IH|IY|OW|OY|UH|UW")
consonant_phoneme_re = re.compile("^(?:B|D|G|JH|L|N|P|S|T|V|Y|ZH|CH|DH|F|HH|K|M|NG|R|SH|TH|W|Z)")

# Helper predicates:
is_vowel = partial(match, vowel_re)
is_vowel_phoneme = partial(match, vowel_phoneme_re)
is_consonant_phoneme = partial(match, consonant_phoneme_re)

def word_to_phonemes(word):
    result = cmudict_dict.get(word.lower(), None)
    if result is None:
        # TODO I don't really like this. Should at least return None.
        return []
    else:
        return first(result)

sentences = lambda raw_text: tokenizer.tokenize(raw_text)

@lru_cache(maxsize=256)
def stem_word(word):
    return stemmer.stem(word)

def tag(sentence_string):
    tokenized_words = nltk.word_tokenize(sentence_string)
    return nltk.pos_tag(tokenized_words)

def stem_sentence(tagged_sentence):
    stemmed = map(compose(stem_word, first), tagged_sentence)
    return list(stemmed)

is_divider = lambda tu: DIVIDER_TAG == second(tu)

def split_multiclause(tagged_sentence):
    if some(is_divider, tagged_sentence):
        pred = invert(is_divider)
        first_clause = list(takewhile(pred, tagged_sentence))
        second_clause = list(dropwhile(pred, tagged_sentence))
        return [first_clause, second_clause]
    else:
        return [tagged_sentence]

def expand_multiclauses(tagged_sentences):
    # TODO consider itertools
    split = []
    for tagged_sentence in tagged_sentences:
        if not is_empty(tagged_sentence):
            split += split_multiclause(tagged_sentence)
    return split

# TODO Ideally we'd store the original sentence along with the tagged version,
# but that gets slightly hard with multiclause expansion.
punctuation_regex = re.compile("^[^a-zA-Z0-9]")

@lru_cache(maxsize=256)
def match_punctuation(string):
    return match(punctuation_regex, string)

def untag_sentence(tagged_sentence):
    """Takes a tagged sentence; returns it as a plain string."""
    output = ""
    for tu in tagged_sentence:
        if not is_empty(tu):
            text = first(tu)
            output += (" " + text) if not match(punctuation_regex, text) else text

    return output

def count_syllables_in_word(word):
    phonemes = word_to_phonemes(word)
    if phonemes:
        # count vowel syllables:
        vowel_things = filter(is_vowel_phoneme, phonemes)
    else:
        # raw vowel counting:
        vowel_things = filter(is_vowel, list(word))

    return len(list(vowel_things))

def count_syllables(tagged_sentence):
    syllable_counts = map(compose(count_syllables_in_word, first),
                          tagged_sentence)
    return sum(syllable_counts)

alpha_tag = re.compile("^[a-zA-Z]")
is_alpha_tag = partial(match, alpha_tag)

def rhyme_sound(tagged_sentence):
    without_punctuation = filter(compose(is_alpha_tag, second), tagged_sentence)
    words = list(map(first, without_punctuation))

    if is_empty(words):
        return None

    last_word = last(words)
    phonemes = word_to_phonemes(last_word)

    if is_empty(phonemes):
        return None

    return "".join(phonemes[-3:])

consonant_re = re.compile("(SH|CH|TH|B|D|G|L|N|P|S|T|V|Y|F|K|M|NG|R|W|Z)")
def has_alliteration(tagged_sentence):
    words = untag_sentence(tagged_sentence).split(' ')

    def first_consonant_sound(word):
        phonemes = word_to_phonemes(word)
        if not is_empty(phonemes):
            return find_first(is_consonant_phoneme, phonemes)
        else:
            return first(consonant_re.findall(word.upper()))

    first_consonant_phonemes = map(first_consonant_sound, words)
    last_phoneme = None
    for phoneme in first_consonant_phonemes:
        if last_phoneme is None:
            last_phoneme = phoneme
        else:
            if last_phoneme == phoneme:
                return True
            else:
                last_phoneme = phoneme
    return False

