import typing

from ._ansi import (
    BLACK as BLACK,
    BLUE as BLUE,
    BOLD as BOLD,
    CYAN as CYAN,
    FAINT as FAINT,
    GREEN as GREEN,
    ITALIC as ITALIC,
    MAGENTA as MAGENTA,
    RED as RED,
    RESET as RESET,
    RGB as RGB,
    UNDERLINE as UNDERLINE,
    WHITE as WHITE,
    YELLOW as YELLOW,
)
from ._arguments import (
    Arguments as Arguments,
    Flag as Flag,
    Option as Option,
    ParsedArguments as ParsedArguments,
    Positional as Positional,
    UsageError as UsageError,
    Variadic as Variadic,
)
from ._command import Command as Command, command as command
from ._completions import Dir as Dir, NoComplete as NoComplete
from ._decode import decode as decode, DecodeError as DecodeError
from ._group import group as group
from ._help import Help as Help, Style as Style


if not hasattr(typing, "GENERATING_DOCUMENTATION"):
    # For some reason this causes methods to stop appearing in our documentation... ?
    for value in list(globals().values()):
        if isinstance(value, type):
            value.__module__ = __name__
