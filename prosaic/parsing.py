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
from concurrent.futures import ProcessPoolExecutor
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

    session.commit()
    session.close()

def process_text(source: Source, text: TextIOBase) -> None:
    """Given raw text and a source filename, adds a new source with the raw
    text as its content and then processes all of the phrases in the text."""


    # single loop reading from the buffer. what to do about sentence
    # boundaries? i'd prefer not to read a character at a time. However, I
    # think it's okay to lose some stuff at the chunk boundaries for now.
    # faster performance means more room to do sentence splitting, and i
    # theorize this will yield net more sentences.

    # if float ids, would need to check the incrementing in the sentence
    # splitter to do

    # I think the float id idea is too complex for now; i want to be more
    # incremental. I will use a process pool for the final sentence processing
    # but have everything be synchronous until then.

    # Going to start with a process pool executor that creates a DB connection
    # when it's ready to add phrases. this means that i may end up with
    # partially committed sources.o

    # Option one with this is to just let that happen. Users can delete and
    # re-add sources if they look incomplete or fucked up. Other option is to
    # detect when a given chunk future fails, shut down the pool, and then
    # delete the source.

    # In an absolutely ideal world, i'd be using nested DB transactions. But
    # going with processes over threads means I can't share that DB handle
    # between the processes.

    # line_no = 0
    # futures = []
    # executor = "TODO"
    # loop over buffer, reading N kb
        # pre_process the chunk
        # extract list of sentences
        # split_sentences = [] # pairs of id, sentence
        # for each sentence
          # attempt to split into subclauses
          # for each subsentence
            # add to split_sentences
        # futures.append(executor.submit(aplit_sentences))
    # loop over all futures until all done or one exception'd
    # if one failed, cancel all futures and delete source from db

    # within each submit:
    # do all of the nlp operations
    # get a db handle
    # commit each phrase object


    # IDEA is there a way to use two pools? one to do the subtasks in the
    # lead-up work before parallelizing?
    CHUNK_SIZE = 2000
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

        done = []
        while len(done) != len(futures):
            log.debug('waiting for chunks to finish processing...')
            for fut in futures:
                if fut.done():
                    if fut.exception():
                        raise fut.exception
                    else:
                        done.append(fut)
            sleep(1)

    log.debug('updating content for source')
    source.content = ultimate_text
    session.add(source)
    session.commit()
    session.close()
    log.debug("done processing text; closing db session")
