import os

if os.name == 'nt':
    _is_windows = True
else:
    _is_windows = False

def is_in_key_codes(v):
    if 0 <= v <=127:
        return True
    # this may fail when input is a unicode char in this range
    elif 1001 <= v <= 1035:
        return True

    return False

def is_printable(v):
    if 32 <= v < 127:
        return True

    return False

# base key codes
# some keys are not inputtable for some terminals
#
# tested on macOS iTerm2, it might differ on other OSs
# so changing some value might needed
# use following `if statement` for key alteration
key_codes = {
    "UNKNOWN_KEY": -1,

    "CTRL_SPACE": 0,

    "CTRL_A": 1,
    "CTRL_B": 2,
    "CTRL_C": 3,
    "CTRL_D": 4,
    "CTRL_E": 5,
    "CTRL_F": 6,
    "CTRL_G": 7,
    "CTRL_H": 8,
    "CTRL_I": 9,  # same as TAB
    "CTRL_J": 10, # same as ENTER in macOS
    "CTRL_K": 11,
    "CTRL_L": 12,
    "CTRL_M": 13,
    "CTRL_N": 14,
    "CTRL_O": 15,
    "CTRL_P": 16,
    "CTRL_Q": 17,
    "CTRL_R": 18,
    "CTRL_S": 19,
    "CTRL_T": 20,
    "CTRL_U": 21,
    "CTRL_V": 22,
    "CTRL_W": 23,
    "CTRL_X": 24,
    "CTRL_Y": 25,
    "CTRL_Z": 26,

    "TAB"   : 9,  # same as CTRL_I
    "ENTER" : 10, # same as CTRL_J
    "FN"    : 16, # same as CTRL_P

    "ESCAPE": 27,

    "CTRL_BACK_SLASH"    : 28,
    "CTRL_RIGHT_BRACKET" : 29, 
    "A_KEY_FOR_HERE"     : 30, # what kind of key comes here?
    "A_KEY_FOR_HERE2"    : 31, # what kind of key comes here?

    # Printable ASCII characters
    "SPACE"            : 32, #  
    "EXCLAMATION_MARK" : 33, # !
    "DOUBLE_QUOTE"     : 34, # "
    "HASH"             : 35, # #
    "DOLLAR"           : 36, # $
    "PERCENT"          : 37, # %
    "AMPERSAND"        : 38, # &
    "SINGLE_QUITE"     : 39, # '
    "LEFT_PAREN"       : 40, # (
    "RIGHT_PAREN"      : 41, # )
    "ASTERISK"         : 42, # *
    "PLUS"             : 43, # +
    "COMMA"            : 44, # ,
    "MINUS"            : 45, # -
    "PERIOD"           : 46, # .
    "SLASH"            : 47, # /
    # symbol
    "!" : 33,
    '"' : 34,
    "#" : 35,
    "$" : 36,
    "%" : 37,
    "&" : 38,
    "'" : 39,
    "(" : 40,
    ")" : 41,
    "*" : 42,
    "+" : 43,
    "," : 44,
    "-" : 45,
    "." : 46,
    "/" : 47,

    "ZERO"  : 48, # 0
    "ONE"   : 49, # 1
    "TWO"   : 50, # 2
    "THREE" : 51, # 3
    "FOUR"  : 52, # 4
    "FIVE"  : 53, # 5
    "SIX"   : 54, # 6
    "SEVEN" : 55, # 7
    "EIGHT" : 56, # 8
    "NINE"  : 57, # 9
    # symbol
    "0": 48,
    "1": 49,
    "2": 50,
    "3": 51,
    "4": 52,
    "5": 53,
    "6": 54,
    "7": 55,
    "8": 56,
    "9": 57,

    "COLON"         : 58, # :
    "SEMICOLON"     : 59, # ;
    "LESS_THAN"     : 60, # <
    "EQUALS"        : 61, # =
    "GREATER_THAN"  : 62, # >
    "QUESTION_MARK" : 63, # ?
    "AT"            : 64, # @
    # symbol
    ":": 58,
    ";": 59,
    "<": 60,
    "=": 61,
    ">": 62,
    "?": 63,
    "@": 64,

    "SHIFT_A": 65, 
    "SHIFT_B": 66,
    "SHIFT_C": 67,
    "SHIFT_D": 68,
    "SHIFT_E": 69,
    "SHIFT_F": 70,
    "SHIFT_G": 71,
    "SHIFT_H": 72,
    "SHIFT_I": 73,
    "SHIFT_J": 74,
    "SHIFT_K": 75,
    "SHIFT_L": 76,
    "SHIFT_M": 77,
    "SHIFT_N": 78,
    "SHIFT_O": 79,
    "SHIFT_P": 80,
    "SHIFT_Q": 81,
    "SHIFT_R": 82,
    "SHIFT_S": 83,
    "SHIFT_T": 84,
    "SHIFT_U": 85,
    "SHIFT_V": 86,
    "SHIFT_W": 87,
    "SHIFT_X": 88,
    "SHIFT_Y": 89,
    "SHIFT_Z": 90,

    "LEFT_BRACKET"  : 91, # [
    "BACK_SLASH"    : 92, # \
    "RIGHT_BRACKET" : 93, # ]
    "CARET"         : 94, # ^
    "UNDER_SCORE"   : 95, # _
    "BACK_QUOTE"    : 96, # ` (sometimes it's called `grave accent`)
    # symbol
    "["  : 91,
    "¥"  : 92, # in windows?
    "\\" : 92,
    "]"  : 93,
    "^"  : 94,
    "_"  : 95,
    "`"  : 96,

    "A": 97,
    "B": 98,
    "C": 99,
    "D": 100,
    "E": 101,
    "F": 102,
    "G": 103,
    "H": 104,
    "I": 105,
    "J": 106,
    "K": 107,
    "L": 108,
    "M": 109,
    "N": 110,
    "O": 111,
    "P": 112,
    "Q": 113,
    "R": 114,
    "S": 115,
    "T": 116,
    "U": 117,
    "V": 118,
    "W": 119,
    "X": 120,
    "Y": 121,
    "Z": 122,

    "LEFT_BRACE"  : 123, # {
    "PIPE"        : 124, # | as same as `vertical bar`
    "RIGHT_BRACE" : 125, # }
    "TILDE"       : 126, # ~
    "BACK_SPACE"  : 127, #  
    # symbol
    "{"           : 123,
    "|"           : 124,
    "}"           : 125,
    "~"           : 126,

    # ALT + keys
    # well, it seem on macOS, it will input some unicode char.
    # so I will skip it.
    #"ALT_WITH_SOME_KEY"  : 1001~?, #  

    # these keys were caught in macOS
    # I don't know it is same in other OSs
    # also, I don't know right/left of shift or control change the code.
    #
    # arrow_up_key    27 91 65
    # arrow_down_key  27 91 66
    # arrow_right_key 27 91 67
    # arrow_left_key  27 91 68
    #
    # pgup_key 27 91 53 126
    # pgdn_key 27 91 54 126
    # del_key  27 91 51 126
    # end_key  27 91 70
    # home_key 27 91 72
    #
    # F1  27 79 80
    # F2  27 79 81
    # F3  27 79 82
    # F4  27 79 83
    #
    # F5  27 91 49 53 126 <- ??
    # F6  27 91 49 55 126 <- ????????
    # F7  27 91 49 56 126
    # F8  27 91 49 57 126
    #
    # F9  27 91 50 48 126
    # F10 27 91 50 49 126
    # F11 27 91 50 51 126 <- ??
    # F12 27 91 50 52 126
    #
    # Ps/SR (Print Screen/System Request) 27 91 49 59 50 80
    #
    # SHIFT_ARROW_UP         27 91 49 59 50 65
    # SHIFT_ARROW_DOWN       27 91 49 59 50 66
    # SHIFT_ARROW_RIGHT      27 91 49 59 50 67
    # SHIFT_ARROW_LEFT       27 91 49 59 50 68
    #
    # CTRL_ARROW_UP          27 91 49 59 53 65
    # CTRL_ARROW_DOWN        27 91 49 59 53 66
    # CTRL_ARROW_RIGHT       27 91 49 59 53 67
    # CTRL_ARROW_LEFT        27 91 49 59 53 68
    #
    # CTRL_SHIFT_ARROW_UP    27 91 49 59 54 65
    # CTRL_SHIFT_ARROW_DOWN  27 91 49 59 54 66
    # CTRL_SHIFT_ARROW_RIGHT 27 91 49 59 54 67
    # CTRL_SHIFT_ARROW_LEFT  27 91 49 59 54 68
    #
    # utf-8 codes 
    # 0x00 -> 0x7f : start of 1byte
    # 0x80 -> 0xbf : code of multibyte
    # 0xc0 -> 0xdf : start of 2bytes char
    # 0xe0 -> 0xef : start of 3bytes char
    # 0xf0 -> 0xff : start of 4bytes char
    #
    # set virtual key code for non-single represented keys
    # at least 1000 > will not harm 1 byte input codes
    #"NOT_USED"  : 1000,
    "ARROW_UP"   : 1001,
    "ARROW_DOWN" : 1002,
    "ARROW_RIGHT": 1003,
    "ARROW_LEFT" : 1004,

    "PAGE_UP"    : 1005,
    "PAGE_DOWN"  : 1006,
    "DEL"        : 1007,
    "END"        : 1008,
    "INSERT"     : 1009, # does it work for a input key?
    "HOME"       : 1010,

    "PS/SR"      : 1011,

    "F1"         : 1012,
    "F2"         : 1013,
    "F3"         : 1014,
    "F4"         : 1015,
    "F5"         : 1016,
    "F6"         : 1017,
    "F7"         : 1018,
    "F8"         : 1019,
    "F9"         : 1020,
    "F10"        : 1021,
    "F11"        : 1022,
    "F12"        : 1023,

    "SHIFT_ARROW_UP"         : 1024,
    "SHIFT_ARROW_DOWN"       : 1025,
    "SHIFT_ARROW_RIGHT"      : 1026,
    "SHIFT_ARROW_LEFT"       : 1027,

    "CTRL_ARROW_UP"          : 1028,
    "CTRL_ARROW_DOWN"        : 1029,
    "CTRL_ARROW_RIGHT"       : 1030,
    "CTRL_ARROW_LEFT"        : 1031,

    "CTRL_SHIFT_ARROW_UP"    : 1032,
    "CTRL_SHIFT_ARROW_DOWN"  : 1033,
    "CTRL_SHIFT_ARROW_RIGHT" : 1034,
    "CTRL_SHIFT_ARROW_LEFT"  : 1035
}

# for some env specific alteration if needed 
if _is_windows:
    pass
else:
    pass

# for get key name
# different name in same value will be overwritten by the name declared later
code2key_name = {v: k for k, v in key_codes.items()}
