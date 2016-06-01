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
from argparse import ArgumentParser
from json import loads
import logging
from os import environ, listdir, remove
from os.path import join, exists
from shutil import copyfile
from subprocess import call
import sys

from sqlalchemy import text

from prosaic.models import Source, Corpus, get_session, get_engine, Database
from prosaic.parsing import process_text
from prosaic.generation import poem_from_template
import prosaic.cfg as cfg
from prosaic.util import slurp, first

log = logging.getLogger('prosaic')

# TODO add aliases (as specified in cli.md)
class ProsaicArgParser(ArgumentParser):
    editor = environ.get('EDITOR')
    _template = None
    _db = None
    _corpus = None

    # Helpers and properties:

    def __init__(self, prog=None):
        super().__init__(prog=prog)
        self.add_argument('--home', action='store', default=cfg.DEFAULT_PROSAIC_HOME)
        self.add_argument('-v', '--verbose', action='store_true')

    def get_corpus(self, session) -> Corpus:
        corpus = session.query(Corpus)\
                   .filter(Corpus.name == self.args.corpus_name)\
                   .one_or_none()

        if corpus is None:
            raise Exception('No such corpus found.')

        return corpus

    @property
    def template_path(self):
        return join(self.args.home, 'templates')

    @property
    def engine(self):
        return get_engine(self.db)

    @property
    def db(self) -> Database:
        if self._db:
            return self._db

        self._db = Database(**self.config['database'])
        return self._db

    @property
    def template(self):
        """Returns the template in JSON form"""
        if self._template:
            return self._template

        template_json = self.read_template(self.args.tmplname)

        self._template = loads(template_json)
        return self._template

    @property
    def template_abspath(self):
        """Returns the absolute path to the template"""
        return join(self.template_path, '{}.{}'.format(self.args.tmplname, 'json'))

    def add_corpus(self):
        self.add_argument('-c', '--corpus', action='store')
        return self

    def read_template(self, filename):
        if filename.startswith('/'):
            path = filename
        else:
            path = self.template_abspath

        return slurp(path)

    # Chaning helpers:

    def add_argument(self, *args, **kwargs):
        super().add_argument(*args, **kwargs)
        return self

    def set_defaults(self, *args, **kwargs):
        super().set_defaults(*args, **kwargs)
        return self

    # Actually define commands:

    def corpus_ls(self):
        session = get_session(self.db)
        for name in session.query(Corpus.name):
            print(first(name))

    def corpus_rm(self):
        conn = self.engine.connect()
        unlink_sql = """
        delete from corpora_sources
        where corpus_id = :corpus_id
        """
        # TODO there is a bug here until corpusname is unique
        delete_sql = """
        delete from corpora
        where name = :corpus_name
        """
        session = get_session(self.db)
        corpus = self.get_corpus(session)
        conn.execute(text(unlink_sql).params(corpus_id=corpus.id))
        conn.execute(text(delete_sql).params(corpus_name=self.args.corpus_name))

    def corpus_link(self):
        session = get_session(self.db)
        corpus = self.get_corpus(session)
        source = session.query(Source).filter(Source.name==self.args.source_name).one()
        corpus.sources.append(source)
        session.add(corpus)
        session.commit()

    def corpus_unlink(self):
        session = get_session(self.db)
        corpus = self.get_corpus(session)
        source = session.query(Source).filter(Source.name==self.args.source_name).one()
        corpus.sources.remove(source)
        session.add(corpus)
        session.commit()

    def corpus_new(self):
        session = get_session(self.db)
        corpus = Corpus(name=self.args.corpus_name,
                        description=self.args.corpus_desc)
        session.add(corpus)
        session.commit()

    def corpus_sources(self):
        session = get_session(self.db)
        corpus = self.get_corpus(session)
        if 0 == len(corpus.sources):
            log.error("Corpus {} has no sources.".format(corpus.name))
            log.error("Use `prosaic corpus link 'corpus name' 'source name'` to add sources")
        for source in corpus.sources:
            print(source.name)

    def source_ls(self):
        session = get_session(self.db)
        for name in session.query(Source.name):
            print(first(name))

    def source_rm(self):
        # ugh i know; TODO figure out how to do this with ORM
        conn = self.engine.connect()
        session = get_session(self.db)
        unlink_sql = """
        delete from corpora_sources
        where source_id = :source_id
        """
        # TODO bug until source name is unique
        source_delete_sql = """
        delete from sources
        where name = :source_name
        """
        phrase_delete_sql = """
        delete from phrases
        where source_id = :source_id
        """
        name = self.args.source_name
        source_id = first(session.query(Source.id).filter(Source.name == name).one())
        conn.execute(text(unlink_sql).params(source_id=source_id))
        conn.execute(text(phrase_delete_sql).params(source_id=source_id))
        conn.execute(text(source_delete_sql).params(source_name=name))

    def source_new(self):
        # TODO slurpin's bad; would be better to fully pipeline parsing from
        # file -> processing -> db, with threading.
        text = slurp(self.args.path)
        name = self.args.source_name
        description = self.args.source_description
        source = Source(name=name, description=description)

        process_text(self.db, source, text)

    def poem_new(self):
        session = get_session(self.db)
        corpus = self.get_corpus(session)
        if 0 == len(corpus.sources):
            log.error("Corpus {} has no sources.".format(corpus.name))
            log.error("Use `prosaic corpus link 'corpus name' 'source name'` to add sources")
            return
        template = self.template
        poem_lines = map(first, poem_from_template(self.template, self.db, corpus.id))
        output_filename = self.args.output
        if output_filename:
            with open(output_filename, 'w') as f:
                f.write(list(poem_lines).join('\n') + '\n')
                log.debug('poem written to {}'.format(output_filename))
        else:
            for line in poem_lines:
                print(line)

    def template_ls(self):
        template_files = filter(lambda s: not s.startswith('.'), listdir(self.template_path))
        # TODO this will be weird once we support non json templates:
        without_ext = map(lambda s: s.replace('.json', ''), template_files)
        for filename in without_ext:
            print(filename)

    def template_rm(self):
        remove(self.template_abspath)

    def template_new(self):
        example_template = join(self.template_path, '.example.template')
        copyfile(example_template, self.template_abspath)
        call([self.editor, self.template_abspath])

    def template_edit(self):
        if not exists(self.template_abspath):
            example_template = join(self.template_path, '.example.template')
            copyfile(example_template, self.template_abspath)
        call([self.editor, self.template_abspath])

    def dispatch(self, args, config):
        self.args = args
        self.config = config

        if getattr(self.args, 'tmplname', None) is None:
            self.args.tmplname = self.config.get('default_template', cfg.DEFAULT_TEMPLATE)

        try:
            self.args.func()
        except AttributeError as e:
            log.error('prosaic experienced a fatal error: {}'.format(e))
            self.print_help()
            return 1

        return 0

def initialize_arg_parser():
    parser = ProsaicArgParser()
    subparsers = parser.add_subparsers()

    corpus_parser = subparsers.add_parser('corpus')
    corpus_subs = corpus_parser.add_subparsers()

    source_parser = subparsers.add_parser('source')
    source_subs = source_parser.add_subparsers()

    poem_parser = subparsers.add_parser('poem')
    poem_subs = poem_parser.add_subparsers()

    template_parser = subparsers.add_parser('template')
    template_subs = template_parser.add_subparsers()

    # corpus commands
    corpus_subs.add_parser('ls')\
            .set_defaults(func=parser.corpus_ls)
    corpus_subs.add_parser('new')\
            .set_defaults(func=parser.corpus_new)\
            .add_argument('corpus_name', action='store')\
            .add_argument('corpus_desc', action='store', default='', nargs='?')
    corpus_subs.add_parser('link')\
            .set_defaults(func=parser.corpus_link)\
            .add_argument('corpus_name', action='store')\
            .add_argument('source_name', action='store', default='', nargs='?')
    corpus_subs.add_parser('unlink')\
            .set_defaults(func=parser.corpus_unlink)\
            .add_argument('corpus_name', action='store')\
            .add_argument('source_name', action='store')
    corpus_subs.add_parser('sources')\
            .set_defaults(func=parser.corpus_sources)\
            .add_argument('corpus_name', action='store')
    corpus_subs.add_parser('rm')\
            .set_defaults(func=parser.corpus_rm)\
            .add_argument('corpus_name', action='store')

    # source commands
    source_subs.add_parser('ls')\
            .set_defaults(func=parser.source_ls)
    source_subs.add_parser('rm')\
            .set_defaults(func=parser.source_rm)\
            .add_argument('source_name', action='store')
    source_subs.add_parser('new')\
            .set_defaults(func=parser.source_new)\
            .add_argument('source_name', action='store')\
            .add_argument('path', action='store')\
            .add_argument('source_description', action='store', default='', nargs='?')

    # poem commands
    poem_subs.add_parser('new') \
             .set_defaults(func=parser.poem_new) \
             .add_argument('-c', '--corpus', dest='corpus_name', action='store')\
             .add_argument('-o', '--output', action='store') \
             .add_argument('-t', '--tmplname', action='store', default=None) \

    # template commands
    template_subs.add_parser('ls')\
                 .set_defaults(func=parser.template_ls)
    template_subs.add_parser('rm') \
                 .set_defaults(func=parser.template_rm) \
                 .add_argument('tmplname', action='store')
    template_subs.add_parser('new') \
                 .set_defaults(func=parser.template_new) \
                 .add_argument('tmplname', action='store')
    template_subs.add_parser('edit') \
                 .set_defaults(func=parser.template_edit) \
                 .add_argument('tmplname', action='store')

    return parser
