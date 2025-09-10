import json
import numpy as np


class VectorStore:
    def __init__(self):
        self.chunks = []
        self.vectors = []

    def add_chunk(self, chunk, vector):
        self.chunks.append(chunk)
        self.vectors.append(vector)

    def search_similar(self, query_vector, top_k=5, similarity_func=None):
        if not self.vectors:
            return []

        # 默認使用 cosine similarity
        if similarity_func is None:
            similarity_func = self._cosine_similarity

        similarities = []
        for i, vector in enumerate(self.vectors):
            similarity = similarity_func(query_vector, vector)
            similarities.append((self.chunks[i], similarity))

        # 按相似度排序，返回 top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def save_to_json(self, filename="chunk_vectors.json"):
        data = {
            "chunks": self.chunks,
            "vectors": self.vectors
        }
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_json(cls, filename="chunk_vectors.json"):
        store = cls()
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                store.chunks = data["chunks"]
                store.vectors = data["vectors"]
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty store.")
        return store

    def __len__(self):
        return len(self.chunks)
