"""MCP server exposing Everything (voidtools) instant filename search."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from everything_mcp.sdk import EverythingError, search, status

mcp = FastMCP("everything")


@mcp.tool()
def everything_status() -> dict[str, Any]:
    """Report whether Everything is reachable and its index is ready.

    Call this to self-diagnose before searching: returns `available` (bool),
    `db_loaded` (False while Everything is still building its index),
    `version`, and `indexed_items` (total files+folders indexed). On failure
    returns `available: False` with an actionable `error` message.
    """
    return status()


@mcp.tool()
def search_files(
    query: str,
    max_results: int = 50,
    offset: int = 0,
    match_case: bool = False,
    match_whole_word: bool = False,
    match_path: bool = False,
    regex: bool = False,
    sort: str = "default",
) -> dict[str, Any]:
    """Instantly search file and folder NAMES across the entire disk using the
    Everything index (use this instead of recursive directory listings when the
    target is outside the current project).

    `query` uses Everything's native syntax — exploit it instead of filtering
    results yourself:
    - Plain words match anywhere in the name: `informe tfg` (space = AND).
    - Wildcards: `*.sfz`, `foto_202?.jpg`. Extension filter: `ext:pdf;docx`.
    - Scope to a folder tree: `path:"C:\\Users\\santi\\Documents" factura`.
      Direct children only: `parent:"C:\\Users\\santi\\Desktop"`.
    - Only folders / only files: `folder:node_modules`, `file:*.log`.
    - Dates: `dm:today`, `dm:lastweek`, `dm:2026`. Size: `size:>10mb`.
    - Operators: `|` (OR), `!` (NOT), quotes for exact phrases.

    Searches names only, NOT file contents. `total_results` in the response is
    the full match count; page with `offset` if it exceeds `max_results`.
    `match_whole_word` requires each search term to match a whole word.
    `match_path` matches the terms against the full path, not just the name.
    `sort` is one of: default (index order), name, path, size (largest first),
    date_modified (newest first).
    """
    try:
        return search(
            query,
            max_results=max_results,
            offset=offset,
            match_case=match_case,
            match_whole_word=match_whole_word,
            match_path=match_path,
            regex=regex,
            sort=sort,
        )
    except EverythingError as exc:
        return {"error": str(exc)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
