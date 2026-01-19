<h1 align='center'><code>tinycli</code></h1>

A does-one-thing-well library for building CLIs.<br>
Designed to be trivially easy to use.

- Zero dependencies;
- Subcommands;
- Fish completions;
- Elegant `--help` messages (with line-breaks, tab-stops, and ANSI escape codes);
- Tiny day-to-day API: `tinycli.{command, group, Doc, Style}`.

_This exists because I wanted ✨pretty help text✨ beyond what any other CLI library supports._

## Installation

```bash
pip install tinycli
```

## Example

```python
import tinycli

@tinycli.command
def my_program(pos: str, /, *, someflag: bool = False):
    ...

if __name__ == "__main__":
    my_program()
```

```
python this_file.py foobar --someflag
```

## Documentation

Available at <https://docs.kidger.site/tinycli>.

## Alternatives

- [`fire`](https://github.com/google/python-fire) was the main inspiration for `tinycli`.<br>
    I love their 'trivial to use' UX: just call the library on your function. Relative to `fire`, we aim to minimise their massive surface area (they also allow you to decorate classes, dictionaries, ..., have an interactive mode, a trace mode, ...), and fix some UX issues (e.g. `-s` short flags, help messages) for a simpler more opinionated library.

- [`click`](https://github.com/pallets/click/) is the 'standard' choice for Python CLIs.<br>
    Honourary mention to other similar libraries that live in this niche, for example [`typer`](https://github.com/fastapi/typer) or [`rich-click`](https://github.com/ewels/rich-click).<br>
    We aim to be (a) smaller/simpler and (b) offer a few nice UX features like fully customisable help messages.

- [`argparse`](https://docs.python.org/3/library/argparse.html) is in the Python stdlib.<br>
    This is usually noted for being highly verbose. We aim to be much easier to use.

As a particular focus, we aim to offer best-in-class help messages, with support for reflowing, tabstops, and respecting ANSI escape codes.
