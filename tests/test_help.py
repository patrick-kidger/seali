import re

import pytest
import seali
from seali._help import _insert_tabstop_at_index, _textwrap


_ansi_regex = re.compile(r"(\x1b\[[;?0-9]*[a-zA-Z])")


def test_insert_tabstop_at_index():
    x = "hi\x1b[31mbye"
    assert _insert_tabstop_at_index(x, 0) == "\fhi\x1b[31mbye"
    assert _insert_tabstop_at_index(x, 1) == "h\fi\x1b[31mbye"
    assert _insert_tabstop_at_index(x, 2) == "hi\x1b[31m\fbye"
    assert _insert_tabstop_at_index(x, 3) == "hi\x1b[31mb\fye"
    assert _insert_tabstop_at_index(x, 4) == "hi\x1b[31mby\fe"
    assert _insert_tabstop_at_index(x, 5) == "hi\x1b[31mbye\f"
    assert _insert_tabstop_at_index(x, 6) == "hi\x1b[31mbye \f"
    assert _insert_tabstop_at_index(x, 7) == "hi\x1b[31mbye  \f"


def test_textwrap():
    red = "\x1b[31m"
    reset = "\x1b[0m"
    input_text = f"""
{red}-i\f{reset}, {red}--input <file>{reset}: where to get the input for this
operation

{red}-o\f{reset}, {red}--output <file>{reset}: where to save the output of this
operation
"""
    wrapped_text = _textwrap(input_text, width=30)
    result = "".join(wrapped_text)
    expected_result = f"""{red}-i{reset}, {red}--input <file>{reset}: where to
  get the input for this
  operation

{red}-o{reset}, {red}--output <file>{reset}: where to
  save the output of this
  operation"""
    assert result == expected_result


def test_doc_basic(capfd):
    style = seali.Style(
        cmd="wahoo",
        heading=lambda x: f"# {x}:",
        positional=">",
        option_or_flag="!",
        indent=2,
        width=50,
    )
    help = seali.Help(
        """
        $USAGE

        $POSITIONAL

        $OPTIONS_AND_FLAGS

        some\v
        thoughts\f that go on for quite a while and will need to wrap
        """,
        style=style,
        arguments=dict(
            pos="Some position, this its docstring, it goes on for a short while.",
            opt="Some option, this its docstring, it goes on for a short while.",
            flag="Some flag, this its docstring, it also goes on for a short while.",
        ),
        option_prompts=dict(opt="foo"),
    )

    @seali.command(help=help)
    def foo(pos: int, /, *, opt: str, flag: bool = False):
        del pos, opt, flag

    with pytest.raises(SystemExit):
        foo(["--help"])
    captured = capfd.readouterr().out
    captured = _ansi_regex.sub("", captured)
    expected = """# Usage:

  wahoofoo >[POSITIONAL] ![OPTIONS AND FLAGS]

# Positional:

  >pos: Some position, this its docstring, it goes on
    for a short while.

# Options and flags:

  !-f, !--flag: Some flag, this its docstring, it
    also goes on for a short while.

  !-o, !--opt !<foo>: Some option, this its
    docstring, it goes on for a short while.

some
thoughts that go on for quite a while and will need
        to wrap
"""
    assert captured == expected


def test_doc_variadic(capfd):
    style = seali.Style(
        cmd="wahoo",
        heading=lambda x: f"# {x}:",
        positional=">",
        option_or_flag="!",
        indent=2,
        width=60,
    )
    help = seali.Help(
        """
        $USAGE

        $POSITIONAL

        $OPTIONS_AND_FLAGS
        """,
        style=style,
        arguments=dict(
            pos="Some position.",
            args="Extra arguments.",
            opt="Some option.",
        ),
        option_prompts=dict(opt="foo"),
    )

    @seali.command(help=help)
    def foo(pos: int, /, *args: str, opt: str):
        del pos, args, opt

    with pytest.raises(SystemExit):
        foo(["--help"])
    captured = capfd.readouterr().out
    captured = _ansi_regex.sub("", captured)
    expected = """# Usage:

  wahoofoo >[POSITIONAL...] ![OPTIONS AND FLAGS]

# Positional:

  >pos: Some position.

  >args: Extra arguments.

# Options and flags:

  !-o, !--opt !<foo>: Some option.
"""
    assert captured == expected


def test_doc_variadic_only(capfd):
    style = seali.Style(
        heading=lambda x: f"# {x}:",
        positional=">",
        indent=2,
        width=50,
    )
    help = seali.Help(
        """
        $USAGE

        $POSITIONAL
        """,
        style=style,
        arguments=dict(args="All the arguments."),
        option_prompts={},
    )

    @seali.command(help=help)
    def foo(*args: str):
        del args

    with pytest.raises(SystemExit):
        foo(["--help"])
    captured = capfd.readouterr().out
    captured = _ansi_regex.sub("", captured)
    expected = """# Usage:

  foo >[POSITIONAL...]

# Positional:

  >args: All the arguments.
"""
    assert captured == expected


def test_doc_variadic_missing():
    style = seali.Style()
    help = seali.Help(
        "$USAGE\n\n$POSITIONAL",
        style=style,
        arguments=dict(pos="Some position."),
        option_prompts={},
    )

    @seali.command(help=help)
    def foo(pos: int, /, *args: str):
        del pos, args

    with pytest.raises(ValueError, match="not documented"):
        foo(["--help"])


def test_group_help_valid(capfd):
    help = seali.Help(
        "$USAGE\n\n$POSITIONAL",
        seali.Style(),
        dict(subcommand="subcommand", remainder="remaining arguments"),
        {},
    )

    @seali.command
    def sub():
        pass

    main = seali.group(name="main", help=help, subcommands=[sub])
    with pytest.raises(SystemExit):
        main(["--help"])
    captured = capfd.readouterr().out
    assert "subcommand" in captured
    assert "remaining arguments" in captured


def test_group_help_missing_subcommand():
    help = seali.Help(
        "$USAGE\n\n$POSITIONAL",
        seali.Style(),
        dict(remainder="remaining arguments"),
        {},
    )

    @seali.command
    def sub():
        pass

    main = seali.group(name="main", help=help, subcommands=[sub])
    with pytest.raises(ValueError, match="not documented"):
        main(["--help"])


def test_group_help_missing_remainder():
    help = seali.Help(
        "$USAGE\n\n$POSITIONAL",
        seali.Style(),
        dict(subcommand="subcommand"),
        {},
    )

    @seali.command
    def sub():
        pass

    main = seali.group(name="main", help=help, subcommands=[sub])
    with pytest.raises(ValueError, match="not documented"):
        main(["--help"])


def test_group_help_missing_both():
    help = seali.Help(
        "$USAGE\n\n$POSITIONAL",
        seali.Style(),
        {},
        {},
    )

    @seali.command
    def sub():
        pass

    main = seali.group(name="main", help=help, subcommands=[sub])
    with pytest.raises(ValueError, match="not documented"):
        main(["--help"])


def test_subcommand(capfd):
    subhelp = seali.Help("subhelp", seali.Style(), {}, {})
    mainhelp = seali.Help(
        "mainhelp",
        seali.Style(),
        dict(subcommand="subcommand", remainder="remaining arguments"),
        {},
    )

    @seali.command(help=subhelp)
    def sub():
        pass

    main = seali.group(name="main", help=mainhelp, subcommands=[sub])

    with pytest.raises(SystemExit):
        main(["--help"])
    captured = capfd.readouterr().out.strip()
    assert captured == "mainhelp"

    with pytest.raises(SystemExit):
        main(["sub", "--help"])
    captured = capfd.readouterr().out.strip()
    assert captured == "subhelp"
