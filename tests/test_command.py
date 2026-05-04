import pathlib
from typing import Literal

import pytest
import seali


def test_positional_arg():
    @seali.command
    def foo(x: int, /):
        return x

    assert foo(["3"]) == 3
    with pytest.raises(SystemExit, match="cannot parse 'foo' as int"):
        assert foo(["foo"]) == 3


def test_named_arg():
    @seali.command
    def foo(*, x: int):
        return x

    assert foo(["-x", "3"]) == 3
    with pytest.raises(SystemExit, match="Unexpected positional argument '3'"):
        assert foo(["3"]) == 3
    with pytest.raises(SystemExit, match="Unexpected positional argument 'foo'"):
        assert foo(["foo"]) == 3


def test_multiple_positional_args():
    @seali.command
    def foo(x: int, y: str, z: float, /):
        return (x, y, z)

    assert foo(["42", "hello", "3.14"]) == (42, "hello", 3.14)


def test_missing_positional_arg():
    @seali.command
    def foo(x: int, y: str, /):
        return (x, y)

    with pytest.raises(SystemExit, match="Missing positional argument 'y'"):
        foo(["5"])


def test_short_flag():
    @seali.command
    def foo(*, xyz: int):
        return xyz

    assert foo(["-x", "10"]) == 10


def test_long_flag():
    @seali.command
    def foo(*, my_option: int):
        return my_option

    assert foo(["--my_option", "20"]) == 20


def test_keyword_equals_syntax():
    @seali.command
    def foo(*, value: int):
        return value

    assert foo(["--value=99"]) == 99
    assert foo(["-v=99"]) == 99


def test_keyword_space_syntax():
    @seali.command
    def foo(*, value: int):
        return value

    assert foo(["--value", "88"]) == 88
    assert foo(["-v", "88"]) == 88


def test_boolean_flag():
    @seali.command
    def foo(*, my_flag: bool = False):
        return my_flag

    assert foo([]) is False
    assert foo(["--my_flag"]) is True
    assert foo(["-m"]) is True


def test_keyword_with_default():
    @seali.command
    def foo(*, option: str = "default_value"):
        return option

    assert foo([]) == "default_value"
    assert foo(["--option", "custom"]) == "custom"


def test_keyword_without_default():
    @seali.command
    def foo(*, required: int):
        return required

    with pytest.raises(SystemExit, match="Missing option 'required'"):
        foo([])

    assert foo(["--required", "7"]) == 7


def test_missing_keyword_value():
    @seali.command
    def foo(*, value: int):
        return value

    with pytest.raises(
        SystemExit, match="Option 'value' was passed without any value."
    ):
        foo(["--value"])


def test_mixed_positional_and_keyword():
    @seali.command
    def foo(x: int, y: str, /, *, option: int, flag: bool = False):
        return (x, y, option, flag)

    assert foo(["1", "test", "--option", "5"]) == (1, "test", 5, False)
    assert foo(["1", "test", "--option", "5", "--flag"]) == (1, "test", 5, True)
    assert foo(["1", "test", "-o", "5", "-f"]) == (1, "test", 5, True)


def test_multiple_keywords():
    @seali.command
    def foo(*, alpha: int, bravo: str, charlie: float):
        return (alpha, bravo, charlie)

    assert foo(["-a", "1", "-b", "hi", "-c", "2.5"]) == (1, "hi", 2.5)
    assert foo(["--alpha", "1", "--bravo", "hi", "--charlie", "2.5"]) == (
        1,
        "hi",
        2.5,
    )
    # Mixed order
    assert foo(["-c", "2.5", "-a", "1", "-b", "hi"]) == (1, "hi", 2.5)


def test_unrecognized_keyword():
    @seali.command
    def foo(*, valid: int):
        return valid

    with pytest.raises(SystemExit, match="Unrecognized flag or option 'invalid'."):
        foo(["--invalid", "5"])


def test_unrecognized_short_keyword():
    @seali.command
    def foo(*, valid: int):
        return valid

    with pytest.raises(
        SystemExit, match="Unrecognized single-letter abbreviation '-x'."
    ):
        foo(["-x", "5"])


def test_invalid_argument_format():
    @seali.command
    def foo(*, value: int):
        return value

    with pytest.raises(
        SystemExit, match="Unexpected positional argument 'nohyphens=5'"
    ):
        foo(["nohyphens=5"])


def test_literal_type():
    @seali.command
    def foo(*, choice: Literal["a", "b", "c"]):
        return choice

    assert foo(["--choice", "a"]) == "a"
    with pytest.raises(
        SystemExit, match="unrecognized value 'd' is not in 'a', 'b', 'c'"
    ):
        foo(["--choice", "d"])


def test_none_type():
    @seali.command
    def foo(*, value: int | None):
        return value

    assert foo(["--value", "5"]) == 5
    assert foo(["--value", "null"]) is None


def test_all_keywords_with_defaults():
    @seali.command
    def foo(*, x: int = 1, y: int = 2, z: int = 3):
        return (x, y, z)

    assert foo([]) == (1, 2, 3)
    assert foo(["-x", "10"]) == (10, 2, 3)
    assert foo(["-x", "10", "-y", "20"]) == (10, 20, 3)
    assert foo(["-x", "10", "-y", "20", "-z", "30"]) == (10, 20, 30)


def test_mixed_flags_and_options():
    @seali.command
    def foo(*, verbose: bool = False, debug: bool = False, count: int, name: str):
        return (verbose, debug, count, name)

    result = foo(["-v", "-d", "-c", "5", "-n", "test"])
    assert result == (True, True, 5, "test")

    result = foo(["-c", "5", "-n", "test"])
    assert result == (False, False, 5, "test")


def test_bool_must_have_false_default():
    with pytest.raises(ValueError, match="all flags .* must have default `False`"):

        @seali.command
        def foo(*, flag: bool = True):
            return flag

        foo([])


def test_bool_with_no_default_raises():
    with pytest.raises(ValueError, match="all flags .* must have default `False`"):

        @seali.command
        def foo(*, flag: bool):
            return flag

        foo([])


def test_argument_name_validation_uppercase():
    with pytest.raises(
        ValueError, match="must use only lowercase letters or underscores"
    ):

        @seali.command
        def foo(*, MyArg: int):
            return MyArg

        foo([])


def test_argument_name_validation_invalid_char():
    with pytest.raises(
        ValueError, match="must use only lowercase letters or underscores"
    ):

        @seali.command
        def foo(*, my_arg_with_number1: int):
            return my_arg_with_number1

        foo(["-m", "5"])


def test_argument_name_validation_starts_with_letter():
    with pytest.raises(ValueError, match="must start with a lowercase letter"):

        @seali.command
        def foo(*, _arg: int):
            return _arg

        foo([])


def test_argument_must_be_annotated():
    with pytest.raises(ValueError, match="must be type-annotated"):

        @seali.command
        def foo(*, arg):
            return arg

        foo([])


def test_regular_argument_not_allowed():
    with pytest.raises(
        ValueError, match="all arguments must be positional-only .* keyword-only"
    ):

        @seali.command
        def foo(arg: int):
            return arg

        foo([])


def test_string_values():
    @seali.command
    def foo(*, name: str):
        return name

    assert foo(["--name", "hello world"]) == "hello world"
    assert foo(["-n", "test"]) == "test"


def test_float_values():
    @seali.command
    def foo(x: float, /):
        return x

    assert foo(["3.14159"]) == 3.14159
    assert foo(["1e-5"]) == 1e-5


def test_negative_int_as_positional():
    @seali.command
    def foo(x: int, /):
        return x

    assert foo(["-5"]) == -5
    assert foo(["-42"]) == -42


def test_negative_int_as_keyword():
    @seali.command
    def foo(*, value: int):
        return value

    assert foo(["--value", "-42"]) == -42
    assert foo(["--value=-42"]) == -42


def test_negative_float_as_positional():
    @seali.command
    def foo(x: float, /):
        return x

    assert foo(["-3"]) == -3.0
    assert foo(["-3.14"]) == -3.14
    assert foo(["-1e-5"]) == -1e-5
    assert foo(["-1.5e10"]) == -1.5e10


def test_multiple_positional_with_negatives():
    @seali.command
    def foo(x: int, y: int, /):
        return (x, y)

    assert foo(["-10", "20"]) == (-10, 20)
    assert foo(["10", "-20"]) == (10, -20)
    assert foo(["-10", "-20"]) == (-10, -20)


def test_negative_positional_with_keyword():
    @seali.command
    def foo(x: int, /, *, option: int):
        return (x, option)

    assert foo(["-5", "--option", "10"]) == (-5, 10)
    assert foo(["-5", "--option", "-10"]) == (-5, -10)
    assert foo(["-5", "-o", "-10"]) == (-5, -10)


def test_override_default_multiple_times():
    @seali.command
    def foo(*, value: int = 10):
        return value

    with pytest.raises(SystemExit, match="Option 'value' passed multiple times."):
        assert foo(["--value", "1", "--value", "2"]) == 2


def test_equals_in_value():
    @seali.command
    def foo(*, equation: str):
        return equation

    assert foo(["--equation", "x=y"]) == "x=y"
    assert foo(["--equation=x=y"]) == "x=y"


def test_combining_short_and_long():
    @seali.command
    def foo(*, alpha: int, bravo: int):
        return (alpha, bravo)

    assert foo(["-a", "1", "--bravo", "2"]) == (1, 2)
    assert foo(["--alpha", "1", "-b", "2"]) == (1, 2)


def test_positional_with_dash():
    @seali.command
    def foo(x: str, y: str, /, *, z: bool = False):
        return x, y, z

    with pytest.raises(SystemExit, match="Missing positional argument 'y'."):
        foo(["hi", "-z"])
    assert foo(["hi", "--", "-z"]) == ("hi", "-z", False)
    assert foo(["hi", "-z", "--", "-z"]) == ("hi", "-z", True)


def test_positional_with_dash2():
    @seali.command
    def foo(x: int, y: int, /, *, z: int):
        return (x, y, z)

    assert foo(["1", "2", "--z", "3"]) == (1, 2, 3)
    assert foo(["1", "-z", "3", "2"]) == (1, 2, 3)
    with pytest.raises(SystemExit, match="Missing positional argument 'y'."):
        foo(["1", "-z", "3"])


def test_keyword_only_single_letter_name():
    @seali.command
    def foo(*, x: int, y: int, z: int):
        return (x, y, z)

    assert foo(["-x", "1", "-y", "2", "-z", "3"]) == (1, 2, 3)
    assert foo(["--x", "1", "--y", "2", "--z", "3"]) == (1, 2, 3)


def test_positional_only_single_letter_name():
    @seali.command
    def foo(x: int, y: int, /):
        return (x, y)

    assert foo(["1", "2"]) == (1, 2)


def test_empty_string_value():
    @seali.command
    def foo(*, text: str):
        return text

    assert foo(["--text", ""]) == ""


def test_boolean_in_equals_form_is_invalid():
    # Boolean flags should not accept values, even with = syntax
    @seali.command
    def foo(*, flag: bool = False):
        return flag

    # This will actually parse as a flag trying to set the value
    # Let's check the actual behavior
    with pytest.raises(
        SystemExit,
        match="s should not be called with `--foo=bar` syntax, but got `--flag=true`.",
    ):
        foo(["--flag=true"])


def test_only_flags():
    @seali.command
    def foo(*, alpha: bool = False, bravo: bool = False):
        return (alpha, bravo)

    assert foo([]) == (False, False)
    assert foo(["--alpha"]) == (True, False)
    assert foo(["--bravo"]) == (False, True)
    assert foo(["--alpha", "--bravo"]) == (True, True)


def test_long_argument_name():
    @seali.command
    def foo(*, very_long_argument_name_with_many_underscores: int):
        return very_long_argument_name_with_many_underscores

    assert foo(["-v", "42"]) == 42
    assert foo(["--very_long_argument_name_with_many_underscores", "42"]) == 42


def test_scientific_notation():
    @seali.command
    def foo(*, value: float):
        return value

    assert foo(["--value", "1e10"]) == 1e10
    assert foo(["--value", "1.5e-3"]) == 1.5e-3
    assert foo(["--value", "-1.5e-3"]) == -1.5e-3


def test_kebab_and_snake_case():
    @seali.command
    def foo(*, my_arg: int, a_flag: bool = False):
        return my_arg, a_flag

    assert foo(["--my-arg", "3"]) == (3, False)
    assert foo(["--my_arg", "3"]) == (3, False)
    assert foo(["--my_arg", "3", "--a_flag"]) == (3, True)
    assert foo(["--my_arg", "3", "--a-flag"]) == (3, True)


def test_path_positional():
    @seali.command
    def foo(path: pathlib.Path, /):
        return path

    assert foo(["/foo/bar"]) == pathlib.Path("/foo/bar")
    assert foo(["relative/path"]) == pathlib.Path("relative/path")
    assert foo(["."]) == pathlib.Path(".")


def test_path_keyword():
    @seali.command
    def foo(*, path: pathlib.Path):
        return path

    assert foo(["--path", "/foo/bar"]) == pathlib.Path("/foo/bar")
    assert foo(["-p", "relative/path"]) == pathlib.Path("relative/path")


def test_path_with_default():
    @seali.command
    def foo(*, path: pathlib.Path = pathlib.Path("default.txt")):
        return path

    assert foo([]) == pathlib.Path("default.txt")
    assert foo(["--path", "custom.txt"]) == pathlib.Path("custom.txt")


def test_multiple_paths():
    @seali.command
    def foo(input_path: pathlib.Path, /, *, output_path: pathlib.Path):
        return (input_path, output_path)

    assert foo(["input.txt", "--output_path", "output.txt"]) == (
        pathlib.Path("input.txt"),
        pathlib.Path("output.txt"),
    )


def test_path_with_union():
    @seali.command
    def foo(*, path: pathlib.Path | None = None):
        return path

    assert foo([]) is None
    assert foo(["--path", "/foo/bar"]) == pathlib.Path("/foo/bar")


def test_positional_with_default():
    @seali.command
    def foo(x: str = "hi", /):
        return x

    assert foo([]) == "hi"
    assert foo(["bye"]) == "bye"
    with pytest.raises(SystemExit, match="Unexpected positional argument 'foo'"):
        foo(["bye", "foo"])


def test_positional_with_default_multi():
    @seali.command
    def foo(x: str = "a", y: str = "b", z: str = "c", /):
        return x, y, z

    assert foo([]) == ("a", "b", "c")
    assert foo(["1"]) == ("1", "b", "c")
    assert foo(["1", "2"]) == ("1", "2", "c")
    assert foo(["1", "2", "3"]) == ("1", "2", "3")
    with pytest.raises(SystemExit, match="Unexpected positional argument '4'"):
        foo(["1", "2", "3", "4"])


def test_positional_with_default_and_keywords():
    @seali.command
    def foo(x: str = "a", /, *, foo: int = 3, bar: str):
        return x, foo, bar

    with pytest.raises(SystemExit, match="Missing option 'bar'"):
        foo([])
    assert foo(["--bar", "hi"]) == ("a", 3, "hi")
    assert foo(["--bar=hi"]) == ("a", 3, "hi")
    assert foo(["fizz", "--bar=hi"]) == ("fizz", 3, "hi")
    assert foo(["fizz", "--bar", "hi"]) == ("fizz", 3, "hi")
    assert foo(["--bar=hi", "fizz"]) == ("fizz", 3, "hi")
    assert foo(["--bar", "hi", "fizz"]) == ("fizz", 3, "hi")
    assert foo(["--bar", "hi", "--", "--bar"]) == ("--bar", 3, "hi")
    with pytest.raises(SystemExit, match="Option 'bar' passed multiple times."):
        foo(["--bar", "hi", "--bar"])


def test_variadic_str():
    @seali.command
    def foo(*args: str):
        return args

    assert foo([]) == ()
    assert foo(["hello"]) == ("hello",)
    assert foo(["hello", "there"]) == ("hello", "there")


def test_variadic_int():
    @seali.command
    def foo(*args: int):
        return args

    assert foo([]) == ()
    assert foo(["3"]) == (3,)
    assert foo(["3", "4"]) == (3, 4)
    assert foo(["--", "3", "4"]) == (3, 4)
    assert foo(["3", "--", "4"]) == (3, 4)
    assert foo(["3", "4", "--"]) == (3, 4)


def test_variadic_with_positional():
    @seali.command
    def foo(bar: str, baz: str, /, *args: str):
        return bar, baz, args

    with pytest.raises(SystemExit, match="Missing positional argument 'bar'"):
        foo([])
    with pytest.raises(SystemExit, match="Missing positional argument 'baz'"):
        foo(["hello"])
    assert foo(["hello", "there"]) == ("hello", "there", ())
    assert foo(["hello", "there", "bob"]) == ("hello", "there", ("bob",))


def test_variadic_with_keyword():
    @seali.command
    def foo(
        bar: str,
        baz: str,
        /,
        *args: str,
        flag: bool = False,
        opt: int,
        another_opt: int = 5,
    ):
        return bar, baz, args, flag, opt, another_opt

    with pytest.raises(SystemExit, match="Missing positional argument 'bar'"):
        foo([])
    with pytest.raises(SystemExit, match="Missing positional argument 'baz'"):
        foo(["hi"])
    with pytest.raises(SystemExit, match="Missing option 'opt'"):
        foo(["hi", "x"])
    with pytest.raises(SystemExit, match="Missing option 'opt'"):
        foo(["hi", "x", "bob"])
    assert foo(["hi", "x", "--opt=3"]) == ("hi", "x", (), False, 3, 5)
    assert foo(["hi", "x", "bob", "--opt=3"]) == ("hi", "x", ("bob",), False, 3, 5)
    assert foo(["hi", "x", "bob", "-o=3", "-f"]) == ("hi", "x", ("bob",), True, 3, 5)
    expected = ("hi", "x", ("bob",), False, 3, 10)
    assert foo(["hi", "x", "bob", "-o", "3", "-a=10"]) == expected
    expected = ("hi", "x", ("bob",), False, 3, 10)
    assert foo(["hi", "x", "bob", "-o=3", "-a", "10"]) == expected

    with pytest.raises(SystemExit, match="Missing option 'opt'"):
        foo(["hi", "x", "bob", "--", "--opt=3"])
    expected = ("hi", "x", ("bob", "--opt=10"), False, 3, 5)
    assert foo(["hi", "x", "bob", "--opt=3", "--", "--opt=10"]) == expected
    expected = ("hi", "x", ("bob", "--opt=10"), True, 3, 5)
    assert foo(["hi", "x", "bob", "--opt=3", "--flag", "--", "--opt=10"]) == expected
    expected = ("hi", "x", ("bob", "--opt=10", "--flag"), False, 3, 5)
    assert foo(["hi", "x", "bob", "--opt=3", "--", "--opt=10", "--flag"]) == expected


def test_variadic_with_default_positional():
    @seali.command
    def foo(x: str = "hi", /, *args: str):
        return x, args

    assert foo([]) == ("hi", ())
    assert foo(["foo"]) == ("foo", ())
    assert foo(["foo", "bar"]) == ("foo", ("bar",))
    assert foo(["foo", "bar", "baz"]) == ("foo", ("bar", "baz"))
    assert foo(["foo", "--", "bar", "baz"]) == ("foo", ("bar", "baz"))


def test_variadic_with_default_positional_and_keyword():
    @seali.command
    def foo(x: str = "hi", /, *args: str, opt: int = 3):
        return x, args, opt

    assert foo([]) == ("hi", (), 3)
    assert foo(["foo"]) == ("foo", (), 3)
    assert foo(["foo", "bar"]) == ("foo", ("bar",), 3)
    assert foo(["foo", "bar", "baz"]) == ("foo", ("bar", "baz"), 3)
    assert foo(["foo", "--", "bar", "baz"]) == ("foo", ("bar", "baz"), 3)
    assert foo(["--opt=5"]) == ("hi", (), 5)
    assert foo(["--opt", "5"]) == ("hi", (), 5)
    assert foo(["foo", "--opt", "5"]) == ("foo", (), 5)
    assert foo(["foo", "bar", "--opt", "5"]) == ("foo", ("bar",), 5)
    assert foo(["--", "--opt", "5"]) == ("--opt", ("5",), 3)
    assert foo(["--", "--opt=5"]) == ("--opt=5", (), 3)


def test_variadic_with_unrecognized_keywords():
    @seali.command
    def foo(*foo: str):
        return foo

    assert foo(["--bar"]) == ("--bar",)
    assert foo(["--bar=4"]) == ("--bar=4",)
    assert foo(["--bar", "4"]) == ("--bar", "4")

    @seali.command
    def foo2(*foo: str, baz: int = 3):
        return foo, baz

    assert foo2(["--bar"]) == (("--bar",), 3)
    assert foo2(["--bar=4"]) == (("--bar=4",), 3)
    assert foo2(["--bar", "4"]) == (("--bar", "4"), 3)

    assert foo2(["--bar", "--baz=5"]) == (("--bar",), 5)
    assert foo2(["--bar=4", "--baz=5"]) == (("--bar=4",), 5)
    assert foo2(["--bar", "4", "--baz=5"]) == (("--bar", "4"), 5)

    assert foo2(["--bar", "--baz", "5"]) == (("--bar",), 5)
    assert foo2(["--bar=4", "--baz", "5"]) == (("--bar=4",), 5)
    assert foo2(["--bar", "4", "--baz", "5"]) == (("--bar", "4"), 5)


def test_flag_and_option_with_same_start_letter():
    @seali.command
    def foo(*, myflag: bool = False, myopt: int = 3):
        return myflag, myopt

    assert foo([]) == (False, 3)
    assert foo(["-m"]) == (True, 3)
    with pytest.raises(SystemExit, match="Unexpected positional argument '5'."):
        foo(["-m", "5"])


def test_two_options_with_same_start_letter():
    @seali.command
    def foo(*, myopt: int = 3, my_another_opt: str = "hi"):
        return myopt, my_another_opt

    assert foo([]) == (3, "hi")
    with pytest.raises(
        SystemExit, match="Option 'myopt' was passed without any value."
    ):
        assert foo(["-m"]) == (True, 3)
    assert foo(["-m", "5"]) == (5, "hi")


def test_completions_argument_name():
    @seali.command
    def foo(*, completions: str):
        pass

    with pytest.raises(ValueError) as exc_info:
        foo()
    assert "Argument name 'completions' is reserved" in str(exc_info)


def test_version_short_flag(capfd):
    @seali.command(version="1.0.0")
    def foo():
        return "executed"

    with pytest.raises(SystemExit) as exc_info:
        foo(["-v"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "1.0.0\n"


def test_version_long_flag(capfd):
    @seali.command(version="2.5.3")
    def foo():
        return "executed"

    with pytest.raises(SystemExit) as exc_info:
        foo(["--version"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "2.5.3\n"


def test_version_with_positional_args(capfd):
    @seali.command(version="1.2.3")
    def foo(x: int, /):
        return x

    # Version flag should take precedence
    with pytest.raises(SystemExit) as exc_info:
        foo(["-v"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "1.2.3\n"

    # Normal execution should still work
    assert foo(["42"]) == 42


def test_version_with_keyword_args(capfd):
    @seali.command(version="3.0.0")
    def foo(*, bar: int = 5):
        return bar

    # Version flag should take precedence
    with pytest.raises(SystemExit) as exc_info:
        foo(["--version"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "3.0.0\n"

    # Normal execution should still work
    assert foo([]) == 5
    assert foo(["--bar", "10"]) == 10


def test_version_with_positional_arg_named_v(capfd):
    # When a positional-only parameter is named something starting with 'v',
    # the version flag should still work
    @seali.command(version="1.0.0")
    def foo(value: int, /):
        return value

    with pytest.raises(SystemExit) as exc_info:
        foo(["-v"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "1.0.0\n"
    assert foo(["3"]) == 3


def test_version_keyword_arg_named_version_error():
    # Having a keyword argument named "version" should raise an error
    # when version is also provided to the command
    with pytest.raises(ValueError, match="Argument name 'version' is reserved"):

        @seali.command(version="1.0.0")
        def foo(*, version: str):
            return version

        foo([])


def test_version_keyword_arg_named_v_conflict(capfd):
    # Having a keyword argument starting with 'v' when version is provided
    # means -v will show version, not set the verbose flag
    @seali.command(version="1.0.0")
    def foo(*, verbose: bool = False):
        return verbose

    # The -v flag shows version (takes precedence)
    with pytest.raises(SystemExit) as exc_info:
        foo(["-v"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "1.0.0\n"

    # But --verbose should still work
    assert foo(["--verbose"]) is True
    assert foo([]) is False


def test_version_with_variadic_args(capfd):
    @seali.command(version="4.5.6")
    def foo(*args: str):
        return args

    # Version flag should take precedence
    with pytest.raises(SystemExit) as exc_info:
        foo(["--version"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "4.5.6\n"

    # Normal execution should still work
    assert foo(["a", "b", "c"]) == ("a", "b", "c")


def test_version_not_activated_by_partial_match():
    @seali.command(version="1.0.0")
    def foo(*args: str):
        return args

    # Only exact `-v` or `--version` should trigger version output
    # Other arguments starting with v should not
    assert foo(["--verbose"]) == ("--verbose",)
    assert foo(["-verbose"]) == ("-verbose",)


def test_version_string_with_metadata(capfd):
    @seali.command(version="1.0.0-beta.1+build.123")
    def foo():
        return "executed"

    with pytest.raises(SystemExit) as exc_info:
        foo(["--version"])
    assert exc_info.value.code == 0
    captured = capfd.readouterr().out
    assert captured == "1.0.0-beta.1+build.123\n"
