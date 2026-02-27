import uuid
from typing import List
from pypdf import PdfReader
from openai import AsyncOpenAI
from app.config.settings import settings

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "NoaVoice"
    }
)

class EmbeddingService: 

    async def process_file(self, file_path: str):

        # 1️⃣ Extract text
        text = self.extract_text(file_path)

        # 2️⃣ Chunk text
        chunks = self.chunk_text(text)

        # 3️⃣ Generate embeddings
        processed_chunks = []

        for chunk in chunks:
            embedding = await self.generate_embedding(chunk)

            processed_chunks.append({
                "id": str(uuid.uuid4()),
                "content": chunk,
                "embedding": embedding
            })

        return processed_chunks

    # -------------------------
    # TEXT EXTRACTION
    # -------------------------

    def extract_text(self, file_path: str) -> str:

        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return text

        # fallback for txt
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    # -------------------------
    # CHUNKING
    # -------------------------

    def chunk_text(self, text: str, size=800, overlap=150) -> List[str]:

        chunks = []
        start = 0

        while start < len(text):
            end = start + size
            chunks.append(text[start:end])
            start += size - overlap

        return chunks

    # -------------------------
    # REAL EMBEDDING
    # -------------------------

    async def generate_embedding(self, text: str):

        response = await client.embeddings.create(
            model="openai/text-embedding-3-small",
            input=text
        )

        return response.data[0].embedding