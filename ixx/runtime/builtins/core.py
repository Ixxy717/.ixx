"""Core built-in functions (v0.4): count, text, number, type, ask."""

from __future__ import annotations

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import display, ixx_type_name


def _builtin_count(x: IXXValue) -> int:
    if isinstance(x, (str, list)):
        return len(x)
    raise IXXRuntimeError(
        f"'count' works on lists and text, not {ixx_type_name(x)}."
    )


def _builtin_text(x: IXXValue) -> str:
    return display(x)


def _builtin_number(x: IXXValue) -> int | float:
    if isinstance(x, bool):
        raise IXXRuntimeError(
            f"Cannot convert '{display(x)}' to a number."
        )
    if isinstance(x, (int, float)):
        return x
    s = str(x)
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    raise IXXRuntimeError(
        f"Cannot convert '{x}' to a number."
    )


def _builtin_type(x: IXXValue) -> str:
    return ixx_type_name(x)


def _builtin_ask(prompt: IXXValue = "") -> str:
    return input(str(prompt))


CORE_BUILTINS: dict[str, object] = {
    "count":  _builtin_count,
    "text":   _builtin_text,
    "number": _builtin_number,
    "type":   _builtin_type,
    "ask":    _builtin_ask,
}
