from pydantic import BaseModel, Field

from chatbot_agent.embeddings.schemas import EmbeddingConfig, FaissConfig


class Emotion(BaseModel):
    neutral: float
    negative: float
    positive: float


class CallSegment(BaseModel):
    """
    Baseconfig for transcript for validation

    """

    channel_index: int
    dialog_acts: list[str] = Field(default_factory=list)
    duration_ms: int
    emotion: Emotion
    human_transcript: str
    index: int = Field(..., description="Turn index within the call")
    offset_ms: int
    speaker_role: str = Field(..., pattern="^(agent|caller)$")
    start_ms: int
    start_timestamp_ms: int
    transcript: str
    word_durations_ms: list[int] = Field(default_factory=list)
    word_offsets_ms: list[int] = Field(default_factory=list)


class AppConfig(BaseModel):
    embeddings: EmbeddingConfig
    faiss: FaissConfig
