import pathlib
import sys
from typing import Literal, Union

import pytest
from tinycli import Dir, NoComplete
from tinycli._decode import decode, DecodeError


def test_decode_none():
    assert decode("null", "eek", None) is None
    assert decode("none", "eek", None) is None
    assert decode("NULL", "eek", None) is None
    assert decode("NoNe", "eek", None) is None
    with pytest.raises(DecodeError, match="cannot parse 'foo' as null"):
        decode("foo", "", None)


def test_decode_str():
    assert decode("hello", "eek", str) == "hello"
    assert decode("", "eek", str) == ""
    assert decode("hello world", "eek", str) == "hello world"
    assert decode("foo=bar", "eek", str) == "foo=bar"
    assert decode("HeLLo", "eek", str) == "HeLLo"
    assert decode("  hello  ", "eek", str) == "  hello  "


def test_decode_bool():
    assert decode("true", "eek", bool) is True
    assert decode("TRUE", "eek", bool) is True
    assert decode("TrUe", "eek", bool) is True

    assert decode("false", "eek", bool) is False
    assert decode("FALSE", "eek", bool) is False
    with pytest.raises(DecodeError, match="cannot parse 'yes' as boolean"):
        decode("yes", "eek", bool)
    with pytest.raises(DecodeError, match="cannot parse '' as boolean"):
        decode("", "eek", bool)


def test_decode_int():
    assert decode("42", "eek", int) == 42
    assert decode("-42", "eek", int) == -42
    assert decode("0", "eek", int) == 0
    assert decode("123456789", "eek", int) == 123456789
    assert decode("007", "eek", int) == 7
    with pytest.raises(DecodeError, match="cannot parse '3.14' as int"):
        decode("3.14", "eek", int)
    with pytest.raises(DecodeError, match="cannot parse 'foo' as int"):
        decode("foo", "eek", int)
    with pytest.raises(DecodeError, match="cannot parse '' as int"):
        decode("", "eek", int)


def test_decode_float():
    assert decode("3.14", "eek", float) == 3.14
    assert decode("-3.14", "eek", float) == -3.14
    assert decode("0.0", "eek", float) == 0.0
    assert decode("1e10", "eek", float) == 1e10
    assert decode("-1.5e-3", "eek", float) == -1.5e-3
    assert decode("42", "eek", float) == 42.0
    assert decode("inf", "eek", float) == float("inf")
    assert decode("-inf", "eek", float) == float("-inf")
    with pytest.raises(DecodeError, match="cannot parse 'foo' as float"):
        decode("foo", "eek", float)


def test_decode_union_first_type_matches():
    assert decode("42", "eek", int | str) == 42
    assert decode("42", "eek", str | int) == "42"
    assert decode("hello", "eek", int | str) == "hello"
    assert decode("hello", "eek", str | int) == "hello"

    assert decode("42", "eek", None | int) == 42

    assert decode("3.14", "eek", int | float) == 3.14
    assert decode("3.14", "eek", int | float | str) == 3.14


def test_decode_union_no_match():
    with pytest.raises(
        DecodeError,
        match=(
            "cannot parse 'foo' as union.*\n"
            ".*cannot parse 'foo' as int.*\n"
            ".*cannot parse 'foo' as boolean"
        ),
    ):
        decode("foo", "eek", int | bool)


def test_decode_union_of_unions():
    assert decode("3.14", "eek", Union[int, float | str]) == 3.14  # noqa: UP007
    # In Python 3.11, Union[int, str | float] gets flattened to (int, float, str)
    # In Python 3.14, it becomes (int, str, float), preserving nested union order
    if sys.version_info >= (3, 14):
        assert decode("3.14", "eek", Union[int, str | float]) == "3.14"  # noqa: UP007
    else:
        # In Python 3.11-3.13, float comes before str after flattening
        assert decode("3.14", "eek", Union[int, str | float]) == 3.14  # noqa: UP007


def test_decode_literal_string():
    assert decode("a", "eek", Literal["a", "b", "c"]) == "a"
    assert decode("b", "eek", Literal["a", "b", "c"]) == "b"
    with pytest.raises(
        DecodeError, match=r"unrecognized value 'd' is not in 'a', 'b', 'c'"
    ):
        decode("d", "eek", Literal["a", "b", "c"])


def test_decode_literal_int():
    assert decode("1", "eek", Literal[1, 2, 3]) == 1
    assert decode("2", "eek", Literal[1, 2, 3]) == 2
    with pytest.raises(
        DecodeError, match=r"unrecognized value '4' is not in '1', '2', '3'"
    ):
        decode("4", "eek", Literal[1, 2, 3])


def test_decode_literal_bool():
    assert decode("true", "eek", Literal[True, False]) is True
    assert decode("false", "eek", Literal[True, False]) is False


def test_decode_literal_float():
    assert decode("2.5", "eek", Literal[1.0, 2.5, 3.0]) == 2.5


def test_decode_literal_mixed_types():
    assert decode("1", "eek", Literal[1, "a", 2.5]) == 1
    assert decode("a", "eek", Literal[1, "a", 2.5]) == "a"
    assert decode("2.5", "eek", Literal[1, "a", 2.5]) == 2.5


def test_decode_unsupported_type_list():
    with pytest.raises(TypeError, match="unsupported type <class 'list'>"):
        decode("[1, 2, 3]", "eek", list)
    with pytest.raises(TypeError, match="unsupported type <class 'dict'>"):
        decode("{'a': 1}", "eek", dict)
    with pytest.raises(TypeError, match="unsupported type <class 'tuple'>"):
        decode("(1, 2)", "eek", tuple)


def test_decode_literal_empty():
    with pytest.raises(TypeError, match="empty literals are not supported"):
        decode("a", "eek", Literal[()])


def test_decode_union_with_literal():
    assert decode("a", "eek", Literal["a", "b"] | int) == "a"
    assert decode("a", "eek", int | Literal["a", "b"]) == "a"
    assert decode("42", "eek", Literal["a", "b"] | int) == 42
    assert decode("42", "eek", int | Literal["a", "b"]) == 42


def test_decode_path():
    assert decode("/foo/bar", "eek", pathlib.Path) == pathlib.Path("/foo/bar")
    assert decode("relative/path", "eek", pathlib.Path) == pathlib.Path("relative/path")
    assert decode(".", "eek", pathlib.Path) == pathlib.Path(".")
    assert decode("..", "eek", pathlib.Path) == pathlib.Path("..")
    assert decode("~/home", "eek", pathlib.Path) == pathlib.Path("~/home")
    assert decode("", "eek", pathlib.Path) == pathlib.Path("")


def test_decode_path_with_union():
    assert decode("/foo/bar", "eek", pathlib.Path | str) == pathlib.Path("/foo/bar")
    assert decode("/foo/bar", "eek", str | pathlib.Path) == "/foo/bar"
    assert decode("/foo/bar", "eek", pathlib.Path | None) == pathlib.Path("/foo/bar")
    assert decode("null", "eek", None | pathlib.Path) is None


def test_decode_dir_with_str():
    assert decode("/foo/bar", "eek", Dir[str, "."]) == "/foo/bar"
    assert decode("relative/path", "eek", Dir[str, "/tmp"]) == "relative/path"
    assert decode("file.txt", "eek", Dir[str, "~"]) == "file.txt"
    assert decode("", "eek", Dir[str, "."]) == ""


def test_decode_dir_with_path():
    assert decode("/foo/bar", "eek", Dir[pathlib.Path, "."]) == pathlib.Path("/foo/bar")
    assert decode("relative/path", "eek", Dir[pathlib.Path, "/tmp"]) == pathlib.Path(
        "relative/path"
    )
    assert decode(".", "eek", Dir[pathlib.Path, "~"]) == pathlib.Path(".")
    assert decode("file.txt", "eek", Dir[pathlib.Path, "/home"]) == pathlib.Path(
        "file.txt"
    )


def test_decode_nocomplete_with_str():
    assert decode("hello", "eek", NoComplete[str]) == "hello"
    assert decode("world", "eek", NoComplete[str]) == "world"
    assert decode("", "eek", NoComplete[str]) == ""


def test_decode_nocomplete_with_int():
    assert decode("42", "eek", NoComplete[int]) == 42
    assert decode("-10", "eek", NoComplete[int]) == -10
    assert decode("0", "eek", NoComplete[int]) == 0


def test_decode_nocomplete_with_float():
    assert decode("3.14", "eek", NoComplete[float]) == 3.14
    assert decode("-2.5", "eek", NoComplete[float]) == -2.5
    assert decode("1e10", "eek", NoComplete[float]) == 1e10


def test_decode_nocomplete_with_path():
    assert decode("/foo/bar", "eek", NoComplete[pathlib.Path]) == pathlib.Path(
        "/foo/bar"
    )
    assert decode("relative/path", "eek", NoComplete[pathlib.Path]) == pathlib.Path(
        "relative/path"
    )


def test_decode_nocomplete_with_bool():
    assert decode("true", "eek", NoComplete[bool]) is True
    assert decode("false", "eek", NoComplete[bool]) is False


def test_decode_dir_and_nocomplete_with_union():
    assert decode("/foo/bar", "eek", Dir[str, "."] | int) == "/foo/bar"
    assert decode("42", "eek", Dir[str, "."] | int) == "42"
    assert decode("test", "eek", NoComplete[str] | int) == "test"
    assert decode("123", "eek", int | NoComplete[str]) == 123
