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
from functools import lru_cache
from sqlalchemy import create_engine, Column, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, INTEGER
from sqlalchemy.ext.declarative import declarative_base

# TODO rebuild venv outside of prosaic src

class Database(dict):
    def __init__(self, user='prosaic', password='prosaic', host='localhost',
                 port=5432, dbname='prosaic'):
        self._data = dict(user=user, password=password, port=port,
                          host=host, dbname=dbname)

    def __getattr__(self, k):
        return self[k]

    def __getitem__(self, k):
        return self._data[k]

    def _fmt(self):
        return ';'.join(sorted(map(str, self._data.values())))

    def __hash__(self):
        return hash(self._fmt())

    def __repr__(self):
        return self._fmt()

@lru_cache(maxsize=128)
def get_engine(db: Database) -> Engine:
    return create_engine('postgresql://{user}:{password}@{host}:{port}/{dbname}'\
           .format(**db))

Session = sessionmaker()

def get_session(db: Database):
    Session.configure(bind=get_engine(db))
    return Session()

Base = declarative_base()

corpora_sources = Table('corpora_sources', Base.metadata,
                       Column('corpus_id', INTEGER, ForeignKey('corpora.id')),
                       Column('source_id', INTEGER, ForeignKey('sources.id')))

def migrate(db: Database):
    Base.metadata.create_all(get_engine(db))

class Source(Base):
    __tablename__ = "sources"

    id = Column(INTEGER, primary_key=True)
    # TODO Needs to be unique and not nil
    name = Column(TEXT)
    description = Column(TEXT)
    content = Column(TEXT)

class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(INTEGER, primary_key=True)
    stems = Column(ARRAY(TEXT))
    raw = Column(TEXT)
    alliteration = Column(Boolean)
    rhyme_sound = Column(TEXT)
    syllables = Column(INTEGER)
    line_no = Column(INTEGER)
    source_id = Column(INTEGER, ForeignKey('sources.id'))

    source = relationship('Source', back_populates='phrases')

    # TODO This just isn't working :(
    # I realized though that I wasn't even using these in rules. I'll circle
    # back on these once I have a compelling reason to do so.
    #phonemes = Column(ARRAY(TEXT, dimensions=2))
    #tagged = Column(ARRAY(TEXT, dimensions=2))

    def __repr__(self) -> str:
        return "Phrase(raw='%s', source='%s')" % (self.raw, self.source.name)

Source.phrases = relationship('Phrase', back_populates='source')

class Corpus(Base):
    __tablename__ = "corpora"

    id = Column(INTEGER, primary_key=True)
    # TODO Needs to be unique and not nil
    name = Column(TEXT)
    description = Column(TEXT)

    sources = relationship('Source', secondary=corpora_sources)
