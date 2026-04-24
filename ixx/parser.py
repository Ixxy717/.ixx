"""
IXX parser: text source → IXX AST Program.

Runs the preprocessor first (converts leading dashes to spaces),
then parses with Lark + the indentation handler.
"""

from __future__ import annotations
import os
from lark import Lark
from lark.indenter import Indenter
from .preprocessor import preprocess
from .build_ast import IXXTransformer
from .ast_nodes import Program

_GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "grammar.lark")


class IXXIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types: list[str] = []
    CLOSE_PAREN_types: list[str] = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


with open(_GRAMMAR_PATH, encoding="utf-8") as _f:
    _GRAMMAR = _f.read()

_parser = Lark(
    _GRAMMAR,
    parser="lalr",
    lexer="basic",
    postlex=IXXIndenter(),
    propagate_positions=True,
)

_transformer = IXXTransformer()


def parse(source: str) -> Program:
    """Parse IXX source text and return a Program AST node."""
    source = preprocess(source)
    if not source.endswith("\n"):
        source += "\n"
    tree = _parser.parse(source)
    return _transformer.transform(tree)
