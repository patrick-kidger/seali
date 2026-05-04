import pytest
import seali


def test_default_not_wrapped_in_command():
    def foo():
        pass

    @seali.command
    def bar():
        pass

    with pytest.raises(TypeError, match="`default` must be either `None` or a command"):
        seali.group(default=foo, subcommands=[bar])  # pyright: ignore[reportArgumentType]


def test_subcommand_not_wrapped_in_command():
    def bar():
        pass

    with pytest.raises(TypeError, match="subcommands must be commands"):
        seali.group(name="foo", subcommands=[bar])  # pyright: ignore[reportArgumentType]


@seali.command
def default_without_args():
    return 0


@seali.command
def default_with_arg(x: str, /):
    return x


@seali.command
def default_with_positional_default(x: str = "hi", /):
    return x


@seali.command
def default_with_varargs(*x: str):
    return x


@seali.command
def default_with_keyword(*, x: int):
    return x


@seali.command
def default_with_keyword_default(*, x: int = 3):
    return x


@pytest.mark.parametrize(
    "default",
    (
        None,
        default_without_args,
        default_with_arg,
        default_with_positional_default,
        default_with_varargs,
        default_with_keyword,
        default_with_keyword_default,
    ),
)
def test_default(default):
    @seali.command
    def foo(x: int = 9, /):
        return x

    cmd = seali.group(
        name="cmd" if default is None else None,
        default=default,
        subcommands=[foo],
    )  # pyright: ignore[reportCallIssue]

    assert cmd(["foo"]) == 9
    with pytest.raises(
        SystemExit, match="unrecognized value 'bar' is not equal to 'foo'\\."
    ):
        cmd(["bar"])

    if default is None:
        with pytest.raises(SystemExit, match="Missing subcommand."):
            cmd([])
    elif default is default_without_args:
        assert cmd([]) == 0
    elif default is default_with_arg:
        with pytest.raises(SystemExit, match="Missing positional argument 'x'."):
            cmd([])
    elif default is default_with_positional_default:
        assert cmd([]) == "hi"
    elif default is default_with_varargs:
        assert cmd([]) == ()
    elif default is default_with_keyword:
        with pytest.raises(SystemExit, match="Missing option 'x'"):
            cmd([])
        assert cmd(["-x", "5"]) == 5
        assert cmd(["-x=5"]) == 5
    elif default is default_with_keyword_default:
        assert cmd([]) == 3
        assert cmd(["-x", "5"]) == 5
        assert cmd(["-x=5"]) == 5
    else:
        assert False


def test_group():
    @seali.command
    def new(commit: str, /):
        return "new", commit

    @seali.command
    def describe(commit: str, /):
        return "describe", commit

    @seali.command
    def add(filename: str, /):
        return "fileadd", filename

    @seali.command
    def exec(*args: str):
        return "utilexec", args

    jj = seali.group(
        name="jj",
        subcommands=[
            new,
            describe,
            seali.group(name="file", subcommands=[add]),
            seali.group(name="util", subcommands=[exec]),
        ],
    )

    with pytest.raises(SystemExit, match="Missing subcommand."):
        jj([])
    with pytest.raises(SystemExit, match="Missing positional argument 'commit'"):
        jj(["new"])
    assert jj(["new", "foo"]) == ("new", "foo")

    with pytest.raises(SystemExit, match="Missing positional argument 'commit'"):
        jj(["describe"])
    assert jj(["describe", "foo"]) == ("describe", "foo")

    with pytest.raises(
        SystemExit,
        match="unrecognized value 'foo' is not in 'new', 'describe', 'file', 'util'\\.",
    ):
        jj(["foo"])

    with pytest.raises(SystemExit, match="Missing subcommand."):
        jj(["file"])
    with pytest.raises(SystemExit, match="Missing positional argument 'filename'"):
        assert jj(["file", "add"])
    assert jj(["file", "add", "foo"]) == ("fileadd", "foo")
    with pytest.raises(
        SystemExit, match="unrecognized value 'foo' is not equal to 'add'\\."
    ):
        jj(["file", "foo"])

    with pytest.raises(SystemExit, match="Missing subcommand."):
        jj(["util"])
    assert jj(["util", "exec"]) == ("utilexec", ())
    assert jj(["util", "exec", "foo"]) == ("utilexec", ("foo",))
    assert jj(["util", "exec", "--", "foo"]) == ("utilexec", ("foo",))


def test_group_with_keywords():
    @seali.command
    def foo(*, x: int = 3):
        return x

    bar = seali.group(name="bar", subcommands=[foo])
    assert bar(["foo"]) == 3
    assert bar(["foo", "--x", "5"]) == 5
    assert bar(["foo", "-x", "5"]) == 5
    assert bar(["foo", "--x=5"]) == 5
    assert bar(["foo", "-x=5"]) == 5

    @seali.command
    def foo2(*, long: int = 3):
        return long

    bar = seali.group(name="bar", subcommands=[foo2])
    assert bar(["foo2"]) == 3
    assert bar(["foo2", "--long", "5"]) == 5
    assert bar(["foo2", "-l", "5"]) == 5
    assert bar(["foo2", "--long=5"]) == 5
    assert bar(["foo2", "-l=5"]) == 5
