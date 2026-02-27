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


class LLMService:

    async def answer(self, query: str, context: list):

        context_text = "\n\n".join(context)

        prompt = f"""
Answer strictly using the provided context.

Context:
{context}

Question:
{query}
"""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer strictly from provided knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content