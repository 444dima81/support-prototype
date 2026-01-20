import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from app.llm.embeddings import EmbeddingsClient


class Retriever:
    def __init__(self):
        load_dotenv(".env")
        self.qdrant = QdrantClient(url=os.environ["QDRANT_URL"])
        self.collection = os.environ["QDRANT_COLLECTION"]
        self.emb = EmbeddingsClient()

    def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.25) -> list[dict]:
        vec = self.emb.embed([query])[0]

        res = self.qdrant.query_points(
            collection_name=self.collection,
            query=vec,
            limit=top_k,
            with_payload=True,
        )
        points = res.points if hasattr(res, "points") else res

        chunks = []
        for p in points:
            score = float(p.score)
            if score < min_score:
                continue
            payload = p.payload or {}
            chunks.append({
                "chunk_id": payload.get("chunk_id"),
                "score": score,
                "text": payload.get("text", ""),
                "metadata": payload.get("metadata", {}),
            })

        return chunks