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
from os import mkdir
from os.path import join, exists, dirname, expanduser
from shutil import copytree

import prosaic.commands as cmd
from prosaic.cfg import read_config

def main():
    parser = cmd.initialize_arg_parser()
    args = parser.parse_args()
    prosaic_home = parser.args.home
    cfgpath = join(prosaic_home, 'prosaic.conf')
    tmplpath = join(prosaic_home, 'templates')

    if not exists(prosaic_home):
        mkdir(prosaic_home)

    if not exists(tmplpath):
        prosaic_install_path = dirname(sys.modules['prosaic'].__file__)
        template_source = join(prosaic_install_path, 'templates')
        copytree(template_source, tmplpath)

    if not exists(cfgpath):
        with open(cfgpath) as f:
            f.write(cfg.DEFAULT_CONFIG)

    config = read_config(cfgpath)

    parser.dispatch(args, config)

if __name__ == '__main__':
    sys.exit(main())
