from pathlib import Path

from archivist.models import RawDocument


def read_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_folder(path: str) -> list[RawDocument]:
    folder = Path(path)
    documents = []

    for file_path in folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md"}:
            raw_text = read_text_file(str(file_path))

            documents.append(
                RawDocument(
                    path=file_path,
                    title=file_path.stem,
                    source_type=file_path.suffix.lower().lstrip("."),
                    raw_text=raw_text,
                )
            )

    return documents