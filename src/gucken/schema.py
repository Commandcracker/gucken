"""
Data structures, used in project.

You may do changes in tables here, then execute
`alembic revision --message="Your text" --autogenerate`
and alembic would generate new migration for you
in staff/alembic/versions folder.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, MetaData
from sqlalchemy.orm import declarative_base


# Default naming convention for all indexes and constraints
# See why this is important and how it would save your time:
# https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(table_name)s__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': (
        'fk__%(table_name)s__%(all_column_names)s__'
        '%(referred_table_name)s'
    ),
    'pk': 'pk__%(table_name)s'
}

# Registry for all tables
metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class Anime(Base):
    __tablename__ = 'anime'

    anime_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    provider = Column(String, nullable=False)
    name = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"Anime(anime_id={self.anime_id!r}, provider={self.provider!r}, name={self.name!r})"


class Watchtime(Base):
    __tablename__ = 'watchtime'

    #watchtime_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    anime_id = Column(Integer, ForeignKey('anime.anime_id'), primary_key=True, nullable=False)
    episode = Column(Integer, primary_key=True, nullable=False)
    season = Column(Integer, primary_key=True, nullable=False)
    time = Column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"Watchtime(watchtime_id={self.watchtime_id!r}, anime_id={self.anime_id!r}, episode={self.episode!r}, season={self.season!r}, time={self.time!r})"