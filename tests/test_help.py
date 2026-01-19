import re

import pytest
import tinycli
from tinycli._help import _insert_tabstop_at_index, _textwrap


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
    style = tinycli.Style(
        cmd="wahoo",
        heading=lambda x: f"# {x}:",
        positional=">",
        option_or_flag="!",
        indent=2,
        width=50,
    )
    help = tinycli.Help(
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

    @tinycli.command(help=help)
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


def test_subcommand(capfd):
    subhelp = tinycli.Help("subhelp", tinycli.Style(), {}, {})
    mainhelp = tinycli.Help(
        "mainhelp", tinycli.Style(), dict(subcommand="subcommand"), {}
    )

    @tinycli.command(help=subhelp)
    def sub():
        pass

    main = tinycli.group(name="main", help=mainhelp, subcommands=[sub])

    with pytest.raises(SystemExit):
        main(["--help"])
    captured = capfd.readouterr().out.strip()
    assert captured == "mainhelp"

    with pytest.raises(SystemExit):
        main(["sub", "--help"])
    captured = capfd.readouterr().out.strip()
    assert captured == "subhelp"
