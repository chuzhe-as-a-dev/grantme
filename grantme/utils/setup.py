import sqlite3
from pathlib import Path

from grantme.constants.sqls import CREATE_DB, CREATE_INDEX


def create_db(data_dir: Path, db_file: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    setup_db(conn)
    conn.close()

    # make db writable to everyone; the directory must be writable as well since
    # sqlite creates and deletes journal files next to the db file
    data_dir.chmod(0o777)
    db_file.chmod(0o666)


def setup_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(CREATE_DB)
    cur.execute(CREATE_INDEX)
    cur.close()
    conn.commit()
