import os
from openai import OpenAI


class EmbeddingsClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ["API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"],
        )
        self.model = os.environ.get("EMBEDDINGS_MODEL", "Qwen/Qwen3-Embedding-0.6B")

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [d.embedding for d in resp.data]