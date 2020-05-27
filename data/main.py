import sys
import tempfile
import sqlite3

insert_sql = """
    INSERT INTO data (tok, cnt)
    VALUES (?, 1)
    ON CONFLICT(tok) DO UPDATE SET cnt = cnt + 1;
"""
create_table_sql = """
    CREATE TABLE data(
        tok varchar(255) UNIQUE,
        cnt int)
"""


def main():
    input_file = sys.argv[1]

    with tempfile.NamedTemporaryFile() as tf:
        connection = sqlite3.connect(tf.name)
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        with open(input_file, 'r') as f:
            for line in f:
                for tok in line.split(' '):
                    if tok[0].isalpha():
                        cursor.execute(insert_sql, [tok.lower()])
        cursor.execute("SELECT tok from data ORDER BY cnt DESC LIMIT 100")
        for tok in cursor.fetchall():
            print(tok)


if __name__ == "__main__":
    exit(main())
