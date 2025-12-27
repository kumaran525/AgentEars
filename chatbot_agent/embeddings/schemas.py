from typing import Literal

from pydantic import BaseModel


class EmbeddingConfig(BaseModel):
    provider: Literal["bge", "e5", "nvidia", "openai"]
    model_name: str
    device: Literal["cpu", "cuda"] = "cpu"
    normalize: bool = True


class FaissConfig(BaseModel):
    index_type: Literal["flat_ip", "flat_l2", "ivf", "hnsw"]
    dim: int
    index_path: str
