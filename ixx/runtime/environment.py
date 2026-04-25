"""Variable scope and environment classes for the IXX runtime."""

from __future__ import annotations

from ..ast_nodes import IXXValue
from .errors import IXXRuntimeError


class Environment:
    """A variable scope.  Looks up parent scopes when a name isn't found here."""

    def __init__(self, parent: "Environment | None" = None):
        self._vars: dict[str, IXXValue] = {}
        self._parent = parent

    def get(self, name: str) -> IXXValue:
        if name in self._vars:
            return self._vars[name]
        if self._parent is not None:
            return self._parent.get(name)
        raise IXXRuntimeError(
            f"I don't know what '{name}' is. Did you set it yet?\n"
            f"  Tip: {name} = \"your value\""
        )

    def set(self, name: str, value: IXXValue) -> None:
        # Write to the nearest scope that already owns this name,
        # otherwise create it in the current scope.
        if name in self._vars or self._parent is None:
            self._vars[name] = value
        elif self._parent._has(name):
            self._parent.set(name, value)
        else:
            self._vars[name] = value

    def _has(self, name: str) -> bool:
        return (
            name in self._vars
            or (self._parent is not None and self._parent._has(name))
        )

    def child(self) -> "Environment":
        return Environment(parent=self)


class FunctionEnvironment(Environment):
    """Local scope for a function call.

    Reads propagate up to the global scope (so globals are readable).
    Writes are always local — never propagate back to the global scope.
    This gives clean function isolation without requiring explicit 'global'.
    """

    def set(self, name: str, value: IXXValue) -> None:
        # Always write locally — never update the parent (global) scope.
        self._vars[name] = value
