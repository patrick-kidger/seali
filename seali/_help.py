import dataclasses
import inspect
import itertools as it
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable

from ._arguments import Arguments, Flag


_RESET = "\033[0m"
_ansi_regex = re.compile(r"(\x1b\[[;?0-9]*[a-zA-Z])")


def _linewrap(txt: str, subsequent_indent: str, width: int) -> list[str]:
    """Wraps a single line of `txt` (no newlines) so that it fits within a `width`;
    respecting ANSI escape codes.

    Subsequent lines are indented by `subsequent_indent`.

    Returns a stream of strings: use `"".join(_textwrap(...))` to obtain the formatted
    output.

    Edge case notes:
    - If a single word is longer than `width` then it will extend past that width.
    - Leading spaces are preserved, but all other inter-word spaces will be collapsed
        into a single space. (A bit like writing Markdown).
    """
    human = {
        "\t": "t",
        "\n": "n",
        "\r": "r",
        "\f": "f",
        "\v": "v",
    }
    for char in "\t\n\r\f\v":
        if char in txt:
            raise ValueError(
                f"The only allowed whitespace is space; found \\{human[char]}."
            )
    txt = txt.rstrip()
    txt_lstrip = txt.lstrip()
    leading_spaces = len(txt) - len(txt_lstrip)
    out = [" " * leading_spaces]
    length = 0
    for i, word in enumerate(txt_lstrip.split()):
        wlength = len(_ansi_regex.sub("", word))
        if length + wlength > width:
            out.append("\n")
            out.append(subsequent_indent)
            length = len(subsequent_indent)
        elif i != 0:
            out.append(" ")
            length += 1
        out.append(word)
        length += wlength
    return out


def _textwrap(txt: str, width: int) -> list[str]:
    r'''Wraps a piece of text so that it consumes no more than `width`; respecting ANSI
    escape codes.

    Whitespace rules:
    - leading spaces on each line are preserved.
    - single newlines, and any number of spaces, are treated as interword spaces. These
        will be collapsed into either a single space or  single newline, according to
        the wrapping.
    - interparagraph spaces are denoted with a double `\n\n`. Paragraphs are separated
        by `\n\n` in the output too.
    - a forced line break (within a paragraph) is denoted `\v`.
    - if you would like wrapped lines to be indented from the left hand edge, then place
        a `\f` within the line. This denotes how far wrapped lines should be indented
        (and will not appear in the output).

    Example:
    ```python
    red = "\x1b[31m"
    reset = "\x1b[0m"
    input_text = f"""
    {red}-i\f{reset}, {red}--input <file>{reset}: where to get the input for this
    operation

    {red}-o\f{reset}, {red}--output <file>{reset}: where to save the output of this
    operation
    """
    wrapped_text = _textwrap(input_text, width=30)
    print("".join(wrapped_text))
    ```
    produces (with colour):
    ```
    -i, --input <file>: where to
      get the input for this
      operation

    -o, --output <file>: where to
      save the output of this
      operation
    ```
    '''
    out_stream = []
    for i, paragraph in enumerate(txt.lstrip("\n").rstrip("\n").split("\n\n")):
        if i != 0:
            out_stream.append("\n\n")
        for j, line in enumerate(
            paragraph.replace("\n", " ").replace("\v ", "\v").split("\v")
        ):
            if j != 0:
                out_stream.append("\n")
            try:
                tabstop = line.index("\f")
            except ValueError:
                words = _linewrap(line, width=width, subsequent_indent="")
            else:
                leader = line[:tabstop]
                trailer = line[tabstop + 1 :]
                if "\f" in trailer:
                    raise ValueError("Cannot have multiple \\f in a single line.")
                words = _linewrap(
                    leader + trailer,
                    width=width,
                    subsequent_indent=" " * len(_ansi_regex.sub("", leader)),
                )
            out_stream.extend(words)
    return out_stream


def _insert_tabstop_at_index(line: str, index: int) -> str:
    assert index >= 0
    length = newlength = 0
    out = []
    pieces = iter(_ansi_regex.split(line))
    for piece in pieces:
        if not _ansi_regex.match(piece):
            newlength = length + len(piece)
            if newlength <= index:
                length = newlength
            else:
                out.append(piece[: index - length])
                out.append("\f")
                out.append(piece[index - length :])
                out.extend(pieces)
                break
        out.append(piece)
    if newlength <= index:
        out.append(" " * (index - newlength))
        out.append("\f")
    return "".join(out)


def _indent(txt: str, prefix: str) -> str:
    out = []
    for line in txt.split("\n"):
        out.append(prefix + line)
    return "\n".join(out)


def _to_callable(x: str | Callable[[str], str]):
    if callable(x):
        return x
    else:
        return lambda y: x + y


@dataclasses.dataclass(frozen=True)
class Style:
    """Defines the styles (what to bold, what to colour, etc.) within a help message.

    This is a separate class to `seali.Help` to allow for manually calling its methods
    whilst constructing the help message, e.g. to insert a custom heading.
    """

    _cmd: Callable[[str], str]
    _heading: Callable[[str], str]
    _positional: Callable[[str], str]
    _option_or_flag: Callable[[str], str]
    indent: int
    width: int

    def __init__(
        self,
        *,
        cmd: str | Callable[[str], str] = "",
        heading: str | Callable[[str], str] = "",
        positional: str | Callable[[str], str] = "",
        option_or_flag: str | Callable[[str], str] = "",
        indent: int = 2,
        width: int = 80,
    ):
        """Most of the following arguments are prefixed to some part of the help
        message. This can be used either to add raw characters (e.g. use 'heading="# "
        to add a '#' before all headings) or to add ANSI escape codes (e.g. use
        `heading=seali.BOLD` to make all headings both) – or both (e.g.
        `heading=seali.BOLD + "# "`)!

        **Arguments:**

        - `cmd`: prefix applied to, or function called on, the name of the command in
            the help message.
        - `heading`: prefix applied, or function called on, every heading in the help
            message.
        - `positional`: prefix applied, or function called on, every positional argument
            in the help message.
        - `option_or_flag`: prefix applied, or function called on, every option and flag
            in the help message.
        - `indent`: how much to automatically indent body text below headings.
        - `width`: at what width to wrap text.
        """
        object.__setattr__(self, "_cmd", _to_callable(cmd))
        object.__setattr__(self, "_heading", _to_callable(heading))
        object.__setattr__(self, "_positional", _to_callable(positional))
        object.__setattr__(self, "_option_or_flag", _to_callable(option_or_flag))
        object.__setattr__(self, "indent", indent)
        object.__setattr__(self, "width", width)

    def cmd(self, x: str) -> str:
        """Format a string with the value provided to `__init__(cmd=...)`"""
        return self._cmd(x) + _RESET

    def heading(self, x: str) -> str:
        """Format a string with the value provided to `__init__(heading=...)`"""
        return self._heading(x) + _RESET

    def positional(self, x: str) -> str:
        """Format a string with the value provided to `__init__(positional=...)`"""
        return self._positional(x) + _RESET

    def option_or_flag(self, x: str) -> str:
        """Format a string with the value provided to `__init__(option_or_flag=...)`"""
        return self._option_or_flag(x) + _RESET


@dataclasses.dataclass(frozen=True)
class Help:
    """Defines the message that appears when a command is ran with `-h` or `--help`."""

    help: str
    style: Style
    arguments: dict[str, str]
    option_prompts: dict[str, str]

    def validate(self, arguments: Arguments) -> None:
        fn_option_names = set(arguments.options.keys())
        variadic_names = (
            {arguments.variadic.name} if arguments.variadic is not None else set()
        )
        fn_argument_names = (
            {p.name for p in arguments.positional}
            | variadic_names
            | fn_option_names
            | {f.name for f in arguments.flags}
        )
        doc_option_names = set(self.option_prompts.keys())
        doc_argument_names = set(self.arguments.keys())
        extra_fn_arguments = fn_argument_names - doc_argument_names
        extra_doc_arguments = doc_argument_names - fn_argument_names
        extra_fn_options = fn_option_names - doc_option_names
        extra_doc_options = doc_option_names - fn_option_names
        errors = ["Could not produce help message."]
        if len(extra_doc_arguments) > 0:
            errors.append(
                "The following extra arguments appear in in the documented "
                f"`arguments`: {extra_doc_arguments}"
            )
        if len(extra_doc_options) > 0:
            errors.append(
                "The following extra options appear in the documented "
                f"`option_prompts`: {extra_doc_options}"
            )
        if len(extra_fn_arguments) > 0:
            errors.append(
                f"The following arguments are not documented in "
                f"`arguments`: {extra_fn_arguments}"
            )
        if len(extra_fn_options) > 0:
            errors.append(
                f"The following options are not documented in "
                f"`option_prompts`: {extra_fn_options}"
            )
        if len(errors) > 1:
            raise ValueError("\n\n".join(errors))

    def format(self, name: str, arguments: Arguments) -> str:
        self.validate(arguments)
        usage = [
            self.style.heading("Usage"),
            "\n\n",
            " " * self.style.indent,
            self.style.cmd(name),
        ]
        if len(arguments.positional) > 0 or arguments.variadic is not None:
            usage.append(" ")
            if arguments.variadic is None:
                usage.append(self.style.positional("[POSITIONAL]"))
            else:
                usage.append(self.style.positional("[POSITIONAL...]"))
        if len(arguments.flags) > 0 or len(arguments.options):
            usage.append(" ")
            usage.append(self.style.option_or_flag("[OPTIONS AND FLAGS]"))

        positional = [self.style.heading("Positional")]
        for param in (
            arguments.positional
            if arguments.variadic is None
            else it.chain(arguments.positional, [arguments.variadic])
        ):
            name = self.style.positional(param.name)
            doc = inspect.cleandoc(self.arguments[param.name])
            if doc == "":
                name_doc = name
            else:
                name_doc = f"{name}: {doc}"
            name_doc = _insert_tabstop_at_index(name_doc, self.style.indent)
            positional.append("\n\n")
            positional.append(_indent(name_doc, " " * self.style.indent))

        options_and_flags = [self.style.heading("Options and flags")]
        options_and_flags_names = list(arguments.options)
        options_and_flags_names.extend([f.name for f in arguments.flags])
        options_and_flags_names.sort()
        has_short = set(arguments.short_to_long.values())
        for name in options_and_flags_names:
            if name in has_short:
                short_piece = self.style.option_or_flag("-" + name[0]) + ","
            else:
                short_piece = "   "
            long_piece = self.style.option_or_flag("--" + name.replace("_", "-"))
            doc = inspect.cleandoc(self.arguments[name])
            if Flag(name) in arguments.flags:
                if doc == "":
                    name_doc = f"{short_piece} {long_piece}"
                else:
                    name_doc = f"{short_piece} {long_piece}: {doc}"
                name_doc = _insert_tabstop_at_index(name_doc, self.style.indent)
                options_and_flags.append("\n\n")
                options_and_flags.append(_indent(name_doc, " " * self.style.indent))
            else:
                prompt = inspect.cleandoc(self.option_prompts[name])
                prompt = self.style.option_or_flag(f"<{prompt}>")
                if doc == "":
                    name_doc = f"{short_piece} {long_piece} {prompt}"
                else:
                    name_doc = f"{short_piece} {long_piece} {prompt}: {doc}"
                name_doc = _insert_tabstop_at_index(name_doc, self.style.indent)
                options_and_flags.append("\n\n")
                options_and_flags.append(_indent(name_doc, " " * self.style.indent))

        doc = inspect.cleandoc(self.help).strip()
        doc = doc.replace("$USAGE", "".join(usage))
        doc = doc.replace("$POSITIONAL", "".join(positional))
        doc = doc.replace("$OPTIONS_AND_FLAGS", "".join(options_and_flags))
        docstream = _textwrap(doc, self.style.width)
        return "".join(docstream)

    def pager(self, name: str, arguments: Arguments) -> None:
        usage_str = self.format(name, arguments)
        if sys.stdin.isatty():
            pager = os.environ.get("PAGER")
            if pager is None or pager == "":
                less_path = shutil.which("less")
                if less_path is None:
                    print(usage_str)
                else:
                    process = subprocess.Popen(
                        [less_path, "-R"], stdin=subprocess.PIPE, text=True
                    )
                    process.communicate(input=usage_str)
            else:
                process = subprocess.Popen(
                    pager, shell=True, stdin=subprocess.PIPE, text=True
                )
                process.communicate(input=usage_str)
        else:
            print(usage_str)


Help.__init__.__doc__ = """**Arguments:**

- `help`: the documentation to appear when running with `-h` or `--help`.

    Use [ANSI escape codes](./ansi.md) to create bold, colour, etc. If the string
    `$USAGE`, `$POSITIONAL` or `$OPTIONS_AND_FLAGS` appear then they will be replaced
    with autogenerated descriptions of how the program should be called.

    Text will flow like Markdown: spaces and newline are equivalent, and two adjacent
    newlines mark the start of a paragraph.

    Use a `\\v` anywhere within a paragraph to create a hard line break, and up to one
    `\\f` per paragraph to mark the indent which text should wrap to.

- `style`: a [`seali.Style`][] object describing how headings etc. should be
    formatted.

- `arguments`: a dictionary, mapping argument name to the description that appears in
    the `$POSITIONAL` and `$OPTIONS_AND_FLAGS` substitutions. All positional arguments,
    options, and flags must be present.

- `option_prompts`: a dictionary, mapping option name to prompt name. This is the 'foo'
    that appears in the `-o, --output <foo>` in the `$OPTIONS_AND_FLAGS` substitution.
"""
