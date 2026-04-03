import types
from typing import Any, get_args, get_origin, Literal, Union

from ._arguments import Arguments, UsageError
from ._decode import Dir, NoComplete
from ._help import Help


# def _description(argname: str, help: Help) -> str:
#     firstline = help.arguments[argname].lstrip().splitlines()[0].replace("\f", "")
#     firstline = ansi_strip(firstline)
#     return f"'{firstline}'"


def _fish_completions_arg(annotation: Any) -> tuple[list[str], bool]:
    origin = get_origin(annotation)

    if isinstance(annotation, type) and issubclass(annotation, NoComplete):  # pyright: ignore[reportArgumentType]
        return [], False
    elif isinstance(annotation, type) and issubclass(annotation, Dir):  # pyright: ignore[reportArgumentType]
        directory = annotation.directory  # pyright: ignore[reportAttributeAccessIssue]
        if directory is None or directory == "":
            # Offer any file completion
            return [], True
        else:
            return [f"(ls {directory} 2>/dev/null)"], False
    elif origin is Literal:
        args = get_args(annotation)
        return [str(arg) for arg in args], False
    elif origin in {Union, types.UnionType}:
        completions: list[str] = []
        allow_files = False
        for arg in get_args(annotation):
            arg_completions, arg_allow_files = _fish_completions_arg(arg)
            allow_files = allow_files or arg_allow_files
            completions.extend(arg_completions)
        return completions, allow_files
    else:
        return [], False


def _fish_completions(
    cmd_name: str,
    arguments: Arguments,
    help: None | Help,
    has_version: bool,
) -> list[str]:
    # Check if cmd_name contains spaces (indicating subcommands)
    cmd_parts = cmd_name.split(maxsplit=1)
    num_tokens = cmd_name.count(" ")
    if len(cmd_parts) > 1:
        base_cmd, subcommands = cmd_parts
        subcommand_condition = f"__fish_seen_subcommand_from {subcommands}"
    else:
        base_cmd = cmd_name
        subcommand_condition = None

    lines = []

    # Help flag
    if help is not None:
        line = ["complete", "-c", base_cmd]
        contains_opt = "not __fish_contains_opt -s h help"
        if subcommand_condition is not None:
            condition = f"{subcommand_condition}; and {contains_opt}"
        else:
            condition = contains_opt
        line.extend(["-n", f"'{condition}'"])
        line.extend(["-s", "h", "-l", "help", "-f"])
        lines.append(" ".join(line))

    # Version flag
    if has_version:
        line = ["complete", "-c", base_cmd]
        contains_opt = "not __fish_contains_opt -s v version"
        if subcommand_condition is not None:
            condition = f"{subcommand_condition}; and {contains_opt}"
        else:
            condition = contains_opt
        line.extend(["-n", f"'{condition}'"])
        line.extend(["-s", "v", "-l", "version", "-f"])
        lines.append(" ".join(line))

    # Positional arguments
    for i, param in enumerate(arguments.positional):
        completions, allow_files = _fish_completions_arg(param.annotation)
        completion = " ".join(completions)
        if completion != "":
            condition = f"__fish_is_nth_token {i + 1 + num_tokens}"
            if subcommand_condition is not None:
                condition = f"{subcommand_condition}; and {condition}"
            line = ["complete", "-c", base_cmd, "-n", f"'{condition}'"]
            if not allow_files:
                line.append("-f")
            line.extend(["-a", f"'{completion}'"])
            # if help is not None:
            # line.extend(["-d", _description(param.name, help)])
            lines.append(" ".join(line))

    # Flags
    for flag in arguments.flags:
        long_name = flag.name.replace("_", "-")
        line = ["complete", "-c", base_cmd]
        has_short = arguments.short_to_long.get(flag.name[0], None) == flag.name
        if has_short:
            contains_opt = f"not __fish_contains_opt -s {flag.name[0]} {long_name}"
        else:
            contains_opt = f"not __fish_contains_opt {long_name}"
        if subcommand_condition is not None:
            condition = f"{subcommand_condition}; and {contains_opt}"
        else:
            condition = contains_opt
        line.extend(["-n", f"'{condition}'"])
        if has_short:
            line.extend(["-s", flag.name[0]])
        line.extend(["-l", long_name, "-f"])
        # if help is not None:
        # line.extend(["-d", _description(flag.name, help)])
        lines.append(" ".join(line))

    # Options
    for opt_name, param in arguments.options.items():
        long_name = opt_name.replace("_", "-")
        line = ["complete", "-c", base_cmd]
        has_short = arguments.short_to_long.get(opt_name[0], None) == opt_name
        if has_short:
            contains_opt = f"not __fish_contains_opt -s {opt_name[0]} {long_name}"
        else:
            contains_opt = f"not __fish_contains_opt {long_name}"
        if subcommand_condition is not None:
            condition = f"{subcommand_condition}; and {contains_opt}"
        else:
            condition = contains_opt
        line.extend(["-n", f"'{condition}'"])
        if has_short:
            line.extend(["-s", opt_name[0]])
        line.extend(["-l", long_name])
        completions, allow_files = _fish_completions_arg(param.annotation)
        if not allow_files:
            line.append("-f")
        line.append("-r")
        if len(completions) > 0:
            completion = " ".join(completions)
            line.extend(["-a", f"'{completion}'"])
        # if help is not None:
        # line.extend(["-d", _description(opt_name, help)])
        lines.append(" ".join(line))

    return lines


def completions(
    shell: str,
    cmd_name: str,
    arguments: Arguments,
    help: None | Help,
    has_version: bool,
) -> list[str]:
    if help is not None:
        help.validate(arguments)
    if shell == "fish":
        return _fish_completions(cmd_name, arguments, help, has_version)
    else:
        raise UsageError(f"Unsupported shell for completions '{shell}'")
