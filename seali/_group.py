import sys
from collections.abc import Sequence
from typing import Literal, overload

from ._command import Command, command
from ._help import Help


def _with_name(name: str):
    def _with_name_impl(fn):
        fn.__name__ = name
        return fn

    return _with_name_impl


@overload
def group(
    *,
    default: Command,
    subcommands: Sequence[Command],
): ...


@overload
def group(
    *,
    name: str,
    help: None | Help = None,
    version: None | str = None,
    subcommands: Sequence[Command],
): ...


def group(
    *,
    default: None | Command = None,
    name: None | str = None,
    help: None | Help = None,
    version: None | str = None,
    subcommands: Sequence[Command],
) -> Command:
    """Group multiple commands, to provide subcommands.

    **Arguments:**

    - `default`: a command to run if no subcommand is provided. Mutually exclusive with
        `name`, `help` and `version`.
    - `name`: name. Either this or `default` must be provided.
    - `help`: help message, as [`seali.command`][]. Mutually exclusive with `default`.
    - `version`: version, as [`seali.command`][]. Mutually exclusive with `default`.
    - `subcommands`: a list/tuple of subcommands.

    **Returns:**

    As `seali.command`.

    **Command line inputs:**

    The first positional input is inspected, and its value used to redispatch to the
    appropriate element of `subcommands`. All flags, options, and remaining positional
    inputs are passed on to the subcommand.

    If no positional inputs are present...
    <br>
    ...and `default` is available, then it will be called with any options and flags.
    <br>
    ...and no `default` is available, then an error will be raised.

    !!! Example

        ```python
        import seali

        @seali.command
        def bar(...): ...

        @seali.command
        def baz(...): ...

        foo = seali.group(name="foo", subcommands=[bar, baz])

        if __name__ == "__main__":
           foo()
        ```
    """
    if default is not None and not isinstance(default, Command):
        raise TypeError(
            "`default` must be either `None` or a command (a callable decorated with "
            "`seali.command`). It should not be a raw function."
        )
    if default is None:
        if name is None:
            raise ValueError("Either `default` or `name` must be provided.")
    else:
        if name is not None:
            raise ValueError(
                "Got `seali.group(name=..., default=...)`. To provide a name "
                "*and* a default command, then set the name for the default command "
                "`seali.group(default=seali.command(<function with name 'name'>))`."
            )
        name = default.fn.__name__
        if help is not None:
            raise ValueError(
                "Got `seali.group(help=..., default=...)`. To provide documentation "
                "*and* a default command, then attach the documentation to the default "
                "command directly: `seali.group(default=seali.command(help=...))`."
            )
        help = default.help
        if version is not None:
            raise ValueError(
                "Got `seali.group(version=..., default=...)`. To provide a version "
                "*and* a default command, then attach the version to the default "
                "command directly: "
                "`seali.group(default=seali.command(version=...))`."
            )
        version = default.version
    for value in subcommands:
        if not isinstance(value, Command):
            raise TypeError(
                "subcommands must be commands (a callable decorated with "
                "`seali.command`). They should not be raw functions."
            )

    subcommand_lookup = {s.fn.__name__: s for s in subcommands}
    del subcommands
    Subcommands = Literal[tuple(subcommand_lookup.keys())]

    def extra_completions(shell: str) -> list[str]:
        out = []
        for subcommand in subcommand_lookup.values():
            out.extend(subcommand.completions(shell, name))
        return out

    @command(help=help, version=version, extra_completions=extra_completions)
    @_with_name(name)
    def run(subcommand: Subcommands = None, /, *remainder: str):  # pyright: ignore[reportInvalidTypeForm,reportRedeclaration]
        if subcommand is None:
            if default is None:
                sys.exit("Missing subcommand.")
            else:
                subcommand_fn = default
        else:
            # This lookup cannot fail, the argument-decoding step will check that
            # `subcommand` matches one of the literal `Subcommands`.
            subcommand_fn = subcommand_lookup[subcommand]
        return subcommand_fn(list(remainder))

    return run
