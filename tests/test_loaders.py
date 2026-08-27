from pathlib import Path

from archivist.ingestion.loaders import load_folder, read_text_file


def test_read_text_file_returns_contents(tmp_path: Path) -> None:
    file_path = tmp_path / "note.txt"
    file_path.write_text("hello world", encoding="utf-8")

    assert read_text_file(str(file_path)) == "hello world"


def test_load_folder_picks_up_txt_and_md(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    (tmp_path / "b.md").write_text("beta", encoding="utf-8")
    (tmp_path / "ignore.pdf").write_text("nope", encoding="utf-8")

    documents = load_folder(str(tmp_path))

    titles = sorted(doc.title for doc in documents)
    assert titles == ["a", "b"]


def test_load_folder_recurses_into_subdirectories(tmp_path: Path) -> None:
    nested = tmp_path / "sub" / "deeper"
    nested.mkdir(parents=True)
    (nested / "deep.txt").write_text("content", encoding="utf-8")

    documents = load_folder(str(tmp_path))

    assert len(documents) == 1
    assert documents[0].title == "deep"


def test_load_folder_sets_metadata(tmp_path: Path) -> None:
    (tmp_path / "doc.md").write_text("body text", encoding="utf-8")

    document = load_folder(str(tmp_path))[0]

    assert document.title == "doc"
    assert document.source_type == "md"
    assert document.raw_text == "body text"


def test_load_folder_empty_returns_no_documents(tmp_path: Path) -> None:
    assert load_folder(str(tmp_path)) == []
