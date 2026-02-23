import seali


def test_control():
    assert seali.RESET == "\x1b[0m"
    assert seali.BOLD == "\x1b[1m"
    assert seali.FAINT == "\x1b[2m"
    assert seali.ITALIC == "\x1b[3m"
    assert seali.UNDERLINE == "\x1b[4m"


def test_colour():
    assert f"{seali.BLACK}" == "\x1b[30m"
    assert f"{seali.RED}" == "\x1b[31m"
    assert f"{seali.GREEN}" == "\x1b[32m"
    assert f"{seali.YELLOW}" == "\x1b[33m"
    assert f"{seali.BLUE}" == "\x1b[34m"
    assert f"{seali.MAGENTA}" == "\x1b[35m"
    assert f"{seali.CYAN}" == "\x1b[36m"
    assert f"{seali.WHITE}" == "\x1b[37m"

    assert f"{seali.BLACK.bg}" == "\x1b[40m"
    assert f"{seali.RED.bg}" == "\x1b[41m"
    assert f"{seali.GREEN.bg}" == "\x1b[42m"
    assert f"{seali.YELLOW.bg}" == "\x1b[43m"
    assert f"{seali.BLUE.bg}" == "\x1b[44m"
    assert f"{seali.MAGENTA.bg}" == "\x1b[45m"
    assert f"{seali.CYAN.bg}" == "\x1b[46m"
    assert f"{seali.WHITE.bg}" == "\x1b[47m"

    assert f"{seali.BLACK.bright}" == "\x1b[90m"
    assert f"{seali.RED.bright}" == "\x1b[91m"
    assert f"{seali.GREEN.bright}" == "\x1b[92m"
    assert f"{seali.YELLOW.bright}" == "\x1b[93m"
    assert f"{seali.BLUE.bright}" == "\x1b[94m"
    assert f"{seali.MAGENTA.bright}" == "\x1b[95m"
    assert f"{seali.CYAN.bright}" == "\x1b[96m"
    assert f"{seali.WHITE.bright}" == "\x1b[97m"

    assert f"{seali.BLACK.bright_bg}" == "\x1b[100m"
    assert f"{seali.RED.bright_bg}" == "\x1b[101m"
    assert f"{seali.GREEN.bright_bg}" == "\x1b[102m"
    assert f"{seali.YELLOW.bright_bg}" == "\x1b[103m"
    assert f"{seali.BLUE.bright_bg}" == "\x1b[104m"
    assert f"{seali.MAGENTA.bright_bg}" == "\x1b[105m"
    assert f"{seali.CYAN.bright_bg}" == "\x1b[106m"
    assert f"{seali.WHITE.bright_bg}" == "\x1b[107m"


def test_rgb():
    x = seali.RGB(40, 50, 60)
    assert f"{x}" == "\x1b[38;2;40;50;60m"
    assert f"{x.bg}" == "\x1b[48;2;40;50;60m"
