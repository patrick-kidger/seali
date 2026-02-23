# FAQ

## How does `seali` compare to `click`, `fire`, etc?

As compared to the alternatives, we aim to be much simpler (even simpler than `fire`!)

This is accomplished through being more opinionated (e.g. all boolean flags must default to `False`).

As a particular focus, we aim to offer best-in-class customisation of help messages, with support for reflowing, tabstops, and respecting ANSI escape codes.

(That said, this is obviously a crowded field, and this library mostly exists to scratch a personal itch.)

## Design choices?

### Decorating functions vs deserializing dataclasses?

CLI libraries tend to use one of two styles:

- they either add a `@decorator` on top of a function, and deserialize `sys.argv[1:]` into its arguments;
- or they have you define a `@dataclass`, and deserialize `sys.argv[1:]` into an instance of that class (and perhaps let you handle calling the function yourself).

For example, `click` and `fire` follow the first strategy, whilst `clap` (in the Rust ecosystem) follows the second strategy.

The reason we went for the first strategy is because it offers a neater generalisation to subcommands: they are obtained as an implementation of the existing logic, rather than requiring a conceptually separate identify-the-right-subcommand-i.e.-dataclass step.

### Separate `seali.Help` versus using the function docstring?

We do not use function docstrings because docstrings cannot be f-strings. (Niche Python fact for you there.) It's fairly common to want to interpolate in extra information (like ANSI escape codes for colours).

### Separate `seali.Help` object vs attaching the documentation to each argument?

An alternate approach to defining the documentation would have been to attach it to each argument – probably each type annotation – like:

```python
some_arg: Help[int, "arg doc here"]
```

Likewise we could imagine introducing some kind of `Option(prompt="foo", doc="bar")`, instead of the existing approach that requires matching up each function arguments `argname` with `seali.Help(arguments=dict(argname=...))` and `seali.Help(option_prompts=dict(argname=...))`

We decide against this for two reasons:

1. slightly smoother onboarding: your first draft of a CLI won't have docs, so this keeps them out of the way until then.
2. keeps logic together, keeps documentation together: the function and its arguments are held together, and all documentation are held together. Whenever each piece is being considered, then typically the other is not.
