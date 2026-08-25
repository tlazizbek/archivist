import requests

from archivist.config import LLM_API_KEY, LLM_BASE_URL


class LLMClient:
    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{LLM_BASE_URL}/embeddings",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "input": text,
                "model": "text-embedding-3-small"
            },
            timeout=30,
        )

        if response.status_code == 429:
            raise RuntimeError(
                "LLM provider rate limit reached. Try again later"
            )
        
        response.raise_for_status()

        data = response.json()

        return data["data"][0]["embedding"]

    def complete(self, prompt: str) -> str:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            },
            timeout=30,
        )

        if response.status_code == 429:
            raise RuntimeError(
                "LLM provider rate limit reached. Try again later"
            )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
    