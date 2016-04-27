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
from sqlalchemy import create_engine, Engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# TODO rebuild venv outside of prosaic src

def db_engine(username: str, dbhost: str, dbname: str) -> Engine:
    return "postgresql://{}@{}/{}".format(username, dbhost, dbname))

# TODO this is hardcoded, shouldn't be
engine = db_engine("vilmibm", "localhost", "prosaic")

# TODO should this live here?
Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)

class Phrase(Base):
    ## stems: array of text
    ## source: FK to sources
    ## tagged: array of POS tags
    ## rhyme_sound: text
    ## phonemes: array of text
    ## syllables: integer
    ## line_no: integer
    ## alliteration: bool
    ## raw: text
    ## blank: bool
    pass

class Corpus(Base):
    ## name: text
    ## source: FK to sources
    pass
