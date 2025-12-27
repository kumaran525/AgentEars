import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

from chatbot_agent.embeddings.base import EmbeddingModel


class BGEEmbedding(EmbeddingModel):
    def __init__(
        self, model_name: str, device: str = "cuda", normalize: bool = True, dim: int = 768
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(device)
        self.device = device
        self.normalize = normalize
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> np.ndarray:
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt").to(
            self.device
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0]  # CLS token

        embeddings = embeddings.cpu().numpy()

        if self.normalize:
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        return embeddings
