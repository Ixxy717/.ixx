"""Shell bridge built-in: do(command) — run an IXX shell command, return its output."""

from __future__ import annotations

from ...ast_nodes import IXXValue
from ..errors import IXXRuntimeError
from ..values import ixx_type_name


def _builtin_do(command: IXXValue) -> str:
    if not isinstance(command, str):
        raise IXXRuntimeError(
            f"'do' expects a shell command as text, not {ixx_type_name(command)}."
        )
    from ...shell.repl import run_command_capture
    return run_command_capture(command)


SHELL_BUILTINS: dict[str, object] = {
    "do": _builtin_do,
}
