# ANSI escape codes (style, colour)

We use [ANSI escape codes](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797) to format documentation. You can type these in to your docstrings directly, or (more readable), you can also use the aliases we provide.

::: seali.RESET

## Styles

Use within an f-string as `f"...{seali.BOLD}red text here{seali.RESET}..."` to set the style.

::: seali.BOLD
::: seali.FAINT
::: seali.ITALIC
::: seali.UNDERLINE

## Colours (standard)

Use within an f-string as `f"...{seali.RED}red text here{seali.RESET}..."` to set the foreground (text) colour.

Use as `f"...{seali.RED.bg}..."` to set the background colour.

Use as `f"...{seali.RED.bright}..."` to set the foreground (text) colour to the bright version of that colour.

Use as `f"...{seali.RED.bright_bg}..."` to set the background colour to the bright version of that colour.

::: seali.BLACK
::: seali.RED
::: seali.GREEN
::: seali.YELLOW
::: seali.BLUE
::: seali.MAGENTA
::: seali.CYAN
::: seali.WHITE

## Colours (RGB)

::: seali.RGB
    options:
        members:
            - __init__
