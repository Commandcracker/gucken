from pathlib import Path
import sys

from alembic.config import Config
from alembic import command
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from platformdirs import user_data_path

from gucken._logging import logs_path


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


class SingletonEngine(Singleton):
    def __init__(self):
        alembic_cfg = Config(Path(__file__).parent.joinpath("alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(Path(__file__).parent.joinpath("alembic")))

        db_path = user_data_path("gucken").joinpath("data.db")
        self.engine = create_engine(f"sqlite:///{db_path}", echo=True)

        _stderr = sys.stderr
        sys.stderr = logs_path.joinpath("alembic.log").open("a")
        command.upgrade(alembic_cfg, "head")
        sys.stderr.close()
        sys.stderr = _stderr


engine = SingletonEngine().engine
Session = sessionmaker(bind=engine)
