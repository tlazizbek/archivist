from sklearn.feature_extraction.text import TfidfVectorizer


class KeywordRetriever:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer()

    def fit(self, texts: list[str]) -> None:
        pass

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        pass