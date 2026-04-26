"""Math built-in functions (v0.5): round, abs, min, max."""

from __future__ import annotations

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import ixx_err_type


_BOOL_IN_MINMAX_MSG = "Cannot use YES/NO in min/max. Use a number instead."
_BOOL_IN_ROUND_MSG = "Cannot use YES/NO as the number of digits. Use a number instead."


def _check_no_bools_minmax(values: tuple | list) -> None:
    """Raise a friendly error if any value in *values* is a boolean."""
    if any(isinstance(v, bool) for v in values):
        raise IXXRuntimeError(_BOOL_IN_MINMAX_MSG)


def _builtin_round(x: IXXValue, digits: IXXValue = 0) -> int | float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise IXXRuntimeError(f"'round' works on numbers, not {ixx_err_type(x)}.")
    if isinstance(digits, bool):
        raise IXXRuntimeError(_BOOL_IN_ROUND_MSG)
    try:
        d = int(digits)
    except (TypeError, ValueError):
        raise IXXRuntimeError("'round' second argument (digits) must be a whole number.")
    result = round(x, d)
    return int(result) if d <= 0 else result


def _builtin_abs(x: IXXValue) -> int | float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise IXXRuntimeError(f"'abs' works on numbers, not {ixx_err_type(x)}.")
    return abs(x)


def _builtin_min(*args: IXXValue) -> IXXValue:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise IXXRuntimeError("'min' cannot find the minimum of an empty list.")
        _check_no_bools_minmax(items)
        return min(items)  # type: ignore[type-var]
    if len(args) < 2:
        raise IXXRuntimeError(
            "'min' needs at least two values, or a list.  Example: min(3, 7)"
        )
    _check_no_bools_minmax(args)
    return min(args)  # type: ignore[type-var]


def _builtin_max(*args: IXXValue) -> IXXValue:
    if len(args) == 1 and isinstance(args[0], list):
        items = args[0]
        if not items:
            raise IXXRuntimeError("'max' cannot find the maximum of an empty list.")
        _check_no_bools_minmax(items)
        return max(items)  # type: ignore[type-var]
    if len(args) < 2:
        raise IXXRuntimeError(
            "'max' needs at least two values, or a list.  Example: max(3, 7)"
        )
    _check_no_bools_minmax(args)
    return max(args)  # type: ignore[type-var]


MATH_BUILTINS: dict[str, object] = {
    "round": _builtin_round,
    "abs":   _builtin_abs,
    "min":   _builtin_min,
    "max":   _builtin_max,
}
