import logging
from platformdirs import user_log_path

logs_path = user_log_path("gucken", ensure_exists=True)


def setup_sqlalchemy():
    logger = logging.getLogger("sqlalchemy")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        filename=logs_path.joinpath("sqlalchemy.log"),
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        fmt="[%(asctime)s %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)
    logger.propagate = False


def setup_global():
    logging.basicConfig(
        filename=logs_path.joinpath("gucken.log"),
        encoding="utf-8",
        level=logging.DEBUG,
        force=True,
        format="[%(asctime)s %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def setup():
    setup_global()
    setup_sqlalchemy()
