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
from random import randint
import re

first = lambda l: l[0] if len(l) > 0 else None
match = lambda regex, string: bool(regex.match(string))
random_nth = lambda l: l[randint(0, len(l)-1)]
plus = lambda x,y: x + y

def invert(f):
    def inverted_fun(*args):
        return not f(*args)
    return inverted_fun

def compose(f, g):
    def composed_fun(*args):
        return f(g(*args))
    return composed_fun
