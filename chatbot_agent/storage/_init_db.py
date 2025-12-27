from chatbot_agent.storage.db import get_connection
from chatbot_agent.storage.schemas import CALLS_TABLE, INDEXES, SEGMENTS_TABLE


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(CALLS_TABLE)
    cursor.execute(SEGMENTS_TABLE)

    for stmt in INDEXES:
        cursor.execute(stmt)

    conn.commit()
    conn.close()

    print("SQLite database initialized successfully")


if __name__ == "__main__":
    init_db()
