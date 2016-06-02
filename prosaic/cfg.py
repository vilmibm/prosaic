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
from os.path import expanduser

from pyhocon import ConfigFactory

DEFAULT_PROSAIC_HOME = expanduser('~/.prosaic')
DEFAULT_TEMPLATE = 'haiku'
DEFAULT_DB = {'user': 'prosaic',
              'password': 'prosaic',
              'host': '127.0.0.1',
              'port': 5432,
              'dbname': 'prosaic'}

DEFAULT_CONFIG = """database: {{
    user: {user}
    password: {password}
    host: {host}
    port: {port}
    dbname: {dbname}
}}
default_template: {default_tmpl}
""".format(default_tmpl=DEFAULT_TEMPLATE,
           user=DEFAULT_DB['user'],
           password=DEFAULT_DB['password'],
           port=DEFAULT_DB['port'],
           host=DEFAULT_DB['host'],
           dbname=DEFAULT_DB['dbname'],)

def read_config(cfgpath):
    return ConfigFactory.parse_file(cfgpath)
