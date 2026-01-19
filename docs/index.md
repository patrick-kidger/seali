# tinycli

A does-one-thing-well library for building CLIs.

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
