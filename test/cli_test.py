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
from os import environ
from os.path import join
import sys

from pymongo import MongoClient
from pytest import fixture
from sh import prosaic, rm

TEST_DB = 'prosaic_test'
TEST_PROSAIC_HOME = '/tmp/prosaic_test'
# TODO pick shorter book lulz
TEST_CORPUS_PATH = './pride.txt'

@fixture(scope='module')
def env(request):
    environ['PROSAIC_HOME'] = TEST_PROSAIC_HOME
    environ['EDITOR'] = 'echo'
    request.addfinalizer(partial(rm, '-rf', TEST_PROSAIC_HOME))
    return None

@fixture(scope='module')
def client(request):
    request.addfinalizer(lambda: MongoClient().drop_database(TEST_DB))
    return MongoClient()

class TestCorpusCommands:

    def test_loadfile(self, env, client):
        client.drop_database(TEST_DB)
        prosaic('corpus', 'loadfile', '-dprosaic_test', TEST_CORPUS_PATH)
        assert client[TEST_DB].phrases.count() > 0

    def test_ls(self, env):
        out = prosaic('corpus', 'ls').split('\n')
        assert "prosaic_test" in out

    def test_rm(self, env, client):
        client.drop_database(TEST_DB)
        out = prosaic('corpus', 'ls').split('\n')
        assert "prosaic_test" not in out


class TestPoemCommands:
    def test_new_with_template(self, env, client):
        prosaic('corpus', 'loadfile', '-dprosaic_test', TEST_CORPUS_PATH)
        out = prosaic('poem', 'new', '-tsonnet', '-dprosaic_test')
        assert len(out.split('\n')) > 10

    def test_new_with_default(self, env):
        out = prosaic('poem', 'new', '-dprosaic_test')
        assert len(out.split('\n')) >= 3

class TestTemplateCommands:
    def test_new(self, env):
        prosaic('template', 'new', 'hello')
        template_path = join(TEST_PROSAIC_HOME, 'templates', 'hello.json')
        lines = open(template_path).readlines()
        assert len(lines) > 1

    def test_ls(self, env):
        out = prosaic('template', 'ls')
        assert len(out.split('\n')) > 4
        assert 'hello' in out

    def test_edit(self, env):
        out = prosaic('template', 'edit', 'hello')
        assert out == '/tmp/prosaic_test/templates/hello.json\n'

    def test_rm(self, env):
        prosaic('template', 'rm', 'hello')
        out = prosaic('template', 'ls')
        assert 'hello' not in out


