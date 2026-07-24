"""Input-validation tests that run without a live Everything instance.

Validation happens before the SDK dll is touched, so these exercise real code
paths on any runner (including CI, which has neither Everything nor the dll).
"""

import pytest

from everything_mcp.sdk import EverythingError, search


def test_zero_max_results_raises() -> None:
    with pytest.raises(EverythingError, match="max_results"):
        search("x", max_results=0)


def test_negative_offset_raises() -> None:
    with pytest.raises(EverythingError, match="offset"):
        search("x", offset=-1)


def test_invalid_sort_raises() -> None:
    with pytest.raises(EverythingError, match="sort"):
        search("x", sort="bogus")
