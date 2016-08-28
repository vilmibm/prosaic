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
from multiprocessing import Process, Queue
from io import IOBase
import logging
import re
from typing import Optional

import prosaic.nlp as nlp
from prosaic.models import Phrase, Source, Database, get_session # TODO

# this is a sigil we use to signal that we're done processing a text file.
DONE_READING = 666

CHUNK_SIZE = 10000

BAD_CHARS = {'(': True,
             ')': True,
             '{': True,
             '}': True,
             '[': True,
             ']': True,
             '`': True,
             '"': True,
             '\n': True,
             '|': True,
             '/': True,
             '“': True,
             '”': True,
             '«': True,
             '»': True,
             '\\': True,
             '=': True,
             '#': True,
             '_': True,}
CLAUSE_MARKERS = {',':True, ';':True, ':':True}
SENTENCE_MARKERS = {'?':True, '.':True, '!':True}
# TODO random, magic number
LONG_ENOUGH = 20

log = logging.getLogger('prosaic')

def line_handler(db: Database,
                 line_queue: Queue,
                 error_queue: Queue,
                 source_id: int) -> None:

    session = get_session(db)
    source = session.query(Source).filter(Source.id == source_id).one()

    while True:
        try:
            line_pair = line_queue.get()
            if line_pair == DONE_READING:
                break

            line_no, line = line_pair
            stems = nlp.stem_sentence(line)
            rhyme_sound = nlp.rhyme_sound(line)
            syllables = nlp.count_syllables(line)
            alliteration = nlp.has_alliteration(line)

            phrase = Phrase(stems=stems, raw=line, alliteration=alliteration,
                            rhyme_sound=rhyme_sound,
                            syllables=syllables, line_no=line_no, source=source)

            session.add(phrase)
        except Exception as e:
            error_queue.put(e)
            log.error('Died while processing text, rolling back')
            session.rollback()
            session.close()
            return

    session.commit()

def peek(stream: IOBase, chunk_size: int) -> str:
    if hasattr(stream, 'peek'):
        return stream.peek(chunk_size)
    else:
        current_pos = stream.tell()
        result = stream.read(chunk_size)
        stream.seek(current_pos)
        return result


def process_text(db: Database,
                 source: Source,
                 text: IOBase) -> Optional[Exception]:
    session = get_session(db)
    line_no = 1 # lol
    ultimate_text = ''
    futures = []
    source.content = ''
    session.add(source)
    session.commit() # so we can attach phrases to it. need its id.
    line_queue = Queue()
    error_queue = Queue()
    db_proc = Process(target=line_handler,
                      args=(db, line_queue, error_queue, source.id))
    db_proc.start()

    chunk = text.read(CHUNK_SIZE)
    while len(chunk) > 0:
        line_buff = ""
        for c in chunk:
            if BAD_CHARS.get(c, False):
                if not line_buff.endswith(' '):
                    line_buff += ' '
                continue
            if CLAUSE_MARKERS.get(c, False):
                if len(line_buff) > LONG_ENOUGH:
                    ultimate_text += line_buff
                    line_queue.put((line_no, line_buff))
                    line_no += 1
                    line_buff = ""
                else:
                    line_buff += c
                continue
            if SENTENCE_MARKERS.get(c, False):
                if len(line_buff) > LONG_ENOUGH:
                    ultimate_text += line_buff
                    line_queue.put((line_no, line_buff))
                    line_no += 1
                line_buff = ""
                continue
            if c == ' ' and line_buff.endswith(' '):
                continue
            if c == "'" and line_buff.endswith(' '):
                continue
            if c == "'" and peek(text, 1) == ' ':
                continue
            line_buff += c
        chunk = text.read(CHUNK_SIZE)

    line_queue.put(DONE_READING)
    db_proc.join()

    error = None
    if error_queue.empty():
        source.content = ultimate_text
        session.add(source)
    else:
        error = error_queue.get()
        session.delete(source)

    result = None
    if error is None:
        result = source.id
    else:
        result = error

    session.commit()
    session.close()

    return result
