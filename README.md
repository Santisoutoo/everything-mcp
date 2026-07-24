# everything-mcp

[![CI](https://github.com/Santisoutoo/everything-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Santisoutoo/everything-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

MCP server that exposes [Everything](https://www.voidtools.com/) (voidtools) instant file search to
LLM agents such as Claude Code. It searches file and folder **names** across the entire disk in
milliseconds using Everything's index — a complement to Glob/Grep, which only see the current project.

## Features

- **Whole-disk filename search in milliseconds** via Everything's live index.
- **Native Everything query syntax** (`ext:`, `path:`, `dm:today`, `size:>10mb`, `folder:`, `file:`,
  `|`, `!`) passed straight through — no need for extra tools.
- **Pagination** with `offset` and a `total_results` count, so an agent knows when to page.
- **`everything_status` diagnostic tool** to check the index is ready before searching.
- **Windows via the Everything SDK dll** over local IPC — no open ports, no per-search subprocess.

## Requirements

- Windows with **Everything running** (living in the tray is enough).
- `Everything64.dll` from the [Everything SDK](https://www.voidtools.com/Everything-SDK.zip).
- Python ≥3.11 and [uv](https://docs.astral.sh/uv/).

## Setup

1. **Clone the repo**

   ```
   git clone https://github.com/Santisoutoo/everything-mcp.git
   cd everything-mcp
   ```

2. **Provide the DLL.** Download the [Everything SDK](https://www.voidtools.com/Everything-SDK.zip)
   and copy `dll/Everything64.dll` into `lib/` (not versioned in the repo), or point the
   `EVERYTHING_DLL` environment variable at the dll wherever it lives.

3. **Register it in Claude Code** (user scope, available in every session):

   ```
   claude mcp add --scope user everything -- uv run --directory C:\path\to\everything-mcp everything-mcp
   ```

   Replace `C:\path\to\everything-mcp` with the absolute path where you cloned the repo.

## Tools

### `search_files`

```
search_files(query, max_results=50, offset=0, match_case=False,
             match_whole_word=False, match_path=False, regex=False, sort="default")
```

| Parameter | Meaning |
|---|---|
| `query` | Everything query. Space = AND; wildcards `*` `?`; filters like `ext:pdf;docx`, `path:"C:\Users"`, `parent:"D:\media"`, `folder:`, `file:`, `dm:today`, `size:>10mb`; operators `|` (OR), `!` (NOT), `"..."` for exact phrases. |
| `max_results` | Cap on returned rows (1–1000). |
| `offset` | Skip N results (pagination). |
| `match_case` | Case-sensitive matching. |
| `match_whole_word` | Require each term to match a whole word. |
| `match_path` | Match terms against the full path, not just the name. |
| `regex` | Treat `query` as a regular expression. |
| `sort` | One of `default` (index order), `name`, `path`, `size` (largest first), `date_modified` (newest first). |

Returns `{total_results, results: [{path, is_folder, size, modified}]}`. `total_results` is the full
match count; page with `offset` when it exceeds `max_results`. Searches names only, not file contents.

### `everything_status`

Returns `{available, db_loaded, version, indexed_items}`, or `{available: false, error}` when
Everything is not running. Useful for an agent to confirm the index is ready before searching.

## Development

```
uv sync
uv run pytest          # smoke tests (self-skip when Everything is not running)
uv run ruff check .    # lint
uv run mypy src        # type-check
uv run everything-mcp  # start the server over stdio
```

## License

Released under the [MIT License](LICENSE).
