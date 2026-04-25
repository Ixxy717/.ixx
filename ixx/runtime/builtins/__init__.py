"""IXX built-in function registry — combines all builtin modules."""

from __future__ import annotations

from .core  import CORE_BUILTINS
from .text  import TEXT_BUILTINS
from .math  import MATH_BUILTINS
from .lists import LIST_BUILTINS
from .files import FILE_BUILTINS
from .color import COLOR_BUILTINS
from .shell import SHELL_BUILTINS

BUILT_INS: dict[str, object] = {
    **CORE_BUILTINS,
    **TEXT_BUILTINS,
    **MATH_BUILTINS,
    **LIST_BUILTINS,
    **FILE_BUILTINS,
    **COLOR_BUILTINS,
    **SHELL_BUILTINS,
}
