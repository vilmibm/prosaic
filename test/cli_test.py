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
from collections import namedtuple
from contextlib import redirect_stdout
import io
from os.path import join
from shutil import rmtree
import sys

from pytest import yield_fixture

import prosaic.models as m
from prosaic.models import Corpus, Source
from prosaic import main

TEST_PROSAIC_HOME = '/tmp/prosaic_test'
# TODO pick shorter book lulz
TEST_SOURCE_PATH = './pride.txt'
DB = m.Database(user='vilmibm', password='foobar', dbname='prosaic_test')
db_args = ['-d', 'prosaic_test', '--user', 'vilmibm', '--password', 'foobar']
Result = namedtuple('Result', ['code', 'lines'])

def prosaic(*args) -> Result:
    """Helper function for running prosaic.main, mimicking use from the command
    line. Sets argv to be ['prosaic'] + whatever is passed as args. Returns the
    exit code prosaic would have returned."""
    sys.argv = ['prosaic'] + list(args) + db_args
    buff = io.StringIO()
    code = None
    with redirect_stdout(buff):
        code = main()
    buff.seek(0)
    result = buff.read()
    lines = set(result.split('\n')[0:-1])
    return Result(lines=lines, code=code)

@yield_fixture(scope='function')
def cleanup(request):
    yield None
    rmtree(TEST_PROSAIC_HOME)

@yield_fixture(scope='function')
def db(request):
    engine = m.get_engine(DB)
    m.Base.metadata.create_all(engine)
    yield m.get_session(DB)
    m.Session.close_all()
    m.Base.metadata.drop_all(engine)

class TestCorpusCommands:
    def test_new_with_desc(self, cleanup, db):
        corpus_desc = 'a fun corpus'
        corpus_name = 'whee'
        assert 0 == prosaic('corpus', 'new', corpus_name, corpus_desc).code
        corpus = db.query(Corpus).filter(Corpus.name==corpus_name).one()
        assert corpus.name == corpus_name
        assert corpus.description == corpus_desc

    def test_new_without_desc(self, cleanup, db):
        corpus_name = 'whee'
        assert 0 == prosaic('corpus', 'new', corpus_name).code
        corpus = db.query(Corpus).filter(Corpus.name==corpus_name).one()
        assert corpus.name == corpus_name

    def test_ls(self, cleanup, db):
        corpora_names = ['a', 'b', 'c', 'd']
        for name in corpora_names:
            prosaic('corpus', 'new', name)

        result = prosaic('corpus', 'ls')
        assert 0 == result.code
        assert len(result.lines.intersection(set(corpora_names))) == len(corpora_names)

    def test_rm(self, cleanup, db):
        name = 'e'
        prosaic('corpus', 'new', name)
        corpora = db.query(Corpus).filter(Corpus.name==name).all()
        assert 1 == len(corpora)
        assert 0 == prosaic('corpus', 'rm', name).code
        corpora = db.query(Corpus).filter(Corpus.name==name).all()
        assert 0 == len(corpora)

    def test_link(self, cleanup, db):
        flarf = Source(name='flarf', description='blah', content='lol naw')
        puke = Source(name='puke', description='blah', content='lol naw')
        corpus = Corpus(name='whee', description='bleh')
        db.add_all([corpus, flarf, puke])
        db.commit()
        assert 0 == prosaic('corpus', 'link', 'whee', 'flarf').code
        assert 0 == prosaic('corpus', 'link', 'whee', 'puke').code
        db.refresh(corpus)
        assert set([puke, flarf]) == set(corpus.sources)

    def test_unlink(self, cleanup, db):
        flarf = Source(name='flarf', description='blah', content='lol naw')
        puke = Source(name='puke', description='blah', content='lol naw')
        corpus = Corpus(name='whee', description='bleh')
        db.add_all([corpus, flarf, puke])
        db.commit()
        prosaic('corpus', 'link', 'whee', 'flarf')
        prosaic('corpus', 'link', 'whee', 'puke')
        db.refresh(corpus)
        assert set([puke, flarf]) == set(corpus.sources)
        assert 0 == prosaic('corpus', 'unlink', 'whee', 'flarf').code
        db.refresh(corpus)
        assert [puke] == corpus.sources
        assert 0 == prosaic('corpus', 'unlink', 'whee', 'puke').code
        db.refresh(corpus)
        assert 0 == len(corpus.sources)

    def test_sources(self, cleanup, db):
        flarf = Source(name='flarf', description='blah', content='lol naw')
        puke = Source(name='puke', description='blah', content='lol naw')
        corpus = Corpus(name='whee', description='bleh')
        db.add_all([corpus, flarf, puke])
        db.commit()
        prosaic('corpus', 'link', 'whee', 'flarf')
        prosaic('corpus', 'link', 'whee', 'puke')
        db.refresh(corpus)
        code, lines = prosaic('corpus', 'sources', 'whee')
        assert 0 == code
        assert set(lines).issuperset(set(['flarf', 'puke']))
        prosaic('corpus', 'unlink', 'whee', 'puke').code
        code, lines = prosaic('corpus', 'sources', 'whee')
        assert 0 == code
        assert lines.issuperset(set(['flarf']))

class TestSourceCommands:
    def test_new_with_desc(self, db, cleanup):
        code, _ = prosaic('source', 'new', 'blargh', TEST_SOURCE_PATH, 'ugh')
        assert 0 == code
        source = db.query(Source).filter(Source.name=='blargh').one()
        assert source.name == 'blargh'
        assert source.description == 'ugh'
        assert len(source.content) > 400
        assert len(source.phrases) > 100

    def test_new_without_desc(self, db, cleanup):
        code, _ = prosaic('source', 'new', 'blargh', TEST_SOURCE_PATH)
        assert 0 == code
        source = db.query(Source).filter(Source.name=='blargh').one()
        assert source.name == 'blargh'
        assert source.description == ''
        assert len(source.content) > 400
        assert len(source.phrases) > 100
        pass

    def test_ls(self, db, cleanup):
        source_names = ['blarf', 'flarf', 'narf']
        for name in source_names:
            db.add(Source(name=name))
        db.commit()
        code, lines = prosaic('source', 'ls')
        assert 0 == code
        assert lines.issuperset(set(source_names))

    def test_rm(self, db, cleanup):
        source_names = ['blarf', 'flarf', 'narf']
        for name in source_names:
            db.add(Source(name=name))
        db.commit()
        assert 3 == db.query(Source).count()
        code, _ = prosaic('source', 'rm', 'flarf')
        assert 0 == code
        code, _ = prosaic('source', 'rm', 'narf')
        assert 0 == code
        assert 1 == db.query(Source).count()

class TestPoemCommands:
    def test_new_with_template(self, db, cleanup):
        script = [['source', 'new', 'flarf', TEST_SOURCE_PATH],
                  ['corpus', 'new', 'puke'],
                  ['corpus', 'link', 'puke', 'flarf']]
        results = map(lambda x: prosaic(*x).code, script)
        assert not any(results)
        code, lines = prosaic('poem', 'new', '-c', 'puke', '-t', 'sonnet')
        assert 0 == code
        assert len(lines) >= 14

    def test_new_with_default_template(self, db, cleanup):
        script = [['source', 'new', 'flarf', TEST_SOURCE_PATH],
                  ['corpus', 'new', 'puke'],
                  ['corpus', 'link', 'puke', 'flarf'],]
        results = map(lambda x: prosaic(*x).code, script)
        assert not any(results)
        code, lines = prosaic('poem', 'new', '-c', 'puke')
        assert 0 == code
        assert len(lines) == 3

class TestTemplateCommands:
    def test_new(self, cleanup):
        assert 0 == prosaic('template', 'new', 'hello').code
        template_path = join(TEST_PROSAIC_HOME, 'templates', 'hello.json')
        lines = open(template_path).readlines()
        assert len(lines) > 1

    def test_ls(self, cleanup):
        prosaic('template', 'new', 'hello')
        code, lines = prosaic('template', 'ls')
        assert 0 == code
        assert len(lines) > 4
        assert 'hello' in lines

    def test_edit(self, cleanup):
        code, lines = prosaic('template', 'edit', 'hello')
        assert 0 == code
        # TODO doing proper output redirection has made this not work, not
        # really sure how to test this now (also need to run the tests with
        # EDITOR=echo
        # assert '/tmp/prosaic_test/templates/hello.json' in lines

    def test_rm(self, cleanup):
        prosaic('template', 'new', 'hello')
        code, _ = prosaic('template', 'rm', 'hello')
        assert 0 == code
        _, lines = prosaic('template', 'ls')
        assert 'hello' not in lines
