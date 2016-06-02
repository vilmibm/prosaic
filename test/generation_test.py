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
from prosaic.parsing import pre_process_text, pre_process_sentence


def test_pre_process_text():
    assert pre_process_text("\nhello\n\n\n\nhow are    you\ni am fine\n\n") == " hello how are you i am fine "

def test_pre_process_sentences():
    should = [(" hello, how are you''", "hello, how are you"),
             ('"i am doing fine ', 'i am doing fine'),
             ('"sup dog"', '"sup dog"'),
             ('{result of the contest', 'result of the contest'),
             ('{result of the contest}', '{result of the contest}'),
             ('result of the contest}', 'result of the contest'),
             ('[result of the contest', 'result of the contest'),
             ('[result of the contest]', '[result of the contest]'),
             ('result of the contest]', 'result of the contest'),
             ('(result of the contest', 'result of the contest'),
             ('(result of the contest)', '(result of the contest)'),
             ('result of the contest)', 'result of the contest'),
             ('result of the conte\\nst', 'result of the contest'),
             ("result of the conte\\'st", "result of the conte'st"),
             ('puke"', 'puke'),
             ('“puke”', 'puke'),
             ('«vomit»', 'vomit')]

    for original, expected in should:
        assert pre_process_sentence(original) == expected
