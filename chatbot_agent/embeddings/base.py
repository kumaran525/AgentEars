from abc import ABC, abstractmethod

import numpy as np


class EmbeddingModel(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def dim(self) -> int:
        pass
