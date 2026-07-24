"""Smoke tests for the Everything SDK bindings.

Require a running Everything instance (skipped otherwise).
"""

import pytest

from everything_mcp.sdk import EverythingError, search


def _everything_available() -> bool:
    try:
        search("test", max_results=1)
        return True
    except EverythingError:
        return False


pytestmark = pytest.mark.skipif(not _everything_available(), reason="Everything is not running")


def test_search_returns_results() -> None:
    # file: filter needed — folders named *.exe exist in the wild
    out = search("file:*.exe", max_results=5)
    assert out["total_results"] > 0
    assert len(out["results"]) == 5
    for r in out["results"]:
        assert r["path"].lower().endswith(".exe")
        assert r["is_folder"] is False
        assert isinstance(r["size"], int)


def test_offset_pagination() -> None:
    first = search("*.dll", max_results=3, sort="name")
    second = search("*.dll", max_results=3, offset=3, sort="name")
    assert first["results"] != second["results"]
    assert first["total_results"] == second["total_results"]


def test_folder_results_have_no_size() -> None:
    out = search("folder:Windows", max_results=5)
    assert all(r["is_folder"] for r in out["results"])
    assert all("size" not in r for r in out["results"])


def test_match_whole_word_narrows_results() -> None:
    loose = search("dll", max_results=1)
    whole = search("dll", match_whole_word=True, max_results=1)
    # whole-word matching can only match a subset of substring matching
    assert whole["total_results"] <= loose["total_results"]
