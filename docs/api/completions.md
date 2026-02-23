# Completions

Completions are available for the `fish` shell.

If your CLI is available from the command line as `foo`, then add the following to `~/.config/fish/completions/foo.fish`:

```fish
foo --completions fish | source
```

Completions are generated based on type annotations:

- `Literal[...]` will suggest the provided values.
- `seali.Dir` may be wrapped around a `str` or `pathlib.Path` to perform file-based completions:
    - `seali.Dir[str/pathlib.Path, pathlib.Path(path) / to / folder]` will suggest the files/folders in that directory as completions.
    - `seali.Dir[str/pathlib.Path, None]` will suggest any file/folder as completions.
- `Union`s will suggest the union of the completions of their components.
- `seali.NoComplete` may be wrapped around an annotation to suppress completions. For example `Foo | NoComplete[Bar]` will suggest whatever completions come from `Foo` without suggesting those that come from `Bar`.
