"""File I/O built-in functions (v0.6): read, readlines, write, append, exists."""

from __future__ import annotations

import os

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import display, ixx_type_name


def _builtin_read(path: IXXValue) -> str:
    if not isinstance(path, str):
        raise IXXRuntimeError(f"'read' expects a file path as text, not {ixx_type_name(path)}.")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise IXXRuntimeError(f"File not found: {path}")
    except PermissionError:
        raise IXXRuntimeError(f"Permission denied reading: {path}")
    except OSError as e:
        raise IXXRuntimeError(f"Could not read '{path}': {e}")


def _builtin_readlines(path: IXXValue) -> list:
    if not isinstance(path, str):
        raise IXXRuntimeError(f"'readlines' expects a file path as text, not {ixx_type_name(path)}.")
    try:
        with open(path, encoding="utf-8") as f:
            return [line.rstrip("\n\r") for line in f.readlines()]
    except FileNotFoundError:
        raise IXXRuntimeError(f"File not found: {path}")
    except PermissionError:
        raise IXXRuntimeError(f"Permission denied reading: {path}")
    except OSError as e:
        raise IXXRuntimeError(f"Could not read '{path}': {e}")


def _builtin_write(path: IXXValue, content: IXXValue) -> None:
    if not isinstance(path, str):
        raise IXXRuntimeError(f"'write' expects a file path as text, not {ixx_type_name(path)}.")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(display(content))
    except PermissionError:
        raise IXXRuntimeError(f"Permission denied writing: {path}")
    except OSError as e:
        raise IXXRuntimeError(f"Could not write '{path}': {e}")


def _builtin_append(path: IXXValue, content: IXXValue) -> None:
    if not isinstance(path, str):
        raise IXXRuntimeError(f"'append' expects a file path as text, not {ixx_type_name(path)}.")
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(display(content))
    except PermissionError:
        raise IXXRuntimeError(f"Permission denied writing: {path}")
    except OSError as e:
        raise IXXRuntimeError(f"Could not append to '{path}': {e}")


def _builtin_exists(path: IXXValue) -> bool:
    if not isinstance(path, str):
        raise IXXRuntimeError(f"'exists' expects a file path as text, not {ixx_type_name(path)}.")
    return os.path.exists(path)


FILE_BUILTINS: dict[str, object] = {
    "read":      _builtin_read,
    "readlines": _builtin_readlines,
    "write":     _builtin_write,
    "append":    _builtin_append,
    "exists":    _builtin_exists,
}
