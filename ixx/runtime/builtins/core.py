"""Core built-in functions (v0.4): count, text, number, type, ask."""

from __future__ import annotations
import math

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import display, ixx_type_name, ixx_err_type


def _builtin_count(x: IXXValue) -> int:
    if isinstance(x, (str, list)):
        return len(x)
    raise IXXRuntimeError(
        f"'count' works on lists and text, not {ixx_err_type(x)}."
    )


def _builtin_text(x: IXXValue) -> str:
    return display(x)


def _builtin_number(x: IXXValue) -> int | float:
    if isinstance(x, bool):
        raise IXXRuntimeError(
            f"Cannot convert '{display(x)}' to a number."
        )
    if isinstance(x, list):
        raise IXXRuntimeError(
            "'number' cannot convert a list to a number. Pass a text value instead."
        )
    if isinstance(x, (int, float)):
        if isinstance(x, float) and not math.isfinite(x):
            raise IXXRuntimeError(
                "'number' only works with finite numbers. "
                "Values like inf and nan are not allowed."
            )
        return x
    s = str(x)
    try:
        result_int = int(s)
        return result_int
    except ValueError:
        pass
    try:
        result_float = float(s)
        if not math.isfinite(result_float):
            raise IXXRuntimeError(
                "'number' only works with finite numbers. "
                "Values like inf and nan are not allowed."
            )
        return result_float
    except ValueError:
        pass
    raise IXXRuntimeError(
        f"Cannot convert '{display(x)}' to a number."
    )


def _builtin_type(x: IXXValue) -> str:
    return ixx_type_name(x)


def _builtin_ask(prompt: IXXValue = "") -> str:
    try:
        return input(str(prompt))
    except EOFError:
        raise IXXRuntimeError("No input available (stdin is closed).")
    except KeyboardInterrupt:
        raise IXXRuntimeError("Input was cancelled.")


CORE_BUILTINS: dict[str, object] = {
    "count":  _builtin_count,
    "text":   _builtin_text,
    "number": _builtin_number,
    "type":   _builtin_type,
    "ask":    _builtin_ask,
}
