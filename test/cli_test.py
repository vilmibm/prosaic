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
from contextlib import redirect_stdout
from functools import partial
import io
from os.path import join
from shutil import rmtree
import sys

from pytest import fixture, yield_fixture
from sqlalchemy import text

import prosaic.models as m
from prosaic.models import Corpus
from prosaic import main

TEST_PROSAIC_HOME = '/tmp/prosaic_test'
# TODO pick shorter book lulz
TEST_CORPUS_PATH = './pride.txt'
DB = m.Database(user='vilmibm', password='foobar', dbname='prosaic_test')

def prosaic(*args) -> int:
    """Helper function for running prosaic.main, mimicking use from the command
    line. Sets argv to be ['prosaic'] + whatever is passed as args. Returns the
    exit code prosaic would have returned."""
    sys.argv = ['prosaic'] + list(args) + ['-d', 'prosaic_test', '--user', 'vilmibm', '--password', 'foobar']
    return main()

@yield_fixture(scope='module')
def cleanup(request):
    yield None
    rmtree(TEST_PROSAIC_HOME)

@yield_fixture(scope='function')
def db(request):
    engine = m.get_engine(DB)
    m.Base.metadata.create_all(engine)
    conn = engine.connect()
    yield conn
    conn.close()
    m.Session.close_all()
    m.Base.metadata.drop_all(engine)

class TestCorpusCommands:

    def test_new_with_desc(self, cleanup, db):
        corpus_desc = 'a fun corpus'
        corpus_name = 'whee'
        assert 0 == prosaic('corpus', 'new', corpus_name, corpus_desc)
        corpus = db.execute(
            text("select name,description from corpora where name=:corpus_name")\
            .params(corpus_name=corpus_name)
        ).fetchone()
        assert corpus[0] == corpus_name
        assert corpus[1] == corpus_desc

    def test_ls(self, cleanup, db):
        corpora_names = ['a', 'b', 'c', 'd']
        for name in corpora_names:
            prosaic('corpus', 'new', name)

        buff = io.StringIO()
        with redirect_stdout(buff):
            assert 0 == prosaic('corpus', 'ls')
        buff.seek(0)
        result = buff.read()
        output_names = set(result.split('\n')[0:-1])
        assert len(output_names.intersection(set(corpora_names))) == len(corpora_names)
        
    def test_rm(self, cleanup, db):
        name = 'e'
        prosaic('corpus', 'new', name)
        find = text("select name from corpora where name=:name").params(name=name)
        results = db.execute(find).fetchall()
        assert 1 == len(results)
        assert 0 == prosaic('corpus', 'rm', name)
        results = db.execute(find).fetchall()
        assert 0 == len(results)

    def test_link(self, cleanup, db):
        pass

    def test_unlink(self, cleanup, db):
        pass

    def test_sources(self, cleanup, db):
        pass

#class TestPoemCommands:
#    def test_new_with_template(self, env, client):
#        # tests template choosing, blank rule
#        prosaic('corpus', 'loadfile', '-dprosaic_test', TEST_CORPUS_PATH)
#        out = prosaic('poem', 'new', '-tsonnet', '-dprosaic_test')
#        assert len(out.split('\n')) >= 17
#
#    def test_new_with_default(self, env):
#        out = prosaic('poem', 'new', '-dprosaic_test')
#        assert len(out.split('\n')) >= 3
#
#class TestTemplateCommands:
#    def test_new(self, env):
#        prosaic('template', 'new', 'hello')
#        template_path = join(TEST_PROSAIC_HOME, 'templates', 'hello.json')
#        lines = open(template_path).readlines()
#        assert len(lines) > 1
#
#    def test_ls(self, env):
#        out = prosaic('template', 'ls')
#        assert len(out.split('\n')) > 4
#        assert 'hello' in out
#
#    def test_edit(self, env):
#        out = prosaic('template', 'edit', 'hello')
#        assert out == '/tmp/prosaic_test/templates/hello.json\n'
#
#    def test_rm(self, env):
#        prosaic('template', 'rm', 'hello')
#        out = prosaic('template', 'ls')
#        assert 'hello' not in out
#

