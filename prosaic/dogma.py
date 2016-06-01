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
import logging
from random import choice
import re

import sqlalchemy as sa

import prosaic.nlp as nlp
from prosaic.models import Phrase, Corpus, Source
from prosaic.util import match, is_empty, update

log = logging.getLogger('prosaic')

class Rule:
    strength = 0

    def weaken(self):
        if self.strength > 0:
            self.strength -= 1

    def to_query(self):
        return '1 = 1'

class SyllableCountRule(Rule):
    __slots__ = ['syllables', 'strength',]
    def __init__(self, syllables):
        self.syllables = syllables
        self.strength = syllables

    def to_query(self):
        if 0 == self.strength:
            return super().to_query()

        modifier = self.syllables - self.strength
        return 'p.syllables >= {} and p.syllables <= {}'.format(
                self.syllables + modifier,
                self.syllables - modifier)

class KeywordRule(Rule):
    __slots__ = ['keyword', 'phrase_cache', 'strength']
    max_strength = 11

    def __init__(self, keyword, conn, corpus_id):
        self.strength = self.max_strength
        self.keyword = nlp.stem_word(keyword)
        self.prime_cache(conn, corpus_id)

    def prime_cache(self, conn, corpus_id):
        log.debug('building phrase cache')
        sql = """
        select p.line_no, p.source_id
        from phrases p
        join corpora_sources cs
        on p.source_id = cs.source_id
        where corpus_id = :corpus_id
        and p.stems @> ARRAY[:keyword]
        """
        self.phrase_cache = conn.execute(sa.text(sql)\
                                         .params(keyword=self.keyword,
                                                 corpus_id=corpus_id))\
                            .fetchall()
        if is_empty(self.phrase_cache):
            self.strength = 0

    def to_query(self):
        if 0 == self.strength:
            return super().to_query()

        if self.max_strength == self.strength:
            return "stems @> ARRAY['{}']".format(self.keyword)

        phrase = choice(self.phrase_cache)
        ok_distance = self.max_strength - self.strength
        line_no, source_id = phrase

        return "p.source_id = {} and abs({} - p.line_no) <= {}".format(
            source_id, line_no, ok_distance
        )

class FuzzyKeywordRule(KeywordRule):
    def to_query(self):
        if 0 == self.strength:
            return super().to_query()

        phrase = choice(self.phrase_cache)
        ok_distance = 1 + self.max_strength - self.strength
        line_no, source_id = phrase

        return "p.source_id = {} and abs({} - p.line_no) <= {}".format(
            source_id, line_no, ok_distance
        )

zero_re = re.compile('0')
one_re = re.compile('1')
two_re = re.compile('2')
class RhymeRule(Rule):
    __slots__ = ['sound', 'strength']
    def __init__(self, rhyme):
        self.strength = 3
        self.sound = rhyme

    def next_sound(self):
        strength = self.strength
        sound = self.sound
        # TODO ugh
        if 3 == strength:
            return sound
        elif 2 == strength:
            if zero_re.search(sound):
                return sound.replace('0', '1')
            elif one_re.search(sound):
                return sound.replace('1', '2')
            elif two_re.search(sound):
                return sound.replace('2', '0')
        elif 1 == strength:
            if zero_re.search(sound):
                return sound.replace('0', '2')
            elif one_re.search(sound):
                return sound.replace('1', '0')
            elif two_re.search(sound):
                return sound.replace('2', '1')

    def to_query(self):
        if 0 == self.strength:
            return super().to_query()

        return "p.rhyme_sound = '{}'".format(self.next_sound())

class AlliterationRule(Rule):
    __slots__ = ['strength', 'which']
    def __init__(self, which):
        self.strength = 1
        self.which = which

    def to_query(self):
        if 0 == self.strength:
            return super().to_query()

        return "p.alliteration = true"

class BlankRule(Rule): pass

class RuleSet:
    def __init__(self, rules):
        self.rules = rules

    def contains(self, rule_class):
        return 0 < len(list(filter(lambda r: rule_class == type(r),
                                   self.rules)))

    def to_query(self, sess):
        base_sql = """
            select p.raw
            from phrases p
            join corpora_sources cs
            on p.source_id = cs.source_id
            where corpus_id = :corpus_id
        """

        wheres = map(lambda r: r.to_query(), self.rules)
        return base_sql + ' and ' + ' and '.join(wheres)

    def weaken(self):
        choice(self.rules).weaken()
        return self

