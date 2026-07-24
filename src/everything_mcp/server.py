"""MCP server exposing Everything (voidtools) instant filename search."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from everything_mcp.sdk import EverythingError, search

mcp = FastMCP("everything")


@mcp.tool()
def search_files(
    query: str,
    max_results: int = 50,
    offset: int = 0,
    match_case: bool = False,
    regex: bool = False,
    sort: str = "relevance",
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
    `sort` is one of: relevance, name, path, size (largest first),
    date_modified (newest first).
    """
    try:
        return search(
            query,
            max_results=max_results,
            offset=offset,
            match_case=match_case,
            regex=regex,
            sort=sort,
        )
    except EverythingError as exc:
        return {"error": str(exc)}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
