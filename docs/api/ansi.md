# ANSI escape codes (style, colour)

We use [ANSI escape codes](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797) to format documentation. You can type these in to your docstrings directly, or (more readable), you can also use the aliases we provide.

::: tinycli.RESET

## Styles

Use within an f-string as `f"...{tinycli.BOLD}red text here{tinycli.RESET}..."` to set the style.

::: tinycli.BOLD
::: tinycli.FAINT
::: tinycli.ITALIC
::: tinycli.UNDERLINE

## Colours (standard)

Use within an f-string as `f"...{tinycli.RED}red text here{tinycli.RESET}..."` to set the foreground (text) colour.

Use as `f"...{tinycli.RED.bg}..."` to set the background colour.

Use as `f"...{tinycli.RED.bright}..."` to set the foreground (text) colour to the bright version of that colour.

Use as `f"...{tinycli.RED.bright_bg}..."` to set the background colour to the bright version of that colour.

::: tinycli.BLACK
::: tinycli.RED
::: tinycli.GREEN
::: tinycli.YELLOW
::: tinycli.BLUE
::: tinycli.MAGENTA
::: tinycli.CYAN
::: tinycli.WHITE

## Colours (RGB)

::: tinycli.RGB
    options:
        members:
            - __init__
