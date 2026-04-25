"""Value display and predicate helpers for the IXX runtime."""

from __future__ import annotations

from ..ast_nodes import IXXValue


def ixx_type_name(value: IXXValue) -> str:
    """Return the IXX type name for a value (never exposes Python names)."""
    if value is None:                     return "nothing"
    if isinstance(value, bool):           return "bool"
    if isinstance(value, (int, float)):   return "number"
    if isinstance(value, str):            return "text"
    if isinstance(value, list):           return "list"
    return "unknown"


def display(value: IXXValue) -> str:
    if isinstance(value, bool): return "YES" if value else "NO"
    if isinstance(value, list): return ", ".join(display(v) for v in value)
    if value is None:           return "nothing"
    return str(value)


def truthy(value: IXXValue) -> bool:
    if isinstance(value, bool):  return value
    if isinstance(value, int):   return value != 0
    if isinstance(value, float): return value != 0.0
    if isinstance(value, str):   return value != ""
    if isinstance(value, list):  return len(value) > 0
    return False
