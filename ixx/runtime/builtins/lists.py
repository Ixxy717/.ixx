"""List built-in functions (v0.5): first, last, sort, reverse."""

from __future__ import annotations

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import ixx_err_type


def _builtin_first(items: IXXValue) -> IXXValue:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'first' works on lists, not {ixx_err_type(items)}.")
    if not items:
        return None
    return items[0]


def _builtin_last(items: IXXValue) -> IXXValue:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'last' works on lists, not {ixx_err_type(items)}.")
    if not items:
        return None
    return items[-1]


def _builtin_sort(items: IXXValue) -> list:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'sort' works on lists, not {ixx_err_type(items)}.")
    try:
        return sorted(items)  # type: ignore[type-var]
    except TypeError:
        raise IXXRuntimeError(
            "'sort' cannot sort a list that mixes text and numbers."
        )


def _builtin_reverse(items: IXXValue) -> list:
    if not isinstance(items, list):
        raise IXXRuntimeError(f"'reverse' works on lists, not {ixx_err_type(items)}.")
    return list(reversed(items))


LIST_BUILTINS: dict[str, object] = {
    "first":   _builtin_first,
    "last":    _builtin_last,
    "sort":    _builtin_sort,
    "reverse": _builtin_reverse,
}
