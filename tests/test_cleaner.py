from archivist.ingestion.cleaner import (
    clean,
    normalize_whitespace,
    strip_boilerplate,
)


def test_normalize_whitespace_collapses_runs_and_tabs() -> None:
    assert normalize_whitespace("a\t\tb   c") == "a b c"


def test_normalize_whitespace_collapses_blank_lines() -> None:
    assert normalize_whitespace("a\n\n\n\nb") == "a\n\nb"


def test_normalize_whitespace_strips_edges() -> None:
    assert normalize_whitespace("  hello  ") == "hello"


def test_strip_boilerplate_removes_separator_lines() -> None:
    text = "real line\n=====\n----\nanother line"

    assert strip_boilerplate(text) == "real line\nanother line"


def test_strip_boilerplate_drops_blank_lines() -> None:
    assert strip_boilerplate("a\n\n   \nb") == "a\nb"


def test_clean_runs_both_stages() -> None:
    raw = "  Title\t\there\n\n=====\n\nBody   text  \n"

    assert clean(raw) == "Title here\nBody text"
