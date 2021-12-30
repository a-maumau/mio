import os

if os.name == 'nt':
    _is_windows = True
else:
    _is_windows = False

# Windows do not have termios
if _is_windows:
    import msvcrt
else:
    import sys
    import tty
    import atexit
    import termios
    from select import select

import keys

class KeyInput:
    def __init__(self):
        '''A class to parse input with no echo, and do not wait for enter.
        '''
        
        if _is_windows:
            # msvcrt's getch() is not implemented in multiple byte reading.
            # so it is impossible to distinguishing "ESC" and keys which have multiple sequence
            # without blocking.
            #
            # need to look for something... or set a timeout?
            self._getch = msvcrt.getch
            self.kbhit = msvcrt.kbhit()
        else:
            self.fd = sys.stdin.fileno()

            # save current terminal settings
            self.old_term = termios.tcgetattr(self.fd)

            # create new terminal setting
            self.new_term = termios.tcgetattr(self.fd)
            # non-canonical, noecho
            # same thing as tty.setcbreak(sys.stdin.fileno())
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            # use new terminal settings
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # sys.stdin.read(n) will block until n chars has been read from stdin
            # this makes things hard like distinguishing "ESC" and keys which have multiple sequence
            # like "ESC+..." (e.g. arrow keys)
            #
            # read n char from input
            self._getch = lambda n=1: os.read(sys.stdin.fileno(), n)
            self.kbhit = self._kbhit_posix

            # change if needed
            #self._parse_key_posix = lambda x: 0

            self._key_buffer = None
            self.parse_key = self._parse_key_posix

            # in case `restore_default_settings()` was not called for some reason,
            # restore default (previous) settings at cleanup
            atexit.register(self.restore_default_settings)

    def restore_default_settings(self):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def _parse_key_windows(self):
        pass

    def _parse_key_posix(self):
        """Function for parse key input.

        NOTE:
            Some OS might have different sequences,
            so please rewrite this functon if needed.

            also, simultaneously pressing "ESC" and non-ESC start key is not parsable
            because multi sequence input use "ESC" (0x1b) for first byte.
        """

        if self._key_buffer is not None:
            if self._key_buffer != 27:
                key_input = self._key_buffer
                self._key_buffer = None

                return key_input

            elif self._key_buffer == 27:
                # stdin must readable immediately
                key_input = [self._key_buffer]+[self._getch(1)[0]]
                self._key_buffer = None

        else:
            # getch() -> b'A'
            # check if following char exist by reading 2 bytes
            key_input = self._getch(2)
            input_num = len(key_input)

            # single input
            if input_num == 1:
                return key_input[0]

            # read 2 bytes
            else:
                if key_input[0] != 27:
                    self._key_buffer = key_input[1]
                    return key_input[0]

        # avoid key input of "ESC"+"some_mutiple_sequence_key" which starts from "ECS" to get parsed
        if key_input[0] == 27 and key_input[1] == 27:
            self._key_buffer = key_input[1]
            return key_input[0]

        # might be slow to read 1 byte each time... 
        # case of "mutiple_sequence_key"
        # always key_input[0] == 27
        if key_input[1] == 91:
            seq_3 = self._getch(1)[0]

            # 27 91 *
            if seq_3 == 65:
                return keys.key_codes["ARROW_UP"]
            elif seq_3 == 66:
                return keys.key_codes["ARROW_DOWN"]
            elif seq_3 == 67:
                return keys.key_codes["ARROW_RIGHT"]
            elif seq_3 == 68:
                return keys.key_codes["ARROW_LEFT"]

            # 27 91 49 *
            elif seq_3 == 49:
                seq_4 = self._getch(1)[0]

                # 27 91 49 * 126 #####################
                if seq_4 == 53:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F5"]
                elif seq_4 == 55:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F6"]
                elif seq_4 == 56:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F7"]
                elif seq_4 == 57:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F8"]
                ######################################

                # 27 91 49 59 * * 
                elif seq_4 == 59:
                    seq_5 = self._getch(1)[0]

                    # 27 91 49 59 50 *
                    if seq_5 == 50:
                        seq_6 = self._getch(1)[0]
                        if seq_6 == 65:
                            return keys.key_codes["SHIFT_ARROW_UP"]
                        elif seq_6 == 66:
                            return keys.key_codes["SHIFT_ARROW_DOWN"]
                        elif seq_6 == 67:
                            return keys.key_codes["SHIFT_ARROW_RIGHT"]
                        elif seq_6 == 68:
                            return keys.key_codes["SHIFT_ARROW_LEFT"]

                        elif seq_6 == 80:
                            return keys.key_codes["PS/SR"]
                        
                        else:
                            return keys.key_codes["UNKNOWN_KEY"]

                    # 27 91 49 59 53 *
                    elif seq_5 == 53:
                        seq_6 = self._getch(1)[0]
                        if seq_6 == 65:
                            return keys.key_codes["CTRL_ARROW_UP"]
                        elif seq_6 == 66:
                            return keys.key_codes["CTRL_ARROW_DOWN"]
                        elif seq_6 == 67:
                            return keys.key_codes["CTRL_ARROW_RIGHT"]
                        elif seq_6 == 68:
                            return keys.key_codes["CTRL_ARROW_LEFT"]
                        else:
                            return keys.key_codes["UNKNOWN_KEY"]

                    # 27 91 49 59 54 *
                    elif seq_5 == 54:
                        seq_6 = self._getch(1)[0]
                        if seq_6 == 65:
                            return keys.key_codes["CTRL_SHIFT_ARROW_UP"]
                        elif seq_6 == 66:
                            return keys.key_codes["CTRL_SHIFT_ARROW_DOWN"]
                        elif seq_6 == 67:
                            return keys.key_codes["CTRL_SHIFT_ARROW_RIGHT"]
                        elif seq_6 == 68:
                            return keys.key_codes["CTRL_SHIFT_ARROW_LEFT"]
                        else:
                            return keys.key_codes["UNKNOWN_KEY"]
                    else:
                        return keys.key_codes["UNKNOWN_KEY"]

            # 27 91 50 * 126
            elif seq_3 == 50:
                seq_4 = self._getch(1)[0]

                if seq_4 == 48:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F9"]
                elif seq_4 == 49:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F10"]
                elif seq_4 == 51:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F11"]
                elif seq_4 == 52:
                    # read remain
                    _ = self._getch(1)
                    return keys.key_codes["F12"]

                else:
                    return keys.key_codes["UNKNOWN_KEY"]


            # 27 91 * 126
            elif seq_3 == 53:
                # read remain
                _ = self._getch(1)
                return keys.key_codes["PAGE_UP"]
            elif seq_3 == 54:
                # read remain
                _ = self._getch(1)
                return keys.key_codes["PAGE_DOWN"]
            elif seq_3 == 51:
                # read remain
                _ = self._getch(1)
                return keys.key_codes["DEL"]

            # 27 91 * 
            elif seq_3 == 70:
                return keys.key_codes["END"]
            elif seq_3 == 72:
                return keys.key_codes["HOME"]
            
            else:
                return keys.key_codes["UNKNOWN_KEY"]

        elif key_input[1] == 79:
            seq_3 = self._getch(1)[0]

            # 27 79 *
            if seq_3 == 80:
                return keys.key_codes["F1"]
            elif seq_3 == 81:
                return keys.key_codes["F2"]
            elif seq_3 == 82:
                return keys.key_codes["F3"]
            elif seq_3 == 83:
                return keys.key_codes["F4"]
            else:
                return keys.key_codes["UNKNOWN_KEY"]

        else:
            return keys.key_codes["UNKNOWN_KEY"]

    def _kbhit_posix(self):
        # this is for when remain input is exist
        if self._key_buffer:
            return True

        # if sys.stdin has some input, it will return TextIOWrapper object
        # 0 for non-blocking
        read_key, _, _ = select([sys.stdin], [], [], 0)

        return read_key != []
 
if __name__ == "__main__":
    import time
    import keys

    print("press q to quit.")

    k = KeyInput()
    while True:
        if k.kbhit():
            a = k.parse_key()
            print(f"{a}: {keys.code2key_name[a] if a in keys.code2key_name else a}")

            if ord("q") == a:
                break

        # https://www.typinglounge.com/worlds-fastest-typists
        # it says, "using stenotype machine, 360 wpm at 97% accuracy."
        # if we consider one word as 7 character, 42 char/s -> 23.8 c/ms
        # so at least sleeping 20ms will be comfortable for typing and can save cpu load, I hope.
        # parsing key input might take some time?
        time.sleep(0.020)
