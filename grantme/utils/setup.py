from pathlib import Path
import sqlite3

from grantme.constants.sqls import CREATE_DB, CREATE_INDEX


def create_db(data_dir: Path, db_file: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    setup_db(conn)
    conn.close()

    # make db accessible to everyone
    data_dir.chmod(data_dir.stat().st_mode | 0o666)
    db_file.chmod(db_file.stat().st_mode | 0o666)


def setup_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(CREATE_DB)
    cur.execute(CREATE_INDEX)
    cur.close()
    conn.commit()
