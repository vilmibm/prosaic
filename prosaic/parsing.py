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
from io import TextIOBase
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import re
from time import sleep

import prosaic.cfg as cfg # TODO this is temporary
import prosaic.nlp as nlp
from prosaic.models import Phrase, Source, Corpus, Session, Database, get_session

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

def process_sentences(source_id, line_offset, sentences):
    """This function takes an initial line number and a list of sentences. it
    opens a DB connection and turns each sentence into a Phrase, committing it
    to the source identified by source_id"""
    # TODO db crap
    log.debug("pre-processing, parsing and saving sentences...")
    log.debug('connecting to db...')
    session = get_session(Database(**cfg.DEFAULT_DB))
    source = session.query(Source).filter(Source.id == source_id).one()

    for x in range(0, len(sentences)):
        sentence = pre_process_sentence(sentences[x])

        stems = nlp.stem_sentence(sentence)
        rhyme_sound = nlp.rhyme_sound(sentence)
        syllables = nlp.count_syllables(sentence)
        alliteration = nlp.has_alliteration(sentence)

        line_no = line_offset + x

        phrase = Phrase(stems=stems, raw=sentence, alliteration=alliteration,
                        rhyme_sound=rhyme_sound,
                        syllables=syllables, line_no=line_no, source=source)

        session.add(phrase)

    log.debug('finished processing sentences...')
    session.commit()
    session.close()

def process_text(source: Source, text: TextIOBase) -> None:
    """Given raw text and a source filename, adds a new source with the raw
    text as its content and then processes all of the phrases in the text."""

    CHUNK_SIZE = 16000
    line_offset = 0
    futures = []
    ultimate_text = ''
    log.debug('connecting to db...')
    session = Session.object_session(source)
    source.content = ''
    session.add(source)
    session.commit()

    with ProcessPoolExecutor() as pool:
        chunk = text.read(CHUNK_SIZE)
        while len(chunk) > 0:
            chunk = pre_process_text(chunk)
            ultimate_text += chunk
            log.debug('extracting sentences')
            sentences = nlp.sentences(chunk)
            log.debug("expanding clauses...")
            sentences = nlp.expand_multiclauses(sentences)

            futures.append(pool.submit(process_sentences, source.id, line_offset, sentences))
            line_offset += len(sentences)
            chunk = text.read(CHUNK_SIZE)

        log.debug('waiting for chunks to finish processing...')
        for fut in as_completed(futures):
            if fut.exception() is not None:
                # TODO if error, cancel all futures and delete source.
                print('raising exception')
                raise fut.exception()

    log.debug('updating content for source')
    source.content = ultimate_text
    session.add(source)
    session.commit()
    session.close()
    log.debug("done processing text; closing db session")
