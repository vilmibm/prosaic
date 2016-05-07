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
from argparse import ArgumentParser, FileType
from json import loads
from os import environ, listdir
from os.path import join
from subprocess import call
import sys

from sqlalchemy import text
from sh import rm, cp

from prosaic.models import Source, Corpus, get_session, get_engine, Database
from prosaic.parsing import process_text
from prosaic.generation import poem_from_template
from prosaic.cfg import DEFAULT_TEMPLATE_EXT, TEMPLATES, EXAMPLE_TEMPLATE, PG_HOST, PG_PORT, PG_USER, PG_PASS,DEFAULT_DB
from prosaic.util import slurp, first

class ProsaicArgParser(ArgumentParser):
    editor = environ.get('EDITOR')
    _template = None
    _db = None
    _corpus = None

    # Helpers and properties:

    @property
    def corpus(self):
        if self._corpus is not None:
            return self._corpus


        self._corpus = self.session.query(Corpus)\
                       .filter(Corpus.name == self.args.corpus)\
                       .one_or_none()

        if self._corpus is None:
            print('creating new corpus {}...'.format(self.args.corpus))
            self._corpus = Corpus(name=self.args.corpus)
            self.session.add(self._corpus)
            self.session.commit()

        if self.args.corpus == '_prosaic':
            print('updating default corpus...')
            self._corpus.sources = self.session.query(Source).all()
            self.session.add(self._corpus)
            self.session.commit()

        return self._corpus

    @property
    def session(self):
        return get_session(self.db)

    @property
    def engine(self):
        return get_engine(self.db)

    @property
    def db(self) -> Database:
        if self._db:
            return self._db

        self._db = Database(user=self.args.user,
                            password=self.args.password,
                            host=self.args.host,
                            dbname=self.args.dbname,
                            port=self.args.port)
        return self._db

    @property
    def template(self):
        if not self.args:
            return None

        if self._template:
            return self._template

        if self.args.tmpl_raw:
            template_path = ''.join(self.args.infile.readlines())
        else:
            template_path = self.read_template(self.args.tmpl)

        self._template = loads(template_path)
        return self._template

    @property
    def template_abspath(self):
        if not self.args:
            return None
        return join(TEMPLATES, '{}.{}'.format(self.args.tmplname, DEFAULT_TEMPLATE_EXT))

    def add_dbhost(self):
        self.add_argument('--host', action='store', default=PG_HOST)
        return self

    def add_dbpass(self):
        self.add_argument('--password', action='store', default=PG_PASS)
        return self

    def add_dbuser(self):
        self.add_argument('--user', action='store', default=PG_USER)
        return self

    def add_dbport(self):
        self.add_argument('-p', '--port', action='store', default=PG_PORT)
        return self

    def add_dbname(self):
        self.add_argument('-d', '--dbname', action='store', default=DEFAULT_DB)
        return self

    def add_corpus(self):
        self.add_argument('-c', '--corpus', action='store', default='_prosaic')
        return self

    def add_db(self):
        self.add_dbhost().add_dbport().add_dbname().add_dbuser().add_dbpass().add_corpus()
        return self

    def read_template(self, filename):
        if filename.startswith('/'):
            path = filename
        else:
            path = join(TEMPLATES, '{}.{}'.format(filename, DEFAULT_TEMPLATE_EXT))

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
        session = self.session
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
        conn.execute(text(unlink_sql).params(corpus_id=self.corpus.id))
        conn.execute(text(delete_sql).params(corpus_name=self.corpus.name))

    def corpus_loadfile(self):
        # TODO stream this, don't slurp it.
        text = slurp(self.args.path)
        corpus = self.corpus
        return process_text(text, self.args.path, corpus, self.db)

    def poem_new(self):
        template = self.template
        poem_lines = map(first, poem_from_template(self.template, self.db, self.corpus))
        output_filename = self.args.output
        if output_filename:
            with open(output_filename, 'w') as f:
                f.write(list(poem_lines).join('\n') + '\n')
                print('poem written to {}'.format(output_filename))
        else:
            for line in poem_lines:
                print(line)

    def template_ls(self):
        template_files = filter(lambda s: not s.startswith('.'), listdir(TEMPLATES))
        # TODO this will be weird once we support non json templates:
        without_ext = map(lambda s: s.replace('.' + DEFAULT_TEMPLATE_EXT, ''), template_files)
        for filename in without_ext:
            print(filename)

    def template_rm(self):
        rm(self.template_abspath)

    def template_new(self):
        cp(EXAMPLE_TEMPLATE, self.template_abspath)
        call([self.editor, self.template_abspath])

    def template_edit(self):
        call([self.editor, self.template_abspath])

    def dispatch(self):
        self.args = self.parse_args()
        try:
            self.args.func()
        except AttributeError as e:
            print('Caught fatal error: {}'.format(e))
            self.print_help()
            return 1

        return 0

def initialize_arg_parser():
    parser = ProsaicArgParser()
    subparsers = parser.add_subparsers()

    corpus_parser = subparsers.add_parser('corpus')
    corpus_subs = corpus_parser.add_subparsers()

    poem_parser = subparsers.add_parser('poem')
    poem_subs = poem_parser.add_subparsers()

    template_parser = subparsers.add_parser('template')
    template_subs = template_parser.add_subparsers()

    parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin)

    # corpus commands
    corpus_subs.add_parser('ls').set_defaults(func=parser.corpus_ls).add_db()
    corpus_subs.add_parser('loadfile') \
               .set_defaults(func=parser.corpus_loadfile) \
               .add_argument('path', action='store') \
               .add_db()
    corpus_subs.add_parser('rm') \
               .set_defaults(func=parser.corpus_rm) \
               .add_dbhost() \
               .add_dbport() \
               .add_dbuser() \
               .add_dbname() \
               .add_dbpass() \
               .add_argument('corpus', action='store')

    # poem commands
    poem_subs.add_parser('new') \
             .set_defaults(func=parser.poem_new) \
             .add_argument('-r', '--tmpl_raw', action='store_true') \
             .add_argument('-o', '--output', action='store') \
             .add_argument('-t', '--tmpl', action='store', default='haiku') \
             .add_db()

    # template commands
    template_subs.add_parser('ls').set_defaults(func=parser.template_ls)
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
