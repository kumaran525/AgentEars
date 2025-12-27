# src/storage/schema.py

CALLS_TABLE = """
CREATE TABLE IF NOT EXISTS calls (
    call_id TEXT PRIMARY KEY,
    created_at INTEGER NOT NULL
);
"""

SEGMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS call_segments (
    segment_id TEXT PRIMARY KEY,
    call_id TEXT NOT NULL,

    turn_index INTEGER NOT NULL,
    speaker_role TEXT NOT NULL CHECK (speaker_role IN ('agent', 'caller')),

    transcript TEXT NOT NULL,
    human_transcript TEXT,

    dialog_acts TEXT,
    emotion TEXT,

    channel_index INTEGER,
    start_ms INTEGER,
    offset_ms INTEGER,
    start_timestamp_ms INTEGER,
    duration_ms INTEGER,

    word_offsets_ms TEXT,
    word_durations_ms TEXT,

    vector_id INTEGER,

    FOREIGN KEY (call_id) REFERENCES calls(call_id) ON DELETE CASCADE
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_segments_call ON call_segments(call_id);",
    "CREATE INDEX IF NOT EXISTS idx_segments_speaker ON call_segments(speaker_role);",
    "CREATE INDEX IF NOT EXISTS idx_segments_turn ON call_segments(call_id, turn_index);",
    "CREATE INDEX IF NOT EXISTS idx_segments_vector ON call_segments(vector_id);",
]
