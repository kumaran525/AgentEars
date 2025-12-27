from pathlib import Path

import faiss
import numpy as np


class FaissStore:
    def __init__(self, dim: int, index_path: str):
        self.dim = dim
        self.index_path = Path(index_path)

        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatIP(dim)

    def add(self, vectors: np.ndarray):
        self.index.add(vectors)

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
