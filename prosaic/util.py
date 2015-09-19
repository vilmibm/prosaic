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
from random import randint
import re

first = lambda l: l[0] if len(l) > 0 else None
second = lambda l: l[1] if len(l) > 1 else None
random_nth = lambda l: l[randint(0, len(l)-1)]
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
