from pathlib import Path

import pytest

from archivist import cli, config


@pytest.fixture
def configured(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(config, "LLM_API_KEY", "real-key")
    monkeypatch.setattr(config, "LLM_BASE_URL", "https://api.example/v1")
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")


def test_start_reports_missing_config(monkeypatch, capsys) -> None:
    monkeypatch.setattr(config, "LLM_API_KEY", "")
    monkeypatch.setattr(config, "LLM_BASE_URL", "https://api.example/v1")

    cli.start(docs=None, port=8000)

    out = capsys.readouterr().out
    assert "not configured" in out
    assert "LLM_API_KEY" in out


def test_start_reports_no_documents(configured, capsys) -> None:
    # Configured but empty database, and no docs folder given.
    cli.start(docs=None, port=8000)

    out = capsys.readouterr().out
    assert "no documents" in out.lower()


def test_start_serves_when_documents_exist(
    configured, monkeypatch, capsys, tmp_path: Path
) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "note.txt").write_text("hello world", encoding="utf-8")

    monkeypatch.setattr(cli, "embed_missing_chunks", lambda on_progress: 0)

    served = {}

    def fake_run(target, host, port):
        served["target"] = target
        served["port"] = port

    monkeypatch.setattr("uvicorn.run", fake_run)

    cli.start(docs=str(docs), port=9001)

    out = capsys.readouterr().out
    assert "http://127.0.0.1:9001/docs" in out
    assert served == {"target": "archivist.api.app:app", "port": 9001}
