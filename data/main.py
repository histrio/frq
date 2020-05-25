import tempfile


def main():

    with tempfile.NamedTemporaryFile() as tf:
        import sqlite3
        connection = sqlite3.connect(tf.name)
        cursor = connection.cursor()
        create_table_sql = """
            CREATE TABLE data(
                tok varchar(255) UNIQUE,
                cnt int)
        """
        cursor.execute(create_table_sql)
        with open('cs.tok', 'r') as f:
            for line in f:
                for tok in line.split(' '):
                    insert_sql = """
                        INSERT INTO data (tok, cnt)
                        VALUES (?, 1)
                        ON CONFLICT(tok) DO UPDATE SET cnt = cnt + 1;
                    """
                    cursor.execute(insert_sql, [tok.lower()])
        cursor.execute("""
        SELECT * from data
        LIMIT 100 ORDER BY cnt DESC
        """)
        print(list(cursor.fetch_all()))


if __name__ == "__main__":
    exit(main())
