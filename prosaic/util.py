# This program is part of prosaic.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
from functools import lru_cache
import re

first = lambda l: l[0] if len(l) > 0 else None
second = lambda l: l[1] if len(l) > 1 else None
plus = lambda x,y: x + y
is_empty = lambda l: 0 == len(l)
last = lambda l: l[-1] if not is_empty(l) else None

@lru_cache(maxsize=256)
def match(regex, string):
    return bool(regex.match(string))

def invert(f):
    def inverted_fun(*args):
        return not f(*args)
    return inverted_fun

def compose(f, g):
    def composed_fun(*args):
        return f(g(*args))
    return composed_fun

some = compose(any, map)

def pluck(dict_list, key):
    return list(map(lambda d: d.get(key), dict_list))

def update(d0, d1):
    d0.update(d1)
    return d0

def thread(initial, *fns):
    value = initial
    for fn in fns:
        value = fn(value)
    return value

def threaded(*fns):
    def threaded_fun(*args, **kwargs):
        value = fns[0](*args, **kwargs)
        for fn in fns[1:]:
            value = fn(value)
        return value
    return threaded_fun

def slurp(filename):
    with open(filename) as f:
        return "".join(map(lambda s: s.replace("\r\n", " "), f.readlines()))

def find_first(predicate, xs):
    return next(filter(predicate, xs), None)
