import analyze_run as parser
import sqlite3
import json
import os

CHAR_DIR = "characters"
REFRESH_MODE = True  # False = full rebuild, True = only process new agendas

# Maps sentiment strings to numeric values
sentiment_map = {"great" : 2,"good": 1, "neutral": 0, "bad": -1,"horrible": -2 }

def process_agenda(text, subject, bio):
    """Use parser to extract structured event data from agenda text."""
    try:
        result = parser.parse_agenda(text, subject, bio)
        if isinstance(result, str):
            data = json.loads(result)
        else:
            data = result
        return data
    except Exception as e:
        print(f"[ERROR] Failed to parse agenda '{text}': {e}")
        return None

def compute_impact(data):
    """Compute impact delta from parsed data."""
    score = sentiment_map.get(data.get("sentiment", "neutral"), 0)
    importance_factor = 1
    return score * importance_factor

def store_result(conn, data, chapter, impact_delta):
    """Insert the processed event into the SQLite table."""
    conn.execute(
        "INSERT INTO impact_log (character, chapter, event, sentiment, score, delta) VALUES (?, ?, ?, ?, ?, ?)",
        (data.get("subject", ""), chapter, data.get("event", ""), data.get("sentiment", ""), 
         sentiment_map.get(data.get("sentiment", "neutral"), 0), impact_delta),
    )
    conn.commit()

def setup_database():
    """Create database and table if not exists."""
    conn = sqlite3.connect("data_store.db")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS impact_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character TEXT,
            chapter INTEGER,
            event TEXT,
            sentiment TEXT,
            score INTEGER,
            delta REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS berry_index (
            character TEXT PRIMARY KEY,
            total_delta REAL DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    return conn

def main():
    conn = setup_database()

    # Read all JSON files in directory
    for filename in os.listdir(CHAR_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(CHAR_DIR, filename)
        with open(path) as f:
            profile = json.load(f)

        subject = profile["subject"]
        bio = profile["bio"]
        chapters = [x["chapter"] for x in profile["agendas"]]
        agendas = [x["event"] for x in profile["agendas"]]

        print(f"\n[PROCESSING] {subject}")

        # Fetch processed chapters if in refresh mode
        processed_chapters = set()
        if REFRESH_MODE:
            cur = conn.execute("SELECT chapter FROM impact_log WHERE character = ?", (subject,))
            processed_chapters = {row[0] for row in cur.fetchall()}

        for chapter, text in zip(chapters, agendas):
            if REFRESH_MODE and chapter in processed_chapters:
                continue
            data = process_agenda(text, subject, bio)
            if not data:
                continue
            impact_delta = compute_impact(data)
            store_result(conn, data, chapter, impact_delta)
            print(f"[OK] {data['subject']} | {chapter} | {data['event']} | Δ {impact_delta}")
        print(f"[DONE] {subject}")
    conn.close()

if __name__ == "__main__":
    main()