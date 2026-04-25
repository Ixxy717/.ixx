"""Text built-in functions (v0.5): upper, lower, trim, replace, split, join."""

from __future__ import annotations

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import ixx_type_name


def _builtin_upper(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'upper' works on text, not {ixx_type_name(x)}.")
    return x.upper()


def _builtin_lower(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'lower' works on text, not {ixx_type_name(x)}.")
    return x.lower()


def _builtin_trim(x: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'trim' works on text, not {ixx_type_name(x)}.")
    return x.strip()


def _builtin_replace(x: IXXValue, find: IXXValue, replacement: IXXValue) -> str:
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'replace' works on text, not {ixx_type_name(x)}.")
    if not isinstance(find, str):
        raise IXXRuntimeError(
            f"'replace' second argument (find) must be text, not {ixx_type_name(find)}."
        )
    return x.replace(str(find), str(replacement))


def _builtin_split(x: IXXValue, sep: IXXValue = None) -> list:  # type: ignore[assignment]
    if not isinstance(x, str):
        raise IXXRuntimeError(f"'split' works on text, not {ixx_type_name(x)}.")
    if sep is None:
        return x.split()
    if not isinstance(sep, str):
        raise IXXRuntimeError(
            f"'split' separator must be text, not {ixx_type_name(sep)}."
        )
    return x.split(sep)


def _builtin_join(items: IXXValue, sep: IXXValue = ", ") -> str:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'join' works on lists, not {ixx_type_name(items)}.")
    if not isinstance(sep, str):
        raise IXXRuntimeError(
            f"'join' separator must be text, not {ixx_type_name(sep)}."
        )
    return sep.join(str(item) for item in items)


TEXT_BUILTINS: dict[str, object] = {
    "upper":   _builtin_upper,
    "lower":   _builtin_lower,
    "trim":    _builtin_trim,
    "replace": _builtin_replace,
    "split":   _builtin_split,
    "join":    _builtin_join,
}
