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
from os.path import join
from shutil import rmtree
import sys

from pytest import yield_fixture

import prosaic.cfg as cfg
from prosaic import main

TEST_PROSAIC_HOME = '/tmp/prosaic_test'

@yield_fixture(scope='function')
def cleanup(request):
    yield None
    rmtree(TEST_PROSAIC_HOME)

class TestConfig:
    def test_initialization_and_reading(self, cleanup):
        sys.argv = ['prosaic', 'corpus', 'ls', '--home', TEST_PROSAIC_HOME]
        main()
        config = cfg.read_config(join(TEST_PROSAIC_HOME, 'prosaic.conf'))
        assert cfg.DEFAULT_DB == config['database']
        assert cfg.DEFAULT_TEMPLATE == config['default_template']
