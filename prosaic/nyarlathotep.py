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
from functools import reduce

import nlp
from util import plus

# rhyme_sound(tagged_sentence)
# count_syllables_in_word(word)
# count_syllables(tagged_sentence)
# tagged_sentence_to_string(tagged_sentence)
# save(db, data)
# is_multiclause(tagged_sentence)
# split_multiclause(tagged_sentence)
# expand_multiclause(tagged_sentences)

def process_sentence(tagged_sentence, source_name, line_no):
    words = map(first, tagged_sentence)
    phonemes = list(map(word_to_phonemes, words))
    return {"stems": sentence_to_stems(tagged_sentence),
            "source": source_name,
            "tagged": tagged_sentence,
            "rhyme_sound": rhyme_sound(tagged_sentence),
            "phonemes": phonemes,
            "num_syllables": count_syllables(tagged_sentence),
            "line_no": line_no,
            "raw": tagged_sentence_to_string(tagged_sentence),}

def process_text(raw_text, source_name, db):
    print("extracting sentences...")
    sentences = nlp.sentences(raw_text)

    print("tagging sentences...")
    tagged_sentences = list(map(tag, sentences))

    print("expanding clauses...")
    tagged_sentences = expand_multiclause(tagged_sentences)

    print("parsing and saving sentences...")
    for x in range(0, len(tagged_sentences)):
        tagged_sentence = tagged_sentences[x]
        data = process_sentence(tagged_sentence, source_name, x)
        save(db, data)

    print("done")

