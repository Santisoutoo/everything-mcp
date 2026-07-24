# everything-mcp

[![CI](https://github.com/Santisoutoo/everything-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Santisoutoo/everything-mcp/actions/workflows/ci.yml)

Servidor MCP que expone la búsqueda instantánea de [Everything](https://www.voidtools.com/)
(voidtools) a agentes LLM (Claude Code, etc.). Busca **nombres** de archivos y carpetas en todo
el disco en milisegundos usando el índice NTFS de Everything — complementa a Glob/Grep, que solo
ven el proyecto actual.

## Requisitos

- Windows con **Everything corriendo** (basta que esté en el tray).
- `Everything64.dll` del [Everything SDK](https://www.voidtools.com/Everything-SDK.zip): descarga el
  zip, copia `dll/Everything64.dll` a `lib/` (no versionada en el repo) o apunta la env var
  `EVERYTHING_DLL` a su ruta.
- Python ≥3.11 + [uv](https://docs.astral.sh/uv/).

## Tool expuesta

`search_files(query, max_results=50, offset=0, match_case=False, match_whole_word=False, regex=False, sort="default")`

`query` acepta la sintaxis nativa de Everything (`ext:pdf`, `path:"C:\..."`, `dm:today`,
`size:>10mb`, `folder:`, `file:`, `|`, `!`…). `sort` es uno de `default` (orden del índice),
`name`, `path`, `size`, `date_modified`. Devuelve `{total_results, results:[{path, is_folder,
size, modified}]}`. Solo busca nombres, no contenido.

## Registro en Claude Code

```
claude mcp add --scope user everything -- uv run --directory C:\Users\santi\Documents\personal_projects\everything-mcp everything-mcp
```

## Desarrollo

```
uv sync
uv run pytest          # smoke tests (requieren Everything corriendo)
uv run everything-mcp  # arranca el servidor por stdio
```
