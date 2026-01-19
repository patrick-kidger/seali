import tinycli


def test_control():
    assert tinycli.RESET == "\x1b[0m"
    assert tinycli.BOLD == "\x1b[1m"
    assert tinycli.FAINT == "\x1b[2m"
    assert tinycli.ITALIC == "\x1b[3m"
    assert tinycli.UNDERLINE == "\x1b[4m"


def test_colour():
    assert f"{tinycli.BLACK}" == "\x1b[30m"
    assert f"{tinycli.RED}" == "\x1b[31m"
    assert f"{tinycli.GREEN}" == "\x1b[32m"
    assert f"{tinycli.YELLOW}" == "\x1b[33m"
    assert f"{tinycli.BLUE}" == "\x1b[34m"
    assert f"{tinycli.MAGENTA}" == "\x1b[35m"
    assert f"{tinycli.CYAN}" == "\x1b[36m"
    assert f"{tinycli.WHITE}" == "\x1b[37m"

    assert f"{tinycli.BLACK.bg}" == "\x1b[40m"
    assert f"{tinycli.RED.bg}" == "\x1b[41m"
    assert f"{tinycli.GREEN.bg}" == "\x1b[42m"
    assert f"{tinycli.YELLOW.bg}" == "\x1b[43m"
    assert f"{tinycli.BLUE.bg}" == "\x1b[44m"
    assert f"{tinycli.MAGENTA.bg}" == "\x1b[45m"
    assert f"{tinycli.CYAN.bg}" == "\x1b[46m"
    assert f"{tinycli.WHITE.bg}" == "\x1b[47m"

    assert f"{tinycli.BLACK.bright}" == "\x1b[90m"
    assert f"{tinycli.RED.bright}" == "\x1b[91m"
    assert f"{tinycli.GREEN.bright}" == "\x1b[92m"
    assert f"{tinycli.YELLOW.bright}" == "\x1b[93m"
    assert f"{tinycli.BLUE.bright}" == "\x1b[94m"
    assert f"{tinycli.MAGENTA.bright}" == "\x1b[95m"
    assert f"{tinycli.CYAN.bright}" == "\x1b[96m"
    assert f"{tinycli.WHITE.bright}" == "\x1b[97m"

    assert f"{tinycli.BLACK.bright_bg}" == "\x1b[100m"
    assert f"{tinycli.RED.bright_bg}" == "\x1b[101m"
    assert f"{tinycli.GREEN.bright_bg}" == "\x1b[102m"
    assert f"{tinycli.YELLOW.bright_bg}" == "\x1b[103m"
    assert f"{tinycli.BLUE.bright_bg}" == "\x1b[104m"
    assert f"{tinycli.MAGENTA.bright_bg}" == "\x1b[105m"
    assert f"{tinycli.CYAN.bright_bg}" == "\x1b[106m"
    assert f"{tinycli.WHITE.bright_bg}" == "\x1b[107m"


def test_rgb():
    x = tinycli.RGB(40, 50, 60)
    assert f"{x}" == "\x1b[38;2;40;50;60m"
    assert f"{x.bg}" == "\x1b[48;2;40;50;60m"
