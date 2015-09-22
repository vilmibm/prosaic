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
from json import loads
from os import environ, listdir
from os.path import join
from subprocess import call

from pymongo import MongoClient
from sh import rm, cp

from prosaic.nyarlathotep import process_text
from prosaic.cthulhu import poem_from_template
from prosaic.cfg import DEFAULT_TEMPLATE_EXT, TEMPLATES, EXAMPLE_TEMPLATE
from prosaic.util import slurp

# TODO refactor all of this stuff to be in the ProsaicArgParser class.

def read_template(name):
    if name.startswith('/'):
        path = name
    else:
        path = join(TEMPLATES, '{}.{}'.format(name, DEFAULT_TEMPLATE_EXT))
    return slurp(path)

def args_to_template(parsed_args):
    if parsed_args.tmpl_raw:
        template = ''.join(parsed_args.infile.readlines())
    else:
        template = read_template(parsed_args.tmpl)

    return loads(template)

def args_to_client(parsed_args):
    return MongoClient(parsed_args.host, parsed_args.port)

def args_to_db(parsed_args):
    client = args_to_client(parsed_args)
    return client[parsed_args.dbname].phrases

def corpus_ls(parsed_args):
    client = args_to_client(parsed_args)
    for dbname in client.database_names():
        print(dbname)

def corpus_rm(parsed_args):
    client = args_to_client(parsed_args)
    client.drop_database(parsed_args.dbname)

def corpus_loadfile(parsed_args):
    db = args_to_db(parsed_args)
    path = parsed_args.path
    # TODO stream this, don't slurp it.
    text = slurp(path)
    return process_text(text, path, db)

def poem_new(parsed_args):
    template = args_to_template(parsed_args)
    db = args_to_db(parsed_args)
    poem_lines = poem_from_template(template, db)
    output_filename = parsed_args.output
    if output_filename:
        with open(output_filename, 'w') as f:
            f.write(map(lambda l: l.get('raw'), poem_lines).join('\n') + '\n')
            print('poem written to {}'.format(output_filename))
    else:
        for line in poem_lines:
            print(line.get('raw'))

def abs_template_path(parsed_args):
    template_name = parsed_args.tmplname
    return join(TEMPLATES, '{}.{}'.format(template_name, DEFAULT_TEMPLATE_EXT))

def template_ls(parsed_args):
    template_files = filter(lambda s: not s.startswith('.'), listdir(TEMPLATES))
    # TODO this will be weird once we support non json templates:
    without_ext = map(lambda s: s.replace('.' + DEFAULT_TEMPLATE_EXT, ''), template_files)
    for filename in without_ext:
        print(filename)

def template_rm(parsed_args):
    template_abspath = abs_template_path(parsed_args)
    rm(template_abspath)

def template_new(parsed_args):
    template_abspath = abs_template_path(parsed_args)
    editor = environ.get('EDITOR', 'vi')
    cp(EXAMPLE_TEMPLATE, template_abspath)
    call([editor, template_abspath])

def template_edit(parsed_args):
    template_abspath = abs_template_path(parsed_args)
    editor = environ.get('EDITOR', 'vi')
    call([editor, template_abspath])
