import sys
import time

from abc import ABCMeta, abstractmethod

"""Base class for widgets

Note:
    Do not include the `self` parameter in the ``Args`` section.

Args:
    status_bar_msg (str): Used for printing status bar
    desc (str)          : The second parameter.

Returns:
    True if successful, False otherwise.

"""

class Component(metaclass=ABCMeta):
    def __init__(self):
        self.drawing = True

    def hide(self):
        self.drawing = False

    def show(self, name):
        self.drawing = True

    @abstractmethod
    def draw(self):
        pass

class Widget(Component):
    """Base class for widgets


    """
    def __init__(self, status_bar_msg, desc):
        """test

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            status_bar_msg (str): Used for printing status bar
            desc (str)          : The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        super(Widget, self).__init__()

        self.status_bar_msg = status_bar_msg
        self.desc = desc

        self.key_bind = {}

    def bind_key(self, key, action):
        self.key_bind[key] = action

    def del_key_bind(self, key):
        self.key_bind.pop(key, None)

class TextBox(Widget):
    def __init__(self, initial_text="", status_bar_msg="", desc="", text_wrap=True):
        super(TextBox, self).__init__(status_bar_msg, desc)

        if isinstance(initial_text, list):
            self.texts = initial_text
        elif isinstance(initial_text, str):
            self.texts = initial_text.splitlines()
        else:
            self.texts = []

        self.text_wrap = text_wrap

        self.text_line_num = 0
        self.box_line_num = 0

    def draw(self, _curses, win, x=0, y=0, width=0, height=0):
        pass

    def draw_test(self, _curses, win, x=0, y=0, width=0, height=0):
        """Draw all
        """

        curses.noecho()
        curses.cbreak()

        win2 = curses.newwin(10, 30, 3, 8)

        _curses.clear()
        win.clear()

        for i, txts in enumerate(self.texts):
            win.addstr(i, 0, txts)

        for i, txts in enumerate(["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbbbbbbbbbbbbbbbbb"]):
            win2.addstr(i, 0, txts)

        _curses.refresh()
        win.refresh()
        win2.refresh()
        #print("called: TextBox")
        _curses.getkey()

    def draw_test(self, _curses, win, x=0, y=0, width=0, height=0):
        """Draw all
        """

        from pycui import TerminalManager, Segment, TextStyle
        tm = TerminalManager()
        tm.init()

        sg = []
        import random
        for i in range(10000):
            x = random.randint(0, 30)
            y = random.randint(0, 20)
            style = random.sample(["BOLD","ITALIC","UNDERLINE","REVERSE","STRIKETHROUGH"], 2)

            sg.append(Segment("random", style=TextStyle(styles=style), cursor_begin_pos=(x,y)))

        tm.add_to_buffer([Segment("text segment", style=TextStyle(styles=["REVERSE"]), cursor_begin_pos=(10,20), cursor_end_pos=None),
                          Segment("text segment", style=TextStyle(fg_color="GREEN", styles=["REVERSE"]), cursor_begin_pos=(10,21), cursor_end_pos=None),
                          ]+sg)
        tm._render()

        tm.move_cursor_to(-3, -2)
        tm.print("adfada")

        # move to x,y
        mv = lambda x,y: sys.stdout.write(f"\x1b[{y+1};{x+1}H")
        mv(0,0)
        mv(3,0)
        sys.stdout.write("ssssss")
        sys.stdout.flush()

        mv(7, 4)
        sys.stdout.write("ssssss")
        sys.stdout.flush()

        import os
        mv(7,5)
        term = os.getenv('TERM')
        sys.stdout.write(str(term))
        sys.stdout.write("\033[31;1;4mHello\033[0m")
        mv(7,6)
        sys.stdout.write("\x1b[31;1;4mHello\x1b[0m")
        sys.stdout.flush()

        time.sleep(3)

        #sys.stdout.write("\x1b[2J\x1b[?47l\x1b8")
        sys.stdout.write("\x1b[?1049l")
        sys.stdout.flush()

    def update(self):
        pass

if __name__ == '__main__':
    import curses

    t = TextBox("test\nthis text\nshould appear\nyey!", "", "")

    #stdscr = curses.initscr()
    #win = curses.newwin(10, 30, 2, 4)
    #curses.wrapper(lambda x: t.draw_test(x, win))
    t.draw_test("a", "b")

    from test_file import test_class_field, c

    print(test_class_field.a)
    c.data = "c"
    test_class_field.a = "a"
    print(test_class_field.a)

