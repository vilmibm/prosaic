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

from pymongo import MongoClient
from sh import rm, cp

from prosaic.nyarlathotep import process_text
from prosaic.cthulhu import poem_from_template
from prosaic.cfg import DEFAULT_TEMPLATE_EXT, TEMPLATES, EXAMPLE_TEMPLATE, MONGO_HOST, MONGO_PORT, DEFAULT_DB
from prosaic.util import slurp

class ProsaicArgParser(ArgumentParser):
    editor = environ.get('EDITOR')
    _template = None
    _client = None


    # Helpers and properties:

    @property
    def client(self):
        if not self.args:
            return None
        return self._client if self._client else MongoClient(self.args.host, self.args.port)

    @property
    def db(self):
        if not self.args:
            return None
        return self.client[self.args.dbname].phrases

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
        self.add_argument('--host', action='store', default=MONGO_HOST)
        return self

    def add_dbport(self):
        self.add_argument('-p', '--port', action='store', default=MONGO_PORT)
        return self

    def add_dbname(self):
        self.add_argument('-d', '--dbname', action='store', default=DEFAULT_DB)
        return self

    def add_db(self):
        self.add_dbhost().add_dbport().add_dbname()
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
        for dbname in self.client.database_names():
            print(dbname)

    def corpus_rm(self):
        self.client.drop_database(self.args.dbname)

    def corpus_loadfile(self):
        # TODO stream this, don't slurp it.
        text = slurp(self.args.path)
        return process_text(text, self.args.path, self.db)

    def poem_new(self):
        template = self.template
        poem_lines = poem_from_template(self.template, self.db)
        output_filename = self.args.output
        if output_filename:
            with open(output_filename, 'w') as f:
                f.write(map(lambda l: l.get('raw'), poem_lines).join('\n') + '\n')
                print('poem written to {}'.format(output_filename))
        else:
            for line in poem_lines:
                print(line.get('raw'))

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
        # TODO try catch
        try:
            self.args.func()
        except AttributeError:
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
               .add_argument('dbname', default=DEFAULT_DB, action='store')

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
