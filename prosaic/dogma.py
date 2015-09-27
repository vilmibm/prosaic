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
from random import choice
import re

import prosaic.nlp as nlp
from prosaic.util import match, is_empty, update

class Rule:
    strength = 0

    def weaken(self):
        if self.strength > 0:
            self.strength -= 1

    def to_query(self):
        # Typically there would be a cond over (. self
        # strength) here, but this base class represents the
        # trivial rule.
        return {}

class SyllableCountRule(Rule):
    __slots__ = ['syllables', 'strength',]
    def __init__(self, syllables):
        self.syllables = syllables
        self.strength = syllables

    def to_query(self):
        if 0 == self.strength:
            query = super().to_query()
        else:
            modifier = self.syllables - self.strength
            lte = self.syllables + modifier
            gte = self.syllables - modifier
            query = {'num_syllables': {'$lte': lte, '$gte': gte}}

        return query

class KeywordRule(Rule):
    __slots__ = ['keyword', 'phrase_cache', 'strength']
    max_strength = 11
    where_clause_tmpl = 'Math.abs({} - this.line_no) <= {}'

    def __init__(self, keyword, db):
        self.strength = self.max_strength
        self.keyword = nlp.stem_word(keyword)
        self.prime_cache(db)

    def prime_cache(self, db):
        print('building phrase cache')
        self.phrase_cache = list(db.find({'stems': self.keyword}))
        if is_empty(self.phrase_cache):
            self.strength = 0

    def to_query(self):
        if 0 == self.strength:
            query = super().to_query()
        else:
            phrase = choice(self.phrase_cache)
            ok_distance = self.max_strength - self.strength
            line_no = phrase['line_no']
            query = {'source': phrase['source'],
                     '$where': self.where_clause_tmpl.format(line_no, ok_distance),}

        return query

class FuzzyKeywordRule(KeywordRule):
    def to_query(self):
        if 0 == self.strength:
            query = super().to_query()
        else:
            # TODO can do a better job of DRYing here
            phrase = choice(self.phrase_cache)
            ok_distance = 1 + self.max_strength - self.strength
            line_no = phrase['line_no']
            query = {'source': phrase['source'],
                     'line_no': {'$ne': line_no},
                     '$where': self.where_clause_tmpl.format(line_no, ok_distance),}
        return query

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
            query = super().to_query()
        else:
            query = {'rhyme_sound': self.next_sound()}

        return query

class AlliterationRule(Rule):
    __slots__ = ['strength', 'which']
    def __init__(self, which):
        self.strength = 1
        self.which = which

    def to_query(self):
        if 0 == self.strength:
            query = super().to_query()
        else:
            query = {'alliteration': self.which}

        return query

class RuleSet:
    def __init__(self, rules):
        self.rules = rules

    def to_query(self):
        return reduce(update, map(lambda r: r.to_query(), self.rules))

    def weaken(self):
        choice(self.rules).weaken()
        return self

