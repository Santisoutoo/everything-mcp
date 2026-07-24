"""Smoke tests for the status() diagnostic (require a running Everything)."""

import pytest

from everything_mcp.sdk import status


def _everything_available() -> bool:
    return bool(status().get("available"))


pytestmark = pytest.mark.skipif(not _everything_available(), reason="Everything is not running")


def test_status_reports_ready_index() -> None:
    out = status()
    assert out["available"] is True
    assert out["db_loaded"] is True
    assert out["version"].startswith("1.")
    assert out["indexed_items"] > 0
