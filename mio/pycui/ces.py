"""
    defines of all terminal control escape sequences
"""

class TerminalControlEscapeSequence(object):
    """

    NOTE:
        check
            https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
            https://en.wikipedia.org/wiki/ANSI_escape_code

        check terminal type by `echo $TERM`, in many case it should be `vt100, xterm, xterm-256color`
        it seem there is many type? does it still exist? (e.g. vt102)

        for xterm, see around here
            https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
    """

    # possible to use `\033` for `\x1b` which is 27 in dex, which represent `^[` (ESC)
    # CSI (Control Sequence Introducer) is `^[[` -> `\x1b[`
    control_codes = {
        "ESC"                   : "\x1b",
        "CSI"                   : "\x1b["
    }

    # not elegant, but more adaptal..., need to check these are all same in terminals
    control_functions = {
        "CARRIAGE_RETURN"       : lambda: "\r",
        "BELL"                  : lambda: "\x07",
        "CLEAR"                 : lambda: "\x1b[2J",

        "SHOW_CURSOR"           : lambda: "\x1b[?25h",
        "HIDE_CURSOR"           : lambda: "\x1b[?25l",
        "CURSOR_UP"             : lambda num: f"\x1b[{num}A",
        "CURSOR_DOWN"           : lambda num: f"\x1b[{num}B",
        "CURSOR_FORWARD"        : lambda num: f"\x1b[{num}C",
        "CURSOR_BACKWARD"       : lambda num: f"\x1b[{num}D",
        "CURSOR_MOVE_TO_COLUMN" : lambda col: f"\x1b[{col+1}G",
        "CURSOR_MOVE_TO"        : lambda x,y: f"\x1b[{y+1};{x+1}H",

        "ERASE_IN_DISPLAY"      : lambda param: f"\x1b[{param}J",
        "ERASE_IN_LINE"         : lambda param: f"\x1b[{param}K",

        # it may both works on each terminal? (tested on macOS' iTerm2 emulation)
        "ENABLE_ALT_SCREEN_XTERM"            : lambda: "\x1b[?47h",
        "DISABLE_ALT_SCREEN_XTERM"           : lambda: "\x1b[2J\x1b[?47l\x1b8",
        "ENABLE_ALT_SCREEN_XTERM_256_COLOR"  : lambda: "\x1b[?1049h",
        "DISABLE_ALT_SCREEN_XTERM_256_COLOR" : lambda: "\x1b[?1049l"
    }

    default_color_name = "DEFAULT"
    style_end_code = "m"

    # using independently is like "\x1b[0m"
    # we can combine some codes like "\x1b[31;1;4mHello, World\x1b[0m"
    style_codes = {
        "END"           : "0",
        "BOLD"          : "1",
        "ITALIC"        : "3",
        "UNDERLINE"     : "4",
        "REVERSE"       : "7",
        "STRIKETHROUGH" : "9"
    }

    fg_rgb2ces_code = lambda r,g,b: f"38;2;{r};{g};{b}"
    bg_rgb2ces_code = lambda r,g,b: f"48;2;{r};{g};{b}"

    fg_256color2ces_code = lambda num: f"38;5;{num}"
    bg_256color2ces_code = lambda num: f"48;5;{num}"

    fg_color_codes = {
        "BLACK"   : "30",
        "RED"     : "31",
        "GREEN"   : "32",
        "YELLOW"  : "33",
        "BLUE"    : "34",
        "PURPLE"  : "35",
        "CYAN"    : "36",
        "WHITE"   : "37",

        "DEFAULT" : "39",

        "BRIGHT_BLACK"   : "90",
        "BRIGHT_RED"     : "91",
        "BRIGHT_GREEN"   : "92",
        "BRIGHT_YELLOW"  : "93",
        "BRIGHT_BLUE"    : "94",
        "BRIGHT_PURPLE"  : "95",
        "BRIGHT_CYAN"    : "96",
        "BRIGHT_WHITE"   : "97",
    }

    bg_color_codes = {
        "BLACK"   : "40",
        "RED"     : "41",
        "GREEN"   : "42",
        "YELLOW"  : "43",
        "BLUE"    : "44",
        "PURPLE"  : "45",
        "CYAN"    : "46",
        "WHITE"   : "47",

        "DEFAULT" : "49",

        "BRIGHT_BLACK"   : "100",
        "BRIGHT_RED"     : "101",
        "BRIGHT_GREEN"   : "102",
        "BRIGHT_YELLOW"  : "103",
        "BRIGHT_BLUE"    : "104",
        "BRIGHT_PURPLE"  : "105",
        "BRIGHT_CYAN"    : "106",
        "BRIGHT_WHITE"   : "107",
    }
