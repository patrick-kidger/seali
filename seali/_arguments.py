import dataclasses
import inspect
import re
import string
from collections.abc import Callable
from typing import Any, cast

from ._decode import decode, DecodeError


_short_name = re.compile(r"-[a-zA-Z]")
_long_name = re.compile(r"--[a-zA-Z][a-zA-Z_-]*")
_sentinel = object()


def _is_numeric(x: str) -> bool:
    try:
        float(x)
    except ValueError:
        return False
    else:
        return True


def _decode(arg: str, name: str, annotation: Any) -> Any:
    assert annotation is not inspect.Signature.empty
    try:
        return decode(arg, name, annotation)
    except DecodeError as e:
        raise UsageError(str(e))


class UsageError(SystemExit):
    pass


@dataclasses.dataclass(frozen=True)
class Positional:
    name: str
    annotation: Any
    default: Any


@dataclasses.dataclass(frozen=True)
class Variadic:
    name: str
    annotation: Any


@dataclasses.dataclass(frozen=True)
class Option:
    name: str
    annotation: Any
    default: Any


@dataclasses.dataclass(frozen=True)
class Flag:
    name: str


@dataclasses.dataclass(frozen=True)
class ParsedArguments:
    args: list[Any]
    kwargs: dict[str, Any]


@dataclasses.dataclass(frozen=True)
class Arguments:
    positional: list[Positional]
    variadic: None | Variadic
    options: dict[str, Option]
    flags: set[Flag]
    short_to_long: dict[str, str]

    @classmethod
    def from_callable(cls, fn: Callable) -> "Arguments":
        positional: list[Positional] = []
        variadic = None
        options: dict[str, Option] = {}
        flags: set[Flag] = set()
        short_to_long = {}

        allowed_chars = set(string.ascii_lowercase) | {"_"}
        for param in inspect.signature(fn).parameters.values():
            if not set(param.name).issubset(allowed_chars):
                raise ValueError(
                    f"Argument '{param.name}': must use only lowercase letters or "
                    "underscores."
                )
            if param.name[0] not in string.ascii_lowercase:
                raise ValueError(
                    f"Argument '{param.name}': must start with a lowercase letter."
                )
            if param.annotation is inspect.Signature.empty:
                raise ValueError(f"Argument '{param.name}': must be type-annotated.")

            match param.kind:
                case inspect.Parameter.POSITIONAL_ONLY:
                    positional.append(
                        Positional(param.name, param.annotation, param.default)
                    )
                case inspect.Parameter.KEYWORD_ONLY:
                    if param.name == "help":
                        raise ValueError(
                            "Argument name 'help' is reserved for use with `--help`."
                        )
                    if param.name == "completions":
                        raise ValueError(
                            "Argument name 'completions' is reserved for use with "
                            "`--completions <SHELL>`."
                        )
                    short = param.name[0]
                    if short not in short_to_long.keys() and not (short == "h"):
                        short_to_long[short] = param.name
                    if param.annotation is bool:
                        if param.default is not False:
                            raise ValueError(
                                f"Argument '{param.name}': all flags (boolean types) "
                                "must have default `False`."
                            )
                        flags.add(Flag(param.name))
                    else:
                        options[param.name] = Option(
                            param.name, param.annotation, param.default
                        )
                case inspect.Parameter.VAR_POSITIONAL:
                    variadic = Variadic(param.name, param.annotation)
                case _:
                    raise ValueError(
                        f"Argument '{param.name}': all arguments must be "
                        "positional-only (before a `/`), keyword-only (after a `*`), "
                        "or the variadic `*args`."
                    )

        return cls(positional, variadic, options, flags, short_to_long)

    def parse(self, argv: list[str]) -> ParsedArguments:
        iter_argv = iter(argv)
        iter_positional = iter(self.positional)
        del argv

        args = []
        variadic = []
        kwargs = {}
        not_force_positional = True
        while True:
            try:
                arg = next(iter_argv)
            except StopIteration:
                break
            if not_force_positional and arg == "--":
                not_force_positional = False
            elif not_force_positional and arg.startswith("-") and not _is_numeric(arg):
                # Option or flag.
                # Note the `_is_numeric` check is not ambiguous as e.g. `-5` must always
                # refer to a positional negative integer, and never a flag, as our flags
                # must be Python identifiers, which cannot start with a number.
                if "=" in arg:
                    name, value = arg.split("=", maxsplit=1)
                else:
                    name = arg
                    value = _sentinel
                if _short_name.match(name):
                    try:
                        fullname = self.short_to_long[name[1]]
                        err = None
                    except KeyError:
                        fullname = None
                        err = f"Unrecognized single-letter abbreviation '{arg}'."
                elif _long_name.match(name):
                    fullname = name.removeprefix("--").replace("-", "_")
                    err = f"Unrecognized flag or option '{fullname}'."
                else:
                    raise UsageError(f"Malformed argument '{arg}'.")
                if fullname is not None and Flag(fullname) in self.flags:
                    if value is _sentinel:
                        if fullname in kwargs:
                            raise UsageError(
                                f"Flag '{fullname}' passed multiple times."
                            )
                        kwargs[fullname] = True
                    else:
                        raise UsageError(
                            "Flags should not be called with `--foo=bar` syntax, but "
                            f"got `{arg}`."
                        )
                elif fullname is not None and fullname in self.options:
                    if fullname in kwargs:
                        raise UsageError(f"Option '{fullname}' passed multiple times.")
                    if value is _sentinel:
                        try:
                            value = next(iter_argv)
                        except StopIteration:
                            raise UsageError(
                                f"Option '{fullname}' was passed without any value."
                            )
                    value = cast(str, value)
                    option = self.options[fullname]
                    kwargs[fullname] = _decode(value, option.name, option.annotation)
                elif self.variadic is not None:
                    # This may seem surprising: if we have a variadic *positional*
                    # argument then we gather all unrecognized options/flags into it as
                    # well, directly using the raw `arg` that was passed on the command
                    # line.
                    #
                    # Perhaps we should be gathering such inputs into a `**kwargs`
                    # instead?
                    #
                    # The reason for this is to allow a command to gather up all inputs
                    # that it doesn't recognize without trying to determine if they are
                    # positional/flags/options. Otherwise, is `--unrecognized-arg foo`
                    # an unrecognized flag followed by a positional argument, or is it
                    # an unrecogized option with value `foo`? We can't know, as by
                    # definition we don't recognize `unrecognized-arg`!
                    #
                    # In particular this use-case comes up when implementing
                    # subcommands. When we run `mycli subcmd --foo 3`, then `mycli`
                    # receives`["subcmd", "--foo", "3"]`, and we would like to defer
                    # processing the `--foo 3` until we re-dispatch to the `subcmd`.
                    # `mycli` doesn't yet know if this is a flag+positional, or an
                    # option.
                    variadic.append(
                        _decode(arg, self.variadic.name, self.variadic.annotation)
                    )
                else:
                    assert err is not None
                    raise UsageError(err)
            else:
                # Positional
                if len(variadic) > 0:
                    # We have started accumulating unknown flags etc. into the
                    # variadic portion. We should also treat positional arguments as
                    # variadic, so that e.g. `--opt 5` will work, and not have the
                    # `5` be treated positionally.
                    assert self.variadic is not None
                    variadic.append(
                        _decode(arg, self.variadic.name, self.variadic.annotation)
                    )
                else:
                    try:
                        positional = next(iter_positional)
                    except StopIteration:
                        if self.variadic is None:
                            raise UsageError(f"Unexpected positional argument '{arg}'.")
                        else:
                            variadic.append(
                                _decode(
                                    arg, self.variadic.name, self.variadic.annotation
                                )
                            )
                    else:
                        args.append(
                            _decode(arg, positional.name, positional.annotation)
                        )

        for positional in iter_positional:
            if positional.default is inspect.Signature.empty:
                raise UsageError(f"Missing positional argument '{positional.name}'.")
            else:
                # We don't just let the default be filled in automatically by Python,
                # in case we have unknown flags/options being collected into `variadic`.
                args.append(positional.default)
        for name, option in self.options.items():
            if option.default is inspect.Signature.empty and name not in kwargs:
                raise UsageError(f"Missing option '{name}'.")

        return ParsedArguments(args + variadic, kwargs)
