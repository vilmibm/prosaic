#   This program is part of prosaic.

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
import prosaic.nlp as nlp

def test_alliteration():
    should = [("Give me the splendid silent sun", True),
              ("Peter Piper picked a peck of pickled peppers", True),
              ("And the silken sad uncertain rustling of each purple curtain", True),
              ("i ate the line along", True),
              ("Zany zebras need to leave", True),
              ("i eat green apples every day", False),
              ("cardossian cruiser, you are cleared to land.", True),
              ("power protip: touch plants and have feels", True),
              ("once upon ultimate fantasy", False),
              ("purely and fundamentally for analytical purposes", True),
              ("Cats chew on dead mice", False),
              ("Sad shanties line darkened blocks", False),]

    for pair in should:
        tagged_sentence = nlp.tag(pair[0])
        assert nlp.has_alliteration(tagged_sentence) == pair[1]
