import os
import sys
import atexit

from ces import TerminalControlEscapeSequence
from utils import truncate_str
from rendering import Renderer, BorderLine

# for lower python version, not using dataclass

"""
- terminal can have multiple windows.
- windows can have multiple panes.
- layout can have mutiple panes
- panes can only have one widget.

(not thinking tab right now, use window for do same thing)

    
+-terminal-----------------------+  --------------------------------------
| +-window (current, visible)--+ |  +-window (other, invisible)--+ | ...
| | +-pane--------------------+| |  |+-pane---------------------+| |
| | |                         || |  ||                          || |
| | |       some widget       || |  ||                          || |
| | +-------------------------+| |  ||                          || |
| | +-pane--------------------+| |  ||                          || |
| | |                         || |         .                       |
| | |       some widget       || |         .                       |
| | +-------------------------+| |         .                       |
| +----------------------------+ |                                 |
+--------------------------------+
 <------------------------------>   <------------------------------------>
         rendered window                     non-rendered window


BLUE PRINT

pyui
    main loop
        check keyinput
        update screen

TerminalManager
    store terminal settings

render
    render UIs
    render buffer

controller
    parse_key
    hook(key, action)

UI
    Window
        active pane
        control

    Layout
        control

    Pane
        widgets
            control

"""


class TerminalTheme(object):
    def __init__(self, default_text_style):
        # default colors
        self.default_style = default_text_style
        self.registered_styles = {}

    def assign_style(self, name, text_style):
        self.registered_styles[name] = text_style

class BorderChars(object):
    def __init__(self, up_left, up_right, down_left, down_right, horizontal, vertical):
        self.up_left = up_left
        self.up_right = up_right
        self.down_left = down_left
        self.down_right = down_right
        self.horizontal = horizontal
        self.vertical = vertical

class PMUI(object):
    def __init__(self, theme=None, use_alt_screen=True, output=None):
        output = output_target if output_target else sys.stdout

        self.theme = theme if theme is not None else TerminalTheme(TextStyle())
        self.renderer = Renderer(self.theme, output)
        self.terminal_manager = TerminalManager(theme, renderer, use_alt_screen)

    def _render(self):
        self.renderer.process()

class UIManager(object):
    def __init__(self, terminal_manager, renderer):
        self.term = terminal_manager
        self.renderer = renderer

        # this list order is the window layer order start from 0 (bottom)
        self.window_list = []
        self.window_names = {}

        self._current_window = None
        self._current_window_idx = -1
        self._current_window_hook_name = None

    def new_window(self, window_title=None, x=0, y=0, width=None, height=None, margin=[0,0,0,0],
                         title_pos=None, title_label_margin=(4, None), title_text_margin=(1,1),
                         window_description="",
                         window_hook_name=None, use_utf8=False):
        
        hook_name = window_hook_name if window_hook_name else window_title

        win = Window(self.renderer, window_title, x, y,
                     width if width else self.term.width,
                     height if height else self.term.height,
                     margin,
                     title_pos, title_label_margin, title_text_margin,
                     window_description)

        if use_utf8:
            # \u2026 is a horizontal ellipsis
            win.ellipsis_char = "\u2026"
            win.set_border_char("\u250C", "\u2510", "\u2514", "\u2518", "\u2500", "\u2502")

            win.update_title()
            win.update_border()

        if hook_name in self.window_names:
            _win = self.window_names[hook_name]
            ind = self.get_window_index(_win)

            self.window_names[hook_name] = win
            self.window_list[ind] = win

        else:
            self.window_names[hook_name] = win
            self.window_list.append(win)

        self._update_current_focus_window_info()

        return win

    def add_window(self, window, window_order=None, window_hook_name=None):
        hook_name = window_hook_name if window_hook_name else window.title

        if window_order is None:
            # swap window
            if hook_name in self.window_names:
                _win = self.window_names[hook_name]
                ind = self.get_window_index(_win)

                self.window_names[hook_name] = window
                self.window_list[ind] = window
            # append window
            else:
                self.window_names[hook_name] = window
                self.window_list.append(window)
        else:
            if hook_name in self.window_names:
                self.change_window_order(hook_name, window_order)

                _win = self.window_names[hook_name]
                ind = self.get_window_index(_win)

                self.window_names[hook_name] = window
                self.window_list[ind] = window

            else:
                self.window_names[hook_name] = window
                self.window_list.insert(ind, window)

        self._update_current_focus_window_info()

    def _update_current_focus_window_info(self):
        if self._current_window_hook_name:
            if self._current_window_hook_name in self.window_names:
                self._current_window_idx = self.get_window_index(self._current_window_hook_name)

        # for initilization
        else:
            if len(self.window_list) < 1:
                self._current_window = None
                self._current_window_idx = -1
                self._current_window_hook_name = None

            else:
                self._current_window = self.window_list[self._current_window_idx]
                # searching by Window object, so if there are same objects in dict,
                # the result might not be what you expected
                for k, v in self.window_names.items():
                    if self._current_window == v:
                        self._current_window_hook_name = k

    def get_window(self, window_hook_name):
        # search by hooked name
        if window_hook_name in self.window_names:
            return self.window_names[window_hook_name]
        else:
            return None

    def get_window_index(self, window_hook_name):
        # search by hooked name
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            return self.window_list.index(win)
        else:
            return -1

    def change_window_order(self, window_hook_name, idx):
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            curr_idx = self.get_window_index(window_hook_name)

            if idx <= curr_idx:
                self.window_list.insert(idx, win)
                self.window_list.pop(curr_idx+1)
            else:
                self.window_list.insert(idx, win)
                self.window_list.pop(curr_idx)

            self._update_current_focus_window_info()

    def delete_window(self, window_hook_name):
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            idx = self.get_window_index(window_hook_name)

            self.window_names.pop(window_hook_name)
            self.window_list.pop(idx)

            self._current_window = None
            self._current_window_idx -= 1
            self._current_window_hook_name = None

            self._update_current_focus_window_info()


class TerminalManager(object):
    """Class for handle console settings and cursor.
    """

    def __init__(self, renderer, use_alt_screen=True):
        #self.theme = term_theme if term_theme is not None else TerminalTheme(TextStyle())
        self.renderer = renderer
        self.use_alt_screen = use_alt_screen

        # printing target
        self.output = sys.stdout
        
        self.os_name = os.name
        self.term_name = os.getenv('TERM').lower()
    
        # this only holds the inital size        
        term_size = os.get_terminal_size()
        self.terminal_width = term_size.columns
        self.terminal_height = term_size.lines

        # queue for rendering
        self._buffer = []
        
        # this list order is the window layer order start from 0 (bottom)
        self.window_list = []
        self.window_names = {}

        self._current_window = None
        self._current_window_idx = -1
        self._current_window_hook_name = None

        self._setup_control_functions()

        # for cleanup, restore default terminal settings
        atexit.register(self._restore_default)

    def _restore_default(self):
        self.show_cursor()
        self._reset_style()
        if self.use_alt_screen:
            self._disable_alt_screen()

    def _setup_control_functions(self):
        """
        NOTE:
            if wrapping a functon to _gen_*_ces cause speed issue, we should implement in native function,
            and create a TerminalManager for each terminal/environment.

            this is for capability of switching the control escape sequence to different easily,
            and for reducing unwated `flush()` call to the screen/system.

            We can think using option flush=True, if-statement may be harmful for speed.
        """

        self._gen_move_cursor_to_head_ces = TerminalControlEscapeSequence.control_functions["CARRIAGE_RETURN"]
        self._gen_ring_bell_ces = TerminalControlEscapeSequence.control_functions["BELL"]
        self._gen_clear_ces = TerminalControlEscapeSequence.control_functions["CLEAR"]
        
        self._gen_show_cursor_ces = TerminalControlEscapeSequence.control_functions["SHOW_CURSOR"]
        self._gen_hide_cursor_ces = TerminalControlEscapeSequence.control_functions["HIDE_CURSOR"]
        self._gen_move_cursor_up_ces = TerminalControlEscapeSequence.control_functions["CURSOR_UP"]
        self._gen_move_cursor_down_ces = TerminalControlEscapeSequence.control_functions["CURSOR_DOWN"]
        self._gen_move_cursor_forward_ces = TerminalControlEscapeSequence.control_functions["CURSOR_FORWARD"]
        self._gen_move_cursor_backward_ces = TerminalControlEscapeSequence.control_functions["CURSOR_BACKWARD"]
        self._gen_move_cursor_to_column_ces = TerminalControlEscapeSequence.control_functions["CURSOR_MOVE_TO_COLUMN"]
        self._gen_move_cursor_to_ces = TerminalControlEscapeSequence.control_functions["CURSOR_MOVE_TO"]
        
        self._gen_erace_display_ces = TerminalControlEscapeSequence.control_functions["ERASE_IN_DISPLAY"]
        self._gen_erase_line_ces = TerminalControlEscapeSequence.control_functions["ERASE_IN_LINE"]
        
        if self.term_name == "xterm":
            self._gen_enable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["ENABLE_ALT_SCREEN_XTERM"]
            self._gen_disable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["DISABLE_ALT_SCREEN_XTERM"]

        elif self.term_name == "xterm-256color":
            self._gen_enable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["ENABLE_ALT_SCREEN_XTERM_256_COLOR"]
            self._gen_disable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["DISABLE_ALT_SCREEN_XTERM_256_COLOR"]

        else:
            # use xterm settings
            self._gen_enable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["ENABLE_ALT_SCREEN_XTERM"]
            self._gen_disable_alt_screen_ces = TerminalControlEscapeSequence.control_functions["DISABLE_ALT_SCREEN_XTERM"]

    def _flush(self):
        self.output.flush()

    def _render(self):
        for segments in self._buffer:
            for sgmt in segments:
                if sgmt.cursor_begin_pos:
                    self.output.write(self._gen_move_cursor_to_ces(*sgmt.cursor_begin_pos))

                self.output.write(self.text_formatter.format(sgmt.text, sgmt.style))

                if sgmt.cursor_end_pos:
                    self.output.write(self._gen_move_cursor_to_ces(*sgmt.cursor_end_pos))

        self.output.flush()
        
        self._buffer = []

    def init(self):
        if self.use_alt_screen:
            self._enable_alt_screen()

        self.clear_screen()
        self.move_cursor_to(0,0)

    def disable_key_input(self):
        pass

    def print(self, text, do_flush=True):
        """Print a characters on output (screen/sys.stdout for default)
        """
        
        self.output.write(text)
        if do_flush:
            self.output.flush()

    def add_to_buffer(self, segments):
        self._buffer.append(segments)

    def move_cursor_to_head(self):
        self.renderer.print(self._gen_move_cursor_to_head_ces())

    def ring_bell(self):
        self.renderer.print(self._gen_ring_bell_ces())

    def clear_screen(self):
        self.renderer.print(self._gen_clear_ces())

    def show_cursor(self):
        self.renderer.print(self._gen_show_cursor_ces())

    def hide_cursor(self):
        self.renderer.print(self._gen_hide_cursor_ces())

    def move_cursor_up(self, num):
        self.renderer.print(self._gen_move_cursor_up_ces(num))

    def move_cursor_down(self, num):
        self.renderer.print(self._gen_move_cursor_down_ces(num))

    def move_cursor_forward(self, num):
        self.renderer.print(self._gen_move_cursor_forward_ces(num))

    def move_cursor_backward(self, num):
        self.renderer.print(self._gen_move_cursor_backward_ces(num))

    def move_cursor_to_colmun(self, num):
        self.renderer.print(self._gen_move_cursor_to_column_ces(num))

    def move_cursor_to(self, x, y):
        self.renderer.print(self._gen_move_cursor_to_ces(x, y))
        
    def erase_display(self, param=2):
        self.renderer.print(self._gen_erace_display_ces(param))

    def erase_in_line(self, param=0):
        self.renderer.print(self._gen_erase_line_ces(param))

    def _enable_alt_screen(self): 
        self.renderer.print(self._gen_enable_alt_screen_ces())

    def _disable_alt_screen(self):
        self.renderer.print(self._gen_disable_alt_screen_ces())

    def _reset_style(self):
        self.renderer.print(self.text_formatter.clear_ces)

    @property
    def width(self):
        return self.terminal_width

    @property
    def height(self):
        return self.terminal_height

    @property
    def size(self):
        return (self.terminal_width, self.terminal_height)

    def new_window(self, window_title=None, x=0, y=0, width=None, height=None, margin=[0,0,0,0],
                         title_pos=None, title_label_margin=(4, None), title_text_margin=(1,1),
                         window_description="",
                         window_hook_name=None, use_utf8=False):
        
        hook_name = window_hook_name if window_hook_name else window_title

        win = Window(self, window_title, x, y,
                     width if width else self.width,
                     height if height else self.height,
                     margin,
                     title_pos, title_label_margin, title_text_margin,
                     window_description)

        if use_utf8:
            # \u2026 is a horizontal ellipsis
            win.ellipsis_char = "\u2026"
            win.set_border_char("\u250C", "\u2510", "\u2514", "\u2518", "\u2500", "\u2502")

            win.update_title()
            win.update_border()

        if hook_name in self.window_names:
            _win = self.window_names[hook_name]
            ind = self.get_window_index(_win)

            self.window_names[hook_name] = win
            self.window_list[ind] = win

        else:
            self.window_names[hook_name] = win
            self.window_list.append(win)

        self._update_current_focus_window_info()

        return win

    def add_window(self, window, window_order=None, window_hook_name=None):
        hook_name = window_hook_name if window_hook_name else window.title

        if window_order is None:
            # swap window
            if hook_name in self.window_names:
                _win = self.window_names[hook_name]
                ind = self.get_window_index(_win)

                self.window_names[hook_name] = window
                self.window_list[ind] = window
            # append window
            else:
                self.window_names[hook_name] = window
                self.window_list.append(window)
        else:
            if hook_name in self.window_names:
                self.change_window_order(hook_name, window_order)

                _win = self.window_names[hook_name]
                ind = self.get_window_index(_win)

                self.window_names[hook_name] = window
                self.window_list[ind] = window

            else:
                self.window_names[hook_name] = window
                self.window_list.insert(ind, window)

        self._update_current_focus_window_info()

    def _update_current_focus_window_info(self):
        if self._current_window_hook_name:
            if self._current_window_hook_name in self.window_names:
                self._current_window_idx = self.get_window_index(self._current_window_hook_name)

        # for initilization
        else:
            if len(self.window_list) < 1:
                self._current_window = None
                self._current_window_idx = -1
                self._current_window_hook_name = None

            else:
                self._current_window = self.window_list[self._current_window_idx]
                # searching by Window object, so if there are same objects in dict,
                # the result might not be what you expected
                for k, v in self.window_names.items():
                    if self._current_window == v:
                        self._current_window_hook_name = k

    def get_window(self, window_hook_name):
        # search by hooked name
        if window_hook_name in self.window_names:
            return self.window_names[window_hook_name]
        else:
            return None

    def get_window_index(self, window_hook_name):
        # search by hooked name
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            return self.window_list.index(win)
        else:
            return -1

    def change_window_order(self, window_hook_name, idx):
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            curr_idx = self.get_window_index(window_hook_name)

            if idx <= curr_idx:
                self.window_list.insert(idx, win)
                self.window_list.pop(curr_idx+1)
            else:
                self.window_list.insert(idx, win)
                self.window_list.pop(curr_idx)

            self._update_current_focus_window_info()

    def delete_window(self, window_hook_name):
        if window_hook_name in self.window_names:
            win = self.window_names[window_hook_name]
            idx = self.get_window_index(window_hook_name)

            self.window_names.pop(window_hook_name)
            self.window_list.pop(idx)

            self._current_window = None
            self._current_window_idx -= 1
            self._current_window_hook_name = None

            self._update_current_focus_window_info()

class DrawableArea(object):
    """Base class of Window and Pane
    """

    def __init__(self, x, y, width, height, margin):
        """
            margin list[4, int]:
                Margins for the inner area. If you want make outer margin, use x, y, width, height for it.
                It will set a specified character size margin at up, right, bottom and left, respectively.
                If margin was int or [2, int], it will set a same margin, or set a up/bottom and right/left margin.
        """

        self.x = x
        self.y = y
        self.width = max(width,0)
        self.height = max(height,0)

        self._margin_top = 0
        self._margin_right = 0
        self._margin_bottom = 0
        self._margin_left = 0
        self.set_margin(margin)

        self.draw_component = True
        self.component_list = {}
        self.draw_list = []

        self.border_chars = BorderChars('+', '+', '+', '+', '-', '|')
        self.border_erase_chars = BorderChars(' ', ' ', ' ', ' ', ' ', ' ')

    @property
    def area(self):
        return (self.x, self.y, self.width, self.height)

    #@property.setter
    def set_area(self, x, y, width, height):
        """
            re-init of area
        """

        self.x = x
        self.y = y
        self.width = max(width,0)
        self.height = max(height,0)

    @property
    def pos(self):
        return (self.x, self.y)

    #@property.setter
    def set_pos(self, x, y):
        """
            set the window position to (x, y)
            which origin is top-left corner of the terminal.
        """

        self.x = x
        self.y = y

    @property
    def size(self):
        return (self.width, self.height)

    #@property.setter
    def set_size(self, width, height):
        """set the area size.        

        the area will be a square of

        .. code-block:: text

            (x, y)            (x+width, y)
                +-------------+
                |             |
                |             |
                |             |
                |             |
                +-------------+
            (x, y+height)    (x+width, y+height)
        """

        self.width = max(width,0)
        self.height = max(height,0)

    def get_valid_drawing_area(self):
        """

        Returning:
            top-left corner position and width, height.
        """

        return (self.x+self._margin_left,
                self.y+self._margin_top,
                self.width-(self._margin_right+self._margin_left),
                self.height-(self._margin_top+self._margin_bottom))

    @property
    def border_chars(self):
        return (self.border_chars.up_left,
                self.border_chars.up_right,
                self.border_chars.down_left,
                self.border_chars.down_right,
                self.border_chars.horizontal,
                self.border_chars.vertical)

    def set_border_char(self, up_left, up_right, down_left, down_right, horizontal, vertical):
        self.border_chars.up_left = up_left
        self.border_chars.up_right = up_right
        self.border_chars.down_left = down_left
        self.border_chars.down_right = down_right
        self.border_chars.horizontal = horizontal
        self.border_chars.vertical = vertical

    @property
    def border_erase_chars(self):
        return (self.border_erase_chars.up_left,
                self.border_erase_chars.up_right,
                self.border_erase_chars.down_left,
                self.border_erase_chars.down_right,
                self.border_erase_chars.horizontal,
                self.border_erase_chars.vertical)

    def set_border_erase_char(self, up_left, up_right, down_left, down_right, horizontal, vertical):
        self.border_erase_chars.up_left = up_left
        self.border_erase_chars.up_right = up_right
        self.border_erase_chars.down_left = down_left
        self.border_erase_chars.down_right = down_right
        self.border_erase_chars.horizontal = horizontal
        self.border_erase_chars.vertical = vertical

    @property
    def margin(self):
        return (self._margin_top, self._margin_right, self._margin_bottom, self._margin_left)

    def set_margin(self, margin):
        if isinstance(margin, (list, tuple)):
            mrgn_l = len(margin) 
            if mrgn_l == 1:
                mrgn = max(margin[0], 0)
                self._margin_top = mrgn
                self._margin_right = mrgn
                self._margin_bottom = mrgn
                self._margin_left = mrgn
            elif mrgn_l == 2:
                mrgn = max(margin[0], 0)
                self._margin_top = mrgn
                self._margin_bottom = mrgn

                mrgn = max(margin[1], 0)
                self._margin_right = mrgn
                self._margin_left = mrgn
            elif mrgn_l == 4:
                self._margin_top = max(margin[0], 0)
                self._margin_right = max(margin[1], 0)
                self._margin_bottom = max(margin[2], 0)
                self._margin_left = max(margin[3], 0)
            else:
                pass
                #self._margin_top = 0
                #self._margin_right = 0
                #self._margin_bottom = 0
                #self._margin_left = 0
        elif isinstance(marginm, int):
            mrgn = max(margin, 0)
            self._margin_top = mrgn
            self._margin_right = mrgn
            self._margin_bottom = mrgn
            self._margin_left = mrgn
        else:
            pass
            #self._margin_top = 0
            #self._margin_right = 0
            #self._margin_bottom = 0
            #self._margin_left = 0

    def move(self, dx, dy):
        """
            set the window position to (x, y)
            which origin is top-left corner of the terminal.
        """

        self.x += dx
        self.y += dy

    def assign_component(self, name, component):
        self.component_list[name] = dr_obj
        self.draw_list = dr_obj

    def hide_component(self, name):
        if name in self.component_list:
            cmpnt = self.component_list[name]
            if cmpnt in self.draw_list:
                self.draw_list.remove(cmpnt)

    def show_component(self, name):
        if name in self.component_list:
            cmpnt = self.component_list[name]
            if cmpnt not in self.draw_list:
                self.draw_list.append(cmpnt)

class Window(DrawableArea):
    def __init__(self, renderer,
                       window_title, x, y, width, height,
                       margin=(0,0,0,0),
                       title_pos=None, title_label_margin=(2, None), title_text_margin=(1,1),
                       window_description=""):
        super(Window, self).__init__(x, y, width, height, margin)

        self.term_mgr = term_mgr
        self.renderer = renderer
        self.title = window_title

        self.clear_char = " "
        self.title_margin_char = " "
        self.ellipsis_char = "."

        # this is for who wants to print the title (window name) outside the border
        self._title_pos = title_pos
        self._title_printing_from = None
        self._title_length = 0
        self.set_title_margins(title_label_margin, title_text_margin)

        self.pane_list = []
        self.pane_names = {}

        #self.set_title_margin(self._title_label_margin)

        self.default_style = self.renderer.theme.default_style
        self._border_style_history = self.default_style
        self._title_style_history = self.default_style
        self._title_margin_style_history = self.default_style

        self._build_boarder_line_string()
        self._build_title_string()

        self.border_line_obj = BorderLine(self.x, self.y, self.width, self.height,
                                          self.style, self.border_chars, self.style, self.border_erase_chars)

    def set_title_margins(self, title_label_margin=None, title_text_margin=None):
        # min and max is used to avoid erasing the corners
        if title_label_margin:
            # label margin max is width without the corners (width-2)
            self._title_label_margin_left = min(max(title_label_margin[0],1),self.width-2) \
                                            if title_label_margin[0] != None else title_label_margin[0]
            self._title_label_margin_right = min(max(title_label_margin[1],1),self.width-2) \
                                             if title_label_margin[1] != None else title_label_margin[1]

        if title_text_margin:
            if self._title_label_margin_left != None:
                self._title_text_margin_left = min(max(title_text_margin[0],0),self.width-self._title_label_margin_left-2)
                self._title_text_margin_right = min(max(title_text_margin[1],0),self.width-self._title_text_margin_left-self._title_label_margin_left-2)
                
            elif self._title_label_margin_right != None:
                self._title_text_margin_left = min(max(title_text_margin[0],0),self.width-self._title_label_margin_right-2)
                self._title_text_margin_right = min(max(title_text_margin[1],0),self.width-self._title_text_margin_left-self._title_label_margin_right-2)

            else:
                self._title_text_margin_left = min(max(title_text_margin[0],0),self.width-2)
                self._title_text_margin_right = min(max(title_text_margin[1],0),self.width-self._title_text_margin_left-2)

    def update_title(self):
        self._build_title_string()

    def update_border(self):
        self._build_boarder_line_string()

    def new_pane(self, pane_name, relative_x=0, relative_y=0, width=0, height=0, margin=[1,1,1,1],
                       pane_hook_name=None, pane_description=""):
        """A function for creating pane and hooking the pane on Window
        """

        return Window(self, window_name,
                            self.x+relative_x,
                            self.y+relative_y,
                            width,
                            height,
                            margin)

    def new_window(self, window_title=None, x=0, y=0, width=None, height=None, margin=[0,0,0,0],
                         window_hook_name=None, window_description=""):
        win = Window(self,
                     window_title,
                     x,
                     y,
                     width if width else self.width,
                     height if height else self.height,
                     margin,
                     window_description)

        self.window_names[window_hook_name if window_hook_name else window_title] = win
        self.window_list.append(win)

    def add_pane(self, pane):
        """A function for hooking a pane on Window
        """

        self.pane_list.append()

    def _build_boarder_line_string(self):
        """
        """

        self._border_top_line_str = self.border_chars.up_left \
                                   +self.border_chars.horizontal*(self.width-2) \
                                   +self.border_chars.up_right

        self._border_bottom_line_str = self.border_chars.down_left \
                                      +self.border_chars.horizontal*(self.width-2) \
                                      +self.border_chars.down_right

    def show_boader(self):
        # if there is no margin, dont draw border
        if (0,0,0,0) == self.margin:
            return

        self.border_line_obj.set_draw()
        self.renderer.push(self.border_line_obj)

    def hide_border(self):
        if (0,0,0,0) == self.margin:
            return

        self.border_line_obj.set_erase()
        self.renderer.push(self.border_line_obj)

    def change_border_style(self, border_style=None, border_erase_style=None):
        self.border_line_obj.update(border_style=border_style, border_erase_style=border_erase_style)

    def _build_title_string(self):
        # this means it will overwrite the boarder chars
        if self._title_pos:
            self._title_str = self.title
            self._title_length = len(self.title)

        else:
            #
            #  label_margin_left       label_margin_right
            #   |                        |
            # <-->                     <-->
            #
            # +---   some_title_here   ---+
            #
            #     <->               <->
            #      |                 |
            # text_maring_left     text_margin_right
            #
            #

            if self._title_label_margin_left:
                title_len = max(self.width-1 \
                                -self._title_label_margin_left \
                                -(self._title_text_margin_left+self._title_text_margin_right),0)

                self._title_str = truncate_str(self.title,
                                               length=title_len,
                                               ellipsis=self.ellipsis_char,
                                               ellipsis_left=False)

                self._title_margin_left_str = f"{self.title_margin_char*self._title_text_margin_left}"
                self._title_margin_right_str = f"{self.title_margin_char*self._title_text_margin_right}"
                self._title_printing_from = self._title_label_margin_left
                self._title_length = len(self._title_str)+self._title_text_margin_left+self._title_text_margin_right

            elif self._title_label_margin_right:
                title_len = max(self.width-1 \
                                -self._title_label_margin_right \
                                -(self._title_text_margin_left+self._title_text_margin_right),0)

                self._title_str = truncate_str(self.title,
                                               length=title_len,
                                               ellipsis=self.ellipsis_char,
                                               ellipsis_left=False)

                self._title_margin_left_str = f"{self.title_margin_char*self._title_text_margin_left}"
                self._title_margin_right_str = f"{self.title_margin_char*self._title_text_margin_right}"
                self._title_printing_from = self.width \
                                            -self._title_label_margin_right \
                                            -len(self._title_str) \
                                            -len(self._title_margin_left_str) \
                                            -len(self._title_margin_right_str)
                self._title_length = len(self._title_str)+self._title_text_margin_left+self._title_text_margin_right

            # centering
            else:
                title_len = max(self.width-1 \
                                -(self._title_text_margin_left+self._title_text_margin_right),0)

                self._title_str = truncate_str(self.title,
                                               length=title_len,
                                               ellipsis=self.ellipsis_char,
                                               ellipsis_left=False)

                self._title_margin_left_str = f"{self.title_margin_char*self._title_text_margin_left}"
                self._title_margin_right_str = f"{self.title_margin_char*self._title_text_margin_right}"
                self._title_printing_from = self.width//2 \
                                            -(len(self._title_str) \
                                              +self._title_text_margin_left \
                                              +self._title_text_margin_right)//2
                self._title_length = len(self._title_str)+self._title_text_margin_left+self._title_text_margin_right

    def show_title(self, title_style=None, margin_style=None, reset_style=False):
        if reset_style:
            self._title_style_history = self.default_style
            self._title_margin_style_history = self.default_style

        if title_style:
            self._title_style_history = title_style
        else:
            title_style = self._title_style_history

        if margin_style:
            margin_style = margin_style
            self._title_margin_style_history = margin_style
        else:
            margin_style = self._title_margin_style_history

        if self._title_pos:
            segs = [Segment(self._title_str,
                            style=margin_style,
                            cursor_begin_pos=self._title_pos)]
        else:
            segs = [Segment(self._title_margin_left_str,
                            style=margin_style,
                            cursor_begin_pos=(self.x+self._title_printing_from, self.y)),
                    Segment(self._title_str,
                            style=title_style),
                    Segment(self._title_margin_right_str,
                            style=margin_style)]

        self.term_mgr.add_to_buffer(segs)

    def hide_title(self, style=None, overwrite_char=None):
        ow_char =  overwrite_char if overwrite_char else " " if self._title_pos else self.border_horizontal
                
        if self._title_pos:
            if style is None:
                style = self.default_style

            seg = [Segment(ow_char*self._title_length,
                           style=style,
                           cursor_begin_pos=self._title_pos)]

        else:
            if style is None:
                style = self._border_style_history

            seg = [Segment(ow_char*self._title_length,
                           style=style,
                           cursor_begin_pos=(self.x+self._title_printing_from, self.y))]

        self.term_mgr.add_to_buffer(seg)

class Layout(DrawableArea):
    def __init__(self, _curses, name, x, y, width, height):
        super(Pane, self).__init__(x, y, width, height)

class Pane(DrawableArea):
    def __init__(self, _curses, name, x, y, width, height):
        super(Pane, self).__init__(x, y, width, height)

        self._curses = _curses

        self.widget = None

    def assign_widget(self, widget):
        self.widget = widget

    #def draw_boader_line(self):
    #    self.

    #def draw_content(self):
    #    self.

    def draw(self):
        if self.widget is not None:
            self.widget.draw(self._curses, self.x, self.y, self.width, self.height)

if __name__ == "__main__":
    import sys
    import time

    import keys
    import key_input

    #from pycui import TerminalManager, Segment, TextStyle

    #style = TerminalTheme(TextStyle((255),(0,10,80)))
    style = TerminalTheme(TextStyle())
    #tm = TerminalManager(TerminalTheme(TextStyle((255),(0,10,80))))
    tm = TerminalManager(style, use_alt_screen=False)
    tm.init()
    win = tm.new_window("test_window", 1, 2, 80, 30, margin=[1,1,1,1],
                        title_pos=None, title_label_margin=(None,None), title_text_margin=(1,1),
                        window_description="",
                        window_hook_name=None,
                        use_utf8=True)

    tm.add_window(Window(tm, "test_window2", 4, 4, 40, 15))
    tm.delete_window("test_window")

    print(tm.get_window_index("test_window2"))
    print(tm.get_window("test_window2"))


    reverse_style = TextStyle(styles=["REVERSE"])
    win.show_boader(TextStyle(196, 16))
    win.show_title(reverse_style)

    style = TextStyle((255,255,255), (120,20,220), ["BOLD", "UNDERLINE"])
    #sq = u" " + u''.join(map(_unich, range(0x258F, 0x2587, -1)))
    """
    2580    ▀   UPPER HALF BLOCK    
    2581    ▁   LOWER ONE EIGHTH BLOCK  
    2582    ▂   LOWER ONE QUARTER BLOCK 
    2583    ▃   LOWER THREE EIGHTHS BLOCK   
    2584    ▄   LOWER HALF BLOCK    
    2585    ▅   LOWER FIVE EIGHTHS BLOCK    
    2586    ▆   LOWER THREE QUARTERS BLOCK  
    2587    ▇   LOWER SEVEN EIGHTHS BLOCK   
    2588    █   FULL BLOCK
    2589    ▉   LEFT SEVEN EIGHTHS BLOCK    
    258A    ▊   LEFT THREE QUARTERS BLOCK   
    258B    ▋   LEFT FIVE EIGHTHS BLOCK 
    258C    ▌   LEFT HALF BLOCK 
    258D    ▍   LEFT THREE EIGHTHS BLOCK    
    258E    ▎   LEFT ONE QUARTER BLOCK  
    258F    ▏   LEFT ONE EIGHTH BLOCK   
    2590    ▐   RIGHT HALF BLOCK
    """

    if sys.stdout.encoding == "UTF-8":
        ch = "\u2588"
    else:
        ch = "#"

    # create 256 color table
    sgs = []
    sgs = sgs + [Segment(ch, TextStyle(  0), (2,  4))] + [Segment(ch, TextStyle(i)) for i in range(  1, 16)]

    sgs = sgs + [Segment(ch, TextStyle( 16), (2,  6))] + [Segment(ch, TextStyle(i)) for i in range( 17, 52)]
    sgs = sgs + [Segment(ch, TextStyle( 52), (2,  7))] + [Segment(ch, TextStyle(i)) for i in range( 53, 88)]
    sgs = sgs + [Segment(ch, TextStyle( 88), (2,  8))] + [Segment(ch, TextStyle(i)) for i in range( 89, 124)]
    sgs = sgs + [Segment(ch, TextStyle(124), (2,  9))] + [Segment(ch, TextStyle(i)) for i in range(125, 160)]
    sgs = sgs + [Segment(ch, TextStyle(160), (2, 10))] + [Segment(ch, TextStyle(i)) for i in range(161, 196)]
    sgs = sgs + [Segment(ch, TextStyle(196), (2, 11))] + [Segment(ch, TextStyle(i)) for i in range(197, 233)]
    
    sgs = sgs + [Segment(ch, TextStyle(233), (2, 13))] + [Segment(ch, TextStyle(i)) for i in range(234, 256)]

    tm.add_to_buffer(sgs)
    tm._render()

    k = key_input.KeyInput()
    while True:
        if k.kbhit():
            a = k.parse_key()

            if a == keys.key_codes["ARROW_UP"]:
                tm.move_cursor_up(1)
            elif a == keys.key_codes["ARROW_DOWN"]:
                tm.move_cursor_down(1)
            elif a == keys.key_codes["ARROW_RIGHT"]:
                tm.move_cursor_forward(1)
            elif a == keys.key_codes["ARROW_LEFT"]:
                tm.move_cursor_backward(1)
            elif a == keys.key_codes["ENTER"]:
                tm.move_cursor_down(1)
                tm.move_cursor_to_head()
            
            elif a == keys.key_codes["BACK_SPACE"]:
                tm.move_cursor_backward(1)
                tm.print(" ")
                tm.move_cursor_backward(1)

            elif a == keys.key_codes["A"]:
                win.show_boader(reverse_style)
                tm._render()
            elif a == keys.key_codes["S"]:
                win.hide_border()
                tm._render()
            elif a == keys.key_codes["R"]:
                win.show_boader(reset_style=True)
                tm._render()

            elif a == keys.key_codes["T"]:
                win.show_title()
                tm._render()

            elif a == keys.key_codes["Y"]:
                win.hide_title()
                tm._render()
            
            elif a == keys.key_codes["Q"]:
                break

            elif keys.is_printable(a):
                tm.print(chr(a))
            
            else:
                pass

        # https://www.typinglounge.com/worlds-fastest-typists
        # it says, "using stenotype machine, 360 wpm at 97% accuracy."
        # if we consider one word as 7 character, 42 char/s -> 23.8 c/ms
        # so at least sleeping 20ms will be enough, I hope.
        # parsing key input might take some time?
        time.sleep(0.01)
