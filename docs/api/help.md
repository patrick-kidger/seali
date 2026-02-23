# Help messages

::: seali.Help
    options:
        members:
            - __init__

::: seali.Style
    options:
        members:
            - __init__
            - cmd
            - heading
            - positional
            - option_or_flag

!!! Example

    The following:
    ```python
    import seali

    style = seali.Style(
      cmd=seali.BOLD,
      heading=lambda x: seali.BOLD + x + ":",
      positional=seali.RED,
      option_or_flag=seali.RED,
      indent=2,
      width=80,
    )

    help = seali.Help(
      f"""
      Help message here. Text flows like Markdown: spaces
      and newlines are equivalent, and paragraphs reflow to the
      specified width.

      Paragraphs are separated by two newlines.

      Hard line breaks can be inserted with a backslash-v:\v
      This text will be in the same paragraph but on a new line.

      (a) \fa backslash-f can be used to insert up to one tabstop per
       line. So if the text here flows for a really really long time
       then that is fine, it will be indented to reflow after the
      '(a)' label.

      (b) \fwhich can be useful when building bulleted lists.

      The usage summary can be inserted with:

      $USAGE

      The list of all positional arguments, and their documentation,
      can be inserted with:

      $POSITIONAL

      The list of all options and flags, and their documentation,
      can be inserted with:

      $OPTIONS_AND_FLAGS

      Use ANSI escape codes to create bold, colour, etc:
      {seali.BOLD}{seali.RED}This text will be bold and in red{seali.RESET}
      """,
      style=style,
      arguments=dict(
          pos="Some position, this is its docstring, it goes on for a short while.",
          opt="Some option, this is its docstring, it goes on for a short while.",
          flag="Some flag, this is its docstring, it goes on for a short while.",
      ),
      option_prompts=dict(opt="foo"),
    )

    @seali.command(help=help)
    def my_program(pos: str, /, *, opt: int, flag: bool = False): ...

    if __name__ == "__main__":
        my_program()
    ```

    produces:

    ---

    <span style="font-family: monospace; font-size: 0.9em;">Help message here. Text flows like Markdown: spaces and newlines are equivalent,<br>
    and paragraphs reflow to the specified width.
    <br><br>
    Paragraphs are separated by two newlines.
    <br><br>
    Hard line breaks can be inserted with a backslash-v:<br>
    This text will be in the same paragraph but on a new line.
    <br><br>
    (a) a backslash-f can be used to insert up to one tabstop per line. So if the<br>
    &nbsp;&nbsp;&nbsp;&nbsp;text here flows for a really really long time then that is fine, it will be<br>
    &nbsp;&nbsp;&nbsp;&nbsp;indented to reflow after the '(a)' label.
    <br><br>
    (b) which can be useful when building bulleted lists.
    <br><br>
    The usage summary can be inserted with:
    <br><br>
    <b>Usage:</b>
    <br><br>
    &nbsp;&nbsp;<b>my_program</b> <span style="color: red;">\[POSITIONAL\] \[OPTIONS AND FLAGS\]</span>
    <br><br>
    The list of all positional arguments, and their documentation, can be inserted<br>
    with:
    <br><br>
    <b>Positional:</b>
    <br><br>
    &nbsp;&nbsp;<span style="color: red;">pos</span>: Some position, this is its docstring, it goes on for a short while.
    <br><br>
    The list of all options and flags, and their documentation, can be inserted with:
    <br><br>
    <b>Options and flags:</b>
    <br><br>
    &nbsp;&nbsp;<span style="color: red;">-f</span>, <span style="color: red;">--flag</span>: Some flag, this is its docstring, it goes on for a short while.
    <br><br>
    &nbsp;&nbsp;<span style="color: red;">-o</span>, <span style="color: red;">--opt &lt;foo&gt;</span>: Some option, this is its docstring, it goes on for a short<br>
    &nbsp;&nbsp;&nbsp;&nbsp;while.
    <br><br>
    Use ANSI escape codes to create bold, colour, etc: <b><span style="color: red;">This text will be bold and in<br>
    red</span></b>
    </span>
