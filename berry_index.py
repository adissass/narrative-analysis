import sqlite3

def update_berry_index():
    conn = sqlite3.connect("data_store.db")

    # compute total delta per character
    rows = conn.execute("""
        SELECT character, SUM(delta) AS total_delta
        FROM impact_log
        GROUP BY character;
    """).fetchall()

    # update or insert each total
    for char, total in rows:
        conn.execute("""
            INSERT INTO berry_index (character, total_delta)
            VALUES (?, ?)
            ON CONFLICT(character)
            DO UPDATE SET
                total_delta = excluded.total_delta,
                last_updated = CURRENT_TIMESTAMP;
        """, (char, total))

    conn.commit()
    conn.close()
    print("[OK] Berry Index updated.")

if __name__ == "__main__":
    update_berry_index()