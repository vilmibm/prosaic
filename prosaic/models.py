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
from sqlalchemy import create_engine, Column, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, INTEGER
from sqlalchemy.ext.declarative import declarative_base

# TODO rebuild venv outside of prosaic src

def db_engine(username: str, password: str, dbhost: str, dbname: str) -> Engine:
    return create_engine('postgresql://{}:{}@{}/{}'.format(username, password, dbhost, dbname))

# TODO this is hardcoded, shouldn't be
engine = db_engine('vilmibm', 'foobar', 'localhost', 'prosaic')

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"

    id = Column(INTEGER, primary_key=True)
    name = Column(TEXT)
    description = Column(TEXT)
    content = Column(TEXT)

    phrases = relationship('Phrase', back_populates='sources')

class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(INTEGER, primary_key=True)
    stems = Column(ARRAY(TEXT))
    raw = Column(TEXT)
    alliteration = Column(Boolean)
    rhyme_sound = Column(TEXT)
    phonemes = Column(ARRAY(TEXT))
    syllables = Column(INTEGER)
    line_no = Column(INTEGER)

    source = relationship('Source', back_populates='phrases')

    # TODO Need to think about this:
    # tagged = Column(ARRAY(ARRAY(TEXT)))

    def __repr__(self) -> str:
        return "Phrase(raw='%s', source='%s')" % (self.raw, self.source.name)

class Corpus(Base):
    __tablename__ = "corpora"

    id = Column(INTEGER, primary_key=True)
    name = Column(TEXT)

    source = relationship('Source')
