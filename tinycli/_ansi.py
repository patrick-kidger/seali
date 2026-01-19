# Credit to https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797 for
# documenting these.

import dataclasses
import re

from ._doc_utils import doc_attr


_ansi_regex = re.compile(r"\x1b\[[;?0-9]*[a-zA-Z]")


def ansi_strip(text: str) -> str:
    """Removes all ANSI codes from a string."""
    return _ansi_regex.sub("", text)


class Colour:
    def __init__(self, index: int):
        self.index = index

    def __repr__(self):
        return f"\x1b[3{self.index}m"

    @property
    def bg(self):
        return f"\x1b[4{self.index}m"

    @property
    def bright(self):
        return f"\x1b[9{self.index}m"

    @property
    def bright_bg(self):
        return f"\x1b[10{self.index}m"


@dataclasses.dataclass(frozen=True)
class RGB:
    """Create an ANSI colour of red/green/blue.

    Use within an f-string as
    ```python
    colour = tinycli.RGB(r=10, g=255, b=45)
    f"...{colour}coloured text here{tinycli.RESET}..."
    ```
    to set the foreground (text) colour, and
    ```python
    colour = tinycli.RGB(r=10, g=255, b=45)
    f"...{colour.bg}coloured background here{tinycli.RESET}..."
    ```
    to set the background colour.
    """

    r: int
    g: int
    b: int

    def __repr__(self):
        return f"\x1b[38;2;{self.r};{self.g};{self.b}m"

    @property
    def bg(self):
        return f"\x1b[48;2;{self.r};{self.g};{self.b}m"


RGB.__init__.__doc__ = """**Arguments:**

- `r`: the amount of red, an integer from 0 to 255 inclusive.
- `g`: the amount of green, an integer from 0 to 255 inclusive.
- `b`: the amount of blue, an integer from 0 to 255 inclusive.
"""


RESET = doc_attr(
    "\x1b[0m", "Place this in a string to reset all current styles and colours."
)
BOLD = doc_attr("\x1b[1m", None)
FAINT = doc_attr("\x1b[2m", None)
ITALIC = doc_attr("\x1b[3m", None)
UNDERLINE = doc_attr("\x1b[4m", None)
BLACK = Colour(0)
RED = Colour(1)
GREEN = Colour(2)
YELLOW = Colour(3)
BLUE = Colour(4)
MAGENTA = Colour(5)
CYAN = Colour(6)
WHITE = Colour(7)
