#!/usr/bin/env python
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
import logging
import re
import prosaic.nlp as nlp
from prosaic.models import Phrase, Source, Corpus, get_session, Database

log = logging.getLogger('prosaic')

pairs = [('{', '}'), ('(', ')'), ('[', ']')]
bad_substrings = ['`', '“', '”', '«', '»', "''", '\\n', '\\',]
collapse_whitespace_re = re.compile("\s+")

def pre_process_text(raw_text: str) -> str:
    """Performs text-wide regex'ing we need before converting to sentences."""
    raw_text = re.sub(collapse_whitespace_re, ' ', raw_text)
    return raw_text

def pre_process_sentence(sentence: str) -> str:
    """Strip dangling pair characters. For now, strips some substrings that we
    don't want. r and lstrip. Returns modified sentence"""
    if sentence.count('"') == 1:
        sentence = sentence.replace('"', '')

    # TODO bootleg
    for l,r in pairs:
        if sentence.count(l) == 1 and sentence.count(r) == 0:
            sentence = sentence.replace(l, '')
        if sentence.count(r) == 1 and sentence.count(l) == 0:
            sentence = sentence.replace(r, '')

    # TODO collapse this into a regex and do it in pre_process_text
    for substring in bad_substrings:
       sentence = sentence.replace(substring, '')

    return sentence.rstrip().lstrip()

# TODO support source descriptions
def process_text(db: Database, source: Source, raw_text: str) -> None:
    """Given raw text and a source filename, adds a new source with the raw
    text as its content and then processes all of the phrases in the text."""

    log.debug('connecting to db...')
    session = get_session(db)

    log.debug('pre-processing text...')
    text = pre_process_text(raw_text)

    log.debug('adding source to corpus...')
    source.content = text
    session.add(source)

    log.debug('extracting sentences')
    sentences = nlp.sentences(text)

    log.debug("expanding clauses...")
    sentences = nlp.expand_multiclauses(sentences)

    log.debug("pre-processing, parsing and saving sentences...")
    for x in range(0, len(sentences)):
        sentence = pre_process_sentence(sentences[x])

        stems = nlp.stem_sentence(sentence)
        rhyme_sound = nlp.rhyme_sound(sentence)
        syllables = nlp.count_syllables(sentence)
        alliteration = nlp.has_alliteration(sentence)

        phrase = Phrase(stems=stems, raw=sentence, alliteration=alliteration, 
                        rhyme_sound=rhyme_sound,
                        syllables=syllables, line_no=x, source=source)
        # TODO save the thread on a coroutine or something

        session.add(phrase)

    session.commit()

    log.debug("done")
