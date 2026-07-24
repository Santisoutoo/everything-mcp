"""ctypes bindings for the Everything (voidtools) SDK DLL.

Talks over IPC to a running Everything instance. The SDK keeps global
per-process query state, so all queries are serialized with a lock.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Sort constants (Everything.h)
SORT_MODES = {
    "relevance": 0,  # EVERYTHING_SORT_NAME_ASCENDING is 1; 0 keeps index order (best-match first for simple queries)
    "name": 1,  # EVERYTHING_SORT_NAME_ASCENDING
    "path": 3,  # EVERYTHING_SORT_PATH_ASCENDING
    "size": 6,  # EVERYTHING_SORT_SIZE_DESCENDING
    "date_modified": 14,  # EVERYTHING_SORT_DATE_MODIFIED_DESCENDING
}

# Request flags
_REQUEST_FILE_NAME = 0x00000001
_REQUEST_PATH = 0x00000002
_REQUEST_SIZE = 0x00000010
_REQUEST_DATE_MODIFIED = 0x00000040

# Error codes (Everything_GetLastError)
_ERROR_MESSAGES = {
    1: "Everything SDK: out of memory.",
    2: (
        "Everything no está corriendo. Abre Everything (se queda en el tray) "
        "y reintenta la búsqueda."
    ),
    3: "Everything SDK: failed to register window class.",
    4: "Everything SDK: failed to create listening window.",
    5: "Everything SDK: failed to create worker thread.",
    6: "Everything SDK: invalid result index.",
    7: "Everything SDK: invalid call.",
}

_MAX_PATH_BUF = 32768
_FILETIME_EPOCH_OFFSET = 116444736000000000  # FILETIME ticks at Unix epoch
_FILETIME_TICKS_PER_SEC = 10_000_000


class EverythingError(RuntimeError):
    """Raised when the Everything SDK reports an error or is unavailable."""


_lock = threading.Lock()
_dll: ctypes.WinDLL | None = None


def _dll_path() -> Path:
    env = os.environ.get("EVERYTHING_DLL")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "lib" / "Everything64.dll"


def _load_dll() -> ctypes.WinDLL:
    global _dll
    if _dll is not None:
        return _dll
    path = _dll_path()
    if not path.is_file():
        raise EverythingError(
            f"No se encontró Everything64.dll en {path}. Descarga el SDK de "
            "https://www.voidtools.com/Everything-SDK.zip y copia dll/Everything64.dll "
            "ahí, o apunta la variable de entorno EVERYTHING_DLL a la DLL."
        )
    dll = ctypes.WinDLL(str(path))
    dll.Everything_SetSearchW.argtypes = [wt.LPCWSTR]
    dll.Everything_QueryW.argtypes = [wt.BOOL]
    dll.Everything_QueryW.restype = wt.BOOL
    dll.Everything_GetResultFullPathNameW.argtypes = [wt.DWORD, wt.LPWSTR, wt.DWORD]
    dll.Everything_GetResultFullPathNameW.restype = wt.DWORD
    dll.Everything_GetResultSize.argtypes = [
        wt.DWORD,
        ctypes.POINTER(ctypes.c_longlong),
    ]
    dll.Everything_GetResultSize.restype = wt.BOOL
    dll.Everything_GetResultDateModified.argtypes = [
        wt.DWORD,
        ctypes.POINTER(ctypes.c_ulonglong),
    ]
    dll.Everything_GetResultDateModified.restype = wt.BOOL
    dll.Everything_IsFolderResult.argtypes = [wt.DWORD]
    dll.Everything_IsFolderResult.restype = wt.BOOL
    _dll = dll
    return dll


def _filetime_to_iso(filetime: int) -> str | None:
    if filetime in (0, 0xFFFFFFFFFFFFFFFF):
        return None
    unix_seconds = (filetime - _FILETIME_EPOCH_OFFSET) / _FILETIME_TICKS_PER_SEC
    try:
        return (
            datetime.fromtimestamp(unix_seconds, tz=UTC).astimezone().isoformat(timespec="seconds")
        )
    except (OverflowError, OSError, ValueError):
        return None


def search(
    query: str,
    max_results: int = 50,
    offset: int = 0,
    match_case: bool = False,
    regex: bool = False,
    sort: str = "relevance",
) -> dict[str, Any]:
    """Run a filename search against the running Everything instance.

    Returns {"total_results": int, "results": [{path, is_folder, size, modified}]}.
    """
    if sort not in SORT_MODES:
        raise EverythingError(f"sort inválido: {sort!r}. Valores: {', '.join(SORT_MODES)}")
    dll = _load_dll()
    with _lock:
        dll.Everything_Reset()
        dll.Everything_SetSearchW(query)
        dll.Everything_SetMatchCase(bool(match_case))
        dll.Everything_SetRegex(bool(regex))
        dll.Everything_SetMax(max_results)
        dll.Everything_SetOffset(offset)
        if SORT_MODES[sort]:
            dll.Everything_SetSort(SORT_MODES[sort])
        dll.Everything_SetRequestFlags(
            _REQUEST_FILE_NAME | _REQUEST_PATH | _REQUEST_SIZE | _REQUEST_DATE_MODIFIED
        )
        if not dll.Everything_QueryW(True):
            code = dll.Everything_GetLastError()
            raise EverythingError(_ERROR_MESSAGES.get(code, f"Everything SDK error {code}."))

        num = dll.Everything_GetNumResults()
        total = dll.Everything_GetTotResults()
        buf = ctypes.create_unicode_buffer(_MAX_PATH_BUF)
        size = ctypes.c_longlong()
        filetime = ctypes.c_ulonglong()
        results: list[dict[str, Any]] = []
        for i in range(num):
            dll.Everything_GetResultFullPathNameW(i, buf, _MAX_PATH_BUF)
            is_folder = bool(dll.Everything_IsFolderResult(i))
            entry: dict[str, Any] = {"path": buf.value, "is_folder": is_folder}
            if dll.Everything_GetResultSize(i, ctypes.byref(size)) and not is_folder:
                entry["size"] = size.value
            if dll.Everything_GetResultDateModified(i, ctypes.byref(filetime)):
                entry["modified"] = _filetime_to_iso(filetime.value)
            results.append(entry)
        return {"total_results": total, "results": results}
