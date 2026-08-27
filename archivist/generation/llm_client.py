import requests

from archivist.config import LLM_API_KEY, LLM_BASE_URL


class LLMClient:
    def _post(self, path: str, payload: dict, timeout: int) -> dict:
        try:
            response = requests.post(
                f"{LLM_BASE_URL}{path}",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )
        except requests.Timeout as error:
            raise RuntimeError("LLM request timed out") from error

        if response.status_code == 429:
            raise RuntimeError(
                "LLM provider rate limit reached. Try again later"
            )

        response.raise_for_status()

        return response.json()

    def embed(self, text: str) -> list[float]:
        data = self._post(
            "/embeddings",
            {
                "input": text,
                "model": "text-embedding-3-small",
            },
            timeout=30,
        )

        return data["data"][0]["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        data = self._post(
            "/embeddings",
            {
                "input": texts,
                "model": "text-embedding-3-small",
            },
            timeout=120,
        )

        return [
            item["embedding"]
            for item in sorted(
                data["data"],
                key=lambda item: item["index"],
            )
        ]

    def complete(self, prompt: str) -> str:
        data = self._post(
            "/chat/completions",
            {
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

        return data["choices"][0]["message"]["content"]
