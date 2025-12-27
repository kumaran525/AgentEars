import json
import logging
import re
import sqlite3
from pathlib import Path

import yaml

from chatbot_agent.consts import PII_PATTERNS, config_path, data_path, db_path, transcript_path
from chatbot_agent.embeddings.bge import BGEEmbedding
from chatbot_agent.schemas import AppConfig, CallSegment
from chatbot_agent.vectorstore.faiss_store import FaissStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(path: str | Path) -> AppConfig:
    with open(path) as f:
        raw = yaml.safe_load(f)

    return AppConfig(**raw)


class IngestionPipeline:
    def __init__(self, data_path: Path, transcript_path: Path, db_path: Path, config: AppConfig):
        self.data_path = data_path
        self.transcript_path = transcript_path
        self.db_path = db_path
        self.config = config

    def ingest_metadata(self, json_file: Path):
        call_id = json_file.stem

        # Load JSON
        with open(json_file) as f:
            segments_data = json.load(f)

        # Determine call start_timestamp_ms (earliest segment)
        start_timestamp_ms = min(seg.get("start_timestamp_ms", 0) for seg in segments_data)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert call
        cursor.execute(
            "INSERT OR IGNORE INTO calls (call_id, created_at) VALUES (?, ?)",
            (call_id, start_timestamp_ms),
        )

        # Insert segments
        for seg_data in segments_data:
            try:
                segment = CallSegment(**seg_data)
            except Exception as e:
                print(f"Validation failed for segment {seg_data.get('index')}: {e}")
                continue

            segment_id = f"{call_id}_{segment.index}"

            cursor.execute(
                """
            INSERT OR REPLACE INTO call_segments (
                segment_id, call_id, turn_index, speaker_role, transcript, human_transcript,
                dialog_acts, emotion, channel_index, start_ms, offset_ms,
                start_timestamp_ms, duration_ms, word_offsets_ms, word_durations_ms,
                vector_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    segment_id,
                    call_id,
                    segment.index,
                    segment.speaker_role,
                    segment.transcript,
                    segment.human_transcript,
                    json.dumps(segment.dialog_acts),
                    json.dumps(segment.emotion.dict()),
                    segment.channel_index,
                    segment.start_ms,
                    segment.offset_ms,
                    segment.start_timestamp_ms,
                    segment.duration_ms,
                    json.dumps(segment.word_offsets_ms),
                    json.dumps(segment.word_durations_ms),
                    None,  # vector_id placeholder
                ),
            )

        conn.commit()
        conn.close()

    @staticmethod
    def build_windows(segments, window_size=0, overlap=0):
        step = window_size - overlap
        windows = []

        for i in range(0, len(segments) - window_size + 1, step):
            window_segments = segments[i : i + window_size]
            windows.append(window_segments)

        return windows

    @staticmethod
    def build_window_text(segments, window_size=2, overlap=1, call_id=None):
        windows = []
        n = len(segments)
        # logger.info(f"Total segments to window {segments[1]}")
        step = window_size - overlap
        for start in range(0, n, step):
            end = min(start + window_size, n)
            window_segments = segments[start:end]
            if window_segments:
                text = " ".join(seg["human_transcript"] for seg in window_segments)
                # Redact PII
                for pattern in PII_PATTERNS:
                    text = re.sub(pattern, "[REDACTED]", text)
                windows.append(
                    {
                        "start_index": window_segments[0]["index"],
                        "end_index": window_segments[-1]["index"],
                        "text": text,
                        "call_id": call_id,
                    }
                )

            if end == n:
                break

        return windows

    @staticmethod
    def remove_noise_segments(segments: list[dict]) -> list[dict]:
        return [seg for seg in segments if seg.get("human_transcript") != "[noise]"]

    def ingest_transcripts(self, json_file: Path):
        call_id = json_file.stem

        embedding_cfg = self.config.embeddings
        faiss_cfg = self.config.faiss

        if embedding_cfg.provider == "bge":
            model = BGEEmbedding(
                model_name=embedding_cfg.model_name,
                device=embedding_cfg.device,
                normalize=embedding_cfg.normalize,
                dim=faiss_cfg.dim,
            )
        else:
            raise NotImplementedError(f"Provider {embedding_cfg.provider} not supported yet")

        faiss_store = FaissStore(dim=faiss_cfg.dim, index_path=faiss_cfg.index_path)

        with open(json_file) as f:
            segments_data = json.load(f)

        segments = IngestionPipeline.remove_noise_segments(segments_data)

        windows = IngestionPipeline.build_window_text(
            sorted(segments, key=lambda x: x["index"]), window_size=2, overlap=1, call_id=call_id
        )

        # logger.info(windows)

        logger.info(f"Built {len(windows)} windows from {len(segments)} segments")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for window in windows:  # noqa: F402
            vector_id = (
                window["call_id"]
                + "_"
                + str(window["start_index"])
                + "_"
                + str(window["end_index"])
            )
            cursor.execute(
                """
                UPDATE call_segments
                SET vector_id = ?
                WHERE call_id = ? AND turn_index BETWEEN ? AND ?
                """,
                (vector_id, call_id, window["start_index"], window["end_index"]),
            )

            rows = cursor.rowcount
            if rows == 0:
                logger.info(f"[WARN] No rows updated for window {window}")
                raise

            embeddings = model.embed(window["text"])
            faiss_store.add(embeddings)
            faiss_store.save()

            logger.info(f"Inserted {len(embeddings)} vectors into FAISS")

        conn.commit()
        conn.close()

        logger.info(f"Updated vector_ids for call_id {call_id}")


if __name__ == "__main__":
    logger.info("Starting ingestion pipeline...")

    config = load_config(config_path / "embeddings.yaml")

    pipeline = IngestionPipeline(data_path, transcript_path, db_path, config=config)

    # for json_file in transcript_path.glob("*.json"):
    #     logger.info(f"Ingesting metadata from {json_file}")
    #     pipeline.ingest_metadata(json_file)
    #     logger.info(f"Finished ingesting metadata from {json_file}")

    for json_file in transcript_path.glob("*.json"):
        logger.info(f"Ingesting transcripts from {json_file}")
        pipeline.ingest_transcripts(json_file)
        logger.info(f"Finished ingesting transcripts from {json_file}")
