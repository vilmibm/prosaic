# This program is part of prosaic.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import re
import prosaic.nlp as nlp
from prosaic.util import first

def save(db, data):
    return db.insert(data)

def process_sentence(sentence, source_name, line_no):
    phonemes = list(map(nlp.word_to_phonemes, nlp.words(sentence)))
    return {'stems': nlp.stem_sentence(sentence),
            'source': source_name,
            'tagged': nlp.tag(sentence),
            'rhyme_sound': nlp.rhyme_sound(sentence),
            'phonemes': phonemes,
            'num_syllables': nlp.count_syllables(sentence),
            'line_no': line_no,
            'alliteration': nlp.has_alliteration(sentence),
            'raw': sentence,
            'blank': False,
    }

collapse_whitespace_re = re.compile("\s+")
def pre_process_text(raw_text):
    raw_text = re.sub(collapse_whitespace_re, ' ', raw_text)
    # TODO anything else?
    return raw_text

pairs = [('{', '}'), ('(', ')'), ('[', ']')]
bad_substrings = ['`', '“', '”', '«', '»', "''"]

def pre_process_sentence(sentence):

    if sentence.count('"') == 1:
        sentence = sentence.replace('"', '')

    # TODO bootleg
    for l,r in pairs:
        if sentence.count(l) == 1 and sentence.count(r) == 0:
            sentence = sentence.replace(l, '')
        if sentence.count(r) == 1 and sentence.count(l) == 0:
            sentence = sentence.replace(r, '')

    for substring in bad_substrings:
       sentence = sentence.replace(substring, '')

    return sentence.rstrip().lstrip()

def process_text(raw_text, source_name, db):
    print('pre-processing text...')
    raw_text = pre_process_text(raw_text)

    print("extracting sentences...")
    sentences = nlp.sentences(raw_text)

    print("expanding clauses...")
    sentences = nlp.expand_multiclauses(sentences)

    print("pre-processing, parsing and saving sentences...")
    for x in range(0, len(sentences)):
        sentence = pre_process_sentence(sentences[x])
        data = process_sentence(sentence, source_name, x)
        save(db, data)

    print("done")
