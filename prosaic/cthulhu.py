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
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from random import choice

from json import loads
import sys

import prosaic.dogma as dogma
from prosaic.util import pluck, is_empty, threaded, first, second

def build_sound_cache(db):
    return db.find().distinct("rhyme_sound")

def map_letters_to_sounds(db, template, sound_cache=None):
    letters = list(set(pluck(template, "rhyme")))
    if is_empty(letters):
        cache = {}
    else:
        sounds = sound_cache if sound_cache is not None else build_sound_cache(db)
        cache = dict(map(lambda l: [l, choice(sounds)], letters))
    return cache

def extract_rule(db, letter_sound_map, raw_pair):
    rule_key = first(raw_pair)
    value = second(raw_pair)
    rule = None

    if rule_key == 'rhyme': rule = dogma.RhymeRule(letter_sound_map.get(value))
    elif rule_key == 'blank': rule = dogma.BlankRule(db)
    elif rule_key == 'alliteration': rule = dogma.AlliterationRule(value)
    elif rule_key == 'keyword': rule = dogma.KeywordRule(value, db)
    elif rule_key == 'fuzzy': rule = dogma.FuzzyKeywordRule(value, db)
    elif rule_key == 'syllables': rule = dogma.SyllableCountRule(value)

    return rule

def extract_ruleset(db, letter_sound_map, template_line):
    rules = map(partial(extract_rule, db, letter_sound_map), template_line.items())
    return dogma.RuleSet(list(rules))

def ruleset_to_line(db, ruleset):
    line = None
    while not line:
        lines = list(db.find(ruleset.to_query()))
        if is_empty(lines):
            ruleset.weaken()
        else:
            line = choice(lines)
    return line

def poem_from_template(template, db, sound_cache=None):
    executor = ThreadPoolExecutor(4)
    letter_sound_map = map_letters_to_sounds(db, template, sound_cache)
    process_tmpl_line = threaded(partial(extract_ruleset, db, letter_sound_map),
                                 partial(ruleset_to_line, db))
    poem_lines = executor.map(process_tmpl_line, template)
    executor.shutdown()
    return list(poem_lines)
