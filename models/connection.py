from sqlalchemy import create_engine

from config import DATABASE_URL

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

engine = create_engine(DATABASE_URL)


def get_connection() -> None:
    connection = engine.connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
