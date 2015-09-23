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
from os.path import join, exists, dirname

from sh import cp, mkdir

import prosaic.commands as cmd
from prosaic.cfg import PROSAIC_HOME, DEFAULT_DB

def is_installed():
    return all(map(exists, [PROSAIC_HOME,
                            join(PROSAIC_HOME, 'templates')]))

def install():
    template_source = join(dirname(sys.modules['prosaic'].__file__), 'templates')
    mkdir(PROSAIC_HOME)
    cp('-r', template_source, PROSAIC_HOME)

def main():
    if not is_installed():
        install()

    return cmd.initialize_arg_parser().dispatch()

if __name__ == '__main__': sys.exit(main())
