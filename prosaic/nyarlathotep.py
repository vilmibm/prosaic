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
import prosaic.nlp as nlp
from prosaic.util import first

def save(db, data):
    return db.insert(data)

def process_sentence(tagged_sentence, source_name, line_no):
    words = map(first, tagged_sentence)
    phonemes = list(map(nlp.word_to_phonemes, words))
    return {"stems": nlp.stem_sentence(tagged_sentence),
            "source": source_name,
            "tagged": tagged_sentence,
            "rhyme_sound": nlp.rhyme_sound(tagged_sentence),
            "phonemes": phonemes,
            "num_syllables": nlp.count_syllables(tagged_sentence),
            "line_no": line_no,
            "alliteration": nlp.has_alliteration(tagged_sentence),
            "raw": nlp.untag_sentence(tagged_sentence),
    }

def process_text(raw_text, source_name, db):
    print("extracting sentences...")
    sentences = nlp.sentences(raw_text)

    print("tagging sentences...")
    tagged_sentences = list(map(nlp.tag, sentences))

    print("expanding clauses...")
    tagged_sentences = nlp.expand_multiclauses(tagged_sentences)

    print("parsing and saving sentences...")
    for x in range(0, len(tagged_sentences)):
        tagged_sentence = tagged_sentences[x]
        data = process_sentence(tagged_sentence, source_name, x)
        save(db, data)

    print("done")
