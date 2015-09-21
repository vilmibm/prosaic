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
from os import environ
from os.path import expanduser, join

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DEFAULT_DB = 'prosaic'
PROSAIC_HOME = environ.get('PROSAIC_HOME', join(expanduser('~'), '.prosaic'))
DEFAULT_TEMPLATE = 'haiku'
# TODO support for hocon (.conf)
DEFAULT_TEMPLATE_EXT = 'json'
TEMPLATES = join(PROSAIC_HOME, 'templates')
EXAMPLE_TEMPLATE = join(TEMPLATES, '.example.template')
