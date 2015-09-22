#!/usr/bin/env python
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
import sys
from argparse import ArgumentParser, FileType
from os.path import join, exists, dirname

from sh import cp, mkdir

import prosaic.commands as cmd
from prosaic.cfg import PROSAIC_HOME, TEMPLATES, MONGO_HOST, MONGO_PORT, DEFAULT_DB

# TODO for love of god put this in readme, not here:
## CLI UI

## prosaic poem new -h <host> -p <port> -d <db> -t <tmpl> -o <name>
## prosaic corpus ls -hpd
## prosaic corpus loadfile -h <host> -p <port> -d <db> <filename>
## prosaic corpus rm -h <host> -p <port> -d <db>
## prosaic template new <name>
## prosaic template ls
## prosaic template rm <name>

def is_installed():
    return all(map(exists, [PROSAIC_HOME,
                            join(PROSAIC_HOME, 'templates')]))

def install():
    template_source = join(dirname(sys.modules['prosaic'].__file__), 'templates')
    mkdir(PROSAIC_HOME)
    cp('-r', template_source, PROSAIC_HOME)

class ProsaicArgParser(ArgumentParser):
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

    def add_argument(self, *args, **kwargs):
        '''literally just here for chaining lol'''
        super().add_argument(*args, **kwargs)
        return self

    def set_defaults(self, *args, **kwargs):
        '''literally just here for chaining lol'''
        super().set_defaults(*args, **kwargs)
        return self

def init_arg_parser():
    top_level_parser = ProsaicArgParser(prog='prosaic')
    subparsers = top_level_parser.add_subparsers()

    corpus_parser = subparsers.add_parser('corpus')
    corpus_subs = corpus_parser.add_subparsers()

    poem_parser = subparsers.add_parser('poem')
    poem_subs = poem_parser.add_subparsers()

    template_parser = subparsers.add_parser('template')
    template_subs = template_parser.add_subparsers()

    top_level_parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin)

    # corpus commands
    corpus_subs.add_parser('ls').set_defaults(func=cmd.corpus_ls).add_db()
    corpus_subs.add_parser('loadfile') \
               .set_defaults(func=cmd.corpus_loadfile) \
               .add_argument('path', action='store') \
               .add_db()
    corpus_subs.add_parser('rm') \
               .set_defaults(func=cmd.corpus_rm) \
               .add_dbhost() \
               .add_dbport() \
               .add_argument('dbname', default=DEFAULT_DB, action='store')

    # poem commands
    poem_subs.add_parser('new') \
             .set_defaults(func=cmd.poem_new) \
             .add_argument('-r', '--tmpl_raw', action='store_true') \
             .add_argument('-o', '--output', action='store') \
             .add_argument('-t', '--tmpl', action='store', default='haiku') \
             .add_db()

    # template commands
    template_subs.add_parser('ls').set_defaults(func=cmd.template_ls)
    template_subs.add_parser('rm') \
                 .set_defaults(func=cmd.template_rm) \
                 .add_argument('tmplname', action='store')
    template_subs.add_parser('new') \
                 .set_defaults(func=cmd.template_new) \
                 .add_argument('tmplname', action='store')
    template_subs.add_parser('edit') \
                 .set_defaults(func=cmd.template_edit) \
                 .add_argument('tmplname', action='store')

    return top_level_parser

def main():
    if not is_installed():
        install()

    argument_parser = init_arg_parser()
    parsed_args = argument_parser.parse_args()
    # TODO try/except for bad subcommand
    parsed_args.func(parsed_args)
    return 0

if __name__ == '__main__': sys.exit(main())
