import json
import sqlite3

from chatbot_agent.consts import db_path


def print_calls(conn):
    print("\n=== CALLS TABLE ===")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calls")

    rows = cursor.fetchall()
    for row in rows:
        print(row)


def print_call_segments(conn, limit=10):
    print("\n=== CALL_SEGMENTS TABLE ===")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            segment_id,
            call_id,
            turn_index,
            speaker_role,
            transcript,
            dialog_acts,
            emotion,
            start_ms,
            duration_ms,
            vector_id
        FROM call_segments
        ORDER BY call_id, turn_index
        LIMIT ?
        """,
        (limit,),
    )

    rows = cursor.fetchall()
    for row in rows:
        (
            segment_id,
            call_id,
            turn_index,
            speaker_role,
            transcript,
            dialog_acts,
            emotion,
            start_ms,
            duration_ms,
            vector_id,
        ) = row
        if call_id == "0002f70f7386445b":
            print("\n--- Segment ---")
            print("segment_id:", segment_id)
            print("call_id:", call_id)
            print("turn_index:", turn_index)
            print("speaker_role:", speaker_role)
            print("transcript:", transcript)
            print("dialog_acts:", json.loads(dialog_acts) if dialog_acts else None)
            print("emotion:", json.loads(emotion) if emotion else None)
            print("start_ms:", start_ms)
            print("duration_ms:", duration_ms)
            print("vector_id:", vector_id)


def main():
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found at {db_path}")

    conn = sqlite3.connect(db_path)

    print_calls(conn)
    print_call_segments(conn, limit=20)

    conn.close()


if __name__ == "__main__":
    main()
