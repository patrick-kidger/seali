import contextlib
import pathlib
import types
from typing import Annotated, Any, get_args, get_origin, Literal, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from typing import Annotated as Dir, TypeAlias, TypeVar

    T = TypeVar("T")
    NoComplete: TypeAlias = Annotated[T, "no-complete"]  # noqa: UP040
else:

    class Dir:
        def __class_getitem__(cls, item):
            if item in {str, pathlib.Path}:
                wrappedcls = item
                directory = None
            elif isinstance(item, tuple) and len(item) == 2:
                wrappedcls, directory = item
            else:
                raise TypeError(
                    "`Dir[cls, ...]` must either be called with a single argument, as "
                    "in `Dir[str]` or `Dir[pathlib.Path]` (to indicate that "
                    "completions should be offered from any directory), or be called "
                    "with two arguments, as in `Dir[str, 'somedir']`, giving both the "
                    "wrapped str/Path type and the directory to get completions from."
                )
            if wrappedcls not in {str, pathlib.Path}:
                raise TypeError(
                    "`Dir[cls, ...]` must wrap either `str` or `pathlib.Path`, "
                    f"indicating how to deserialize the argument. Got '{wrappedcls}'."
                )
            return type(
                f"Dir[{wrappedcls}, {directory}]",
                (Dir,),
                dict(wrappedcls=wrappedcls, directory=directory),
            )

    class NoComplete:
        def __class_getitem__(cls, wrappedcls):
            return type(
                f"NoComplete[{wrappedcls}]", (NoComplete,), dict(wrappedcls=wrappedcls)
            )


class DecodeError(Exception):
    def __init__(self, name: str, msg: str):
        self.name = name
        self.msg = msg
        super().__init__(f"Argument '{name}': {msg}")


def decode(argument: str, name: str, annotation: Any):
    origin = get_origin(annotation)
    if annotation in {None, types.NoneType}:
        if argument.lower() in {"null", "none"}:
            return None
        else:
            raise DecodeError(name, f"cannot parse '{argument}' as null.")
    elif annotation is str:
        return argument
    elif annotation is bool:
        match argument.lower():
            case "true":
                return True
            case "false":
                return False
            case _:
                raise DecodeError(name, f"cannot parse '{argument}' as boolean.")
    elif annotation in {int, float}:
        try:
            return annotation(argument)
        except ValueError as e:
            raise DecodeError(
                name, f"cannot parse '{argument}' as {annotation.__name__}."
            ) from e
    elif annotation is pathlib.Path:
        return pathlib.Path(argument)
    elif origin in {types.UnionType, Union}:
        args = get_args(annotation)
        for i, arg in enumerate(args):
            while isinstance(arg, type) and issubclass(arg, (Dir, NoComplete)):  # pyright: ignore[reportArgumentType]
                arg = arg.wrappedcls  # pyright: ignore[reportAttributeAccessIssue]
            if arg is str and i < len(args) - 1:
                raise TypeError(
                    f"Argument '{name}': `str` must be the last member of a union, "
                    f"as any input can be decoded into `str`, so later members would "
                    f"be unreachable."
                )
        if len(args) == 0:
            raise TypeError(f"Argument '{name}': empty unions are not supported.")
        elif len(args) == 1:
            return decode(argument, name, args[0])
        else:
            errors = [f"cannot parse '{argument}' as union:"]
            for arg in args:
                try:
                    return decode(argument, name, arg)
                except DecodeError as e:
                    errors.append("- " + e.msg)
            else:
                raise DecodeError(name, "\n".join(errors))
    elif origin is Literal:
        args = get_args(annotation)
        if len(args) == 0:
            raise TypeError(f"Argument '{name}': empty literals are not supported.")
        elif len(args) == 1:
            value = args[0]
            out = decode(argument, name, type(value))
            if out == value:
                return out
            else:
                raise DecodeError(
                    name, f"unrecognized value '{argument}' is not equal to '{value}'."
                )
        else:
            for value in args:
                with contextlib.suppress(DecodeError):
                    out = decode(argument, name, type(value))
                    if out == value:
                        return out
            else:
                args_str = str(list(map(str, args)))[1:-1]
                raise DecodeError(
                    name, f"unrecognized value '{argument}' is not in {args_str}."
                )
    elif isinstance(annotation, type) and issubclass(annotation, (Dir, NoComplete)):  # pyright: ignore[reportArgumentType]
        return decode(argument, name, annotation.wrappedcls)  # pyright: ignore[reportAttributeAccessIssue]
    else:
        raise TypeError(f"Argument '{name}': unsupported type {annotation}")
