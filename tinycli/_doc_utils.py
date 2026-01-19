import inspect
import typing
from collections.abc import Callable
from typing import TypeVar


_T = TypeVar("_T")
_Callable = TypeVar("_Callable", bound=Callable)


def doc_remove_return(fn: _Callable) -> _Callable:
    if getattr(typing, "GENERATING_DOCUMENTATION", "") == "tinycli":
        sig = inspect.signature(fn)
        sig = sig.replace(return_annotation=inspect.Signature.empty)
        object.__setattr__(fn, "__signature__", sig)
    return fn


class _DocAttr:
    pass


def doc_attr(obj: _T, doc: None | str) -> _T:
    if getattr(typing, "GENERATING_DOCUMENTATION", "") == "tinycli":
        obj = _DocAttr()  # pyright: ignore[reportAssignmentType]
        obj.__doc__ = doc
    return obj
