from typing import Type, Union
from collections.abc import Callable
from abc import ABCMeta, abstractmethod

class TextStyle(object):
    style_codes = TerminalControlEscapeSequence.style_codes
    fg_color_codes = TerminalControlEscapeSequence.fg_color_codes
    bg_color_codes = TerminalControlEscapeSequence.bg_color_codes

    fg_256color2ces = TerminalControlEscapeSequence.fg_256color2ces
    bg_256color2ces = TerminalControlEscapeSequence.bg_256color2ces
    fg_rgb2ces = TerminalControlEscapeSequence.fg_rgb2ces
    bg_rgb2ces = TerminalControlEscapeSequence.bg_rgb2ces

    def __init__(self,
                 fg_color=TerminalControlEscapeSequence.default_color_name: Union[str, int, tuple[int, int, int]],
                 bg_color=TerminalControlEscapeSequence.default_color_name: Union[str, int, tuple[int, int, int]],
                 styles=[]: list[str]):
        """A class for 
        """

        self.fg_color = self._parse_color(fg_color, self.fg_color_codes, self.fg_256color2ces, self.fg_rgb2ces)
        self.bg_color = self._parse_color(bg_color, self.bg_color_codes, self.bg_256color2ces, self.bg_rgb2ces)
        self.styles = self._parse_style(styles)

        self.text_style_codes = self._build_style_code()

    def _parse_color(self,
                     col: Union[str, int, tuple[int, int, int]],
                     color_codes: dict[str, str],
                     color_rgb_f: Callable[[Union[str, int, tuple[int, int, int]]], str],
                     color_256_f: Callable[[Union[str, int, tuple[int, int, int]]], str]) -> str:
        # look up named color
        if isinstance(col, str):
            if col in color_codes:
                return color_codes[col]
            else:
                return color_codes[TerminalControlEscapeSequence.default_color_name]
        # 256 color, may not need max and min
        elif isinstance(col, int):
            return color_256_f(max(min(col, 255), 0))
        # rgb color, may not need max and min
        elif isinstance(col, tuple):
            return color_rgb_f(max(min(col[0], 255), 0), max(min(col[1], 255), 0), max(min(col[2], 255), 0))
        else:
            return color_codes[TerminalControlEscapeSequence.default_color_name]

    def _parse_style(self, styles: list[str])-> list[str]:
        return list(filter(lambda x: x.upper() in self.style_codes))

    def _build_style_code(self) -> str:
        # merge in one string
        # like "90;31;1;4;31"
        return f"{';'.join(filter(lambda x: x, [self.bg_color]+[self.fg_color]+self.styles))}"

class Segment(object):
    """Class for storing information of text printing.
    """

    self._gen_move_cursor_to_ces = TerminalControlEscapeSequence.control_functions["CURSOR_MOVE_TO"]

    self.csi_ces = TerminalControlEscapeSequence.control_codes["CSI"]
    self.clear_ces = TerminalControlEscapeSequence.control_codes["CSI"] \
                    +TerminalControlEscapeSequence.style_codes["END"] \
                    +TerminalControlEscapeSequence.style_end_code
    self.end_code = TerminalControlEscapeSequence.style_end_code

    def __init__(self,
                 text: str,
                 style: TextStyle,
                 cursor_begin_pos=None: tuple[int, int],
                 cursor_end_pos=None: tuple[int, int]):
        """
        """

        self.text = text
        self.style = style
        self.cursor_begin_pos = cursor_begin_pos
        self.cursor_end_pos = cursor_end_pos
        self._data = self._format_segment_to_text()

    def _format_segment_to_text(self) -> str:
        """
        NOTE:
            each styled text contains `self.clear_code` which might not needed.
        """
        
        # {self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}
        # should look like "\x1b[40;31;1;4mTEXT\x1b[0m"
        return (f"{self._gen_move_cursor_to_ces(*self.cursor_begin_pos) if self.cursor_begin_pos else ""}"
                +f"{self.csi_ces}{self.style.text_style_codes}{self.end_code}{self.text}{self.clear_ces}"
                +f"{self._gen_move_cursor_to_ces(*self.cursor_end_pos) if self.cursor_end_pos else ""}")

    def update(self, text=None, style=None, cursor_begin_pos=None, cursor_end_pos=None) -> None:
        if text: self.text = text
        if style: self.style = style
        if cursor_begin_pos: self.cursor_begin_pos = cursor_begin_pos
        if cursor_end_pos: self.cursor_end_pos = cursor_end_pos

        self._data = self._format_segment_to_text()

class SegmentArray(object):
    def __init__(self, segments: Union[Segment, list[Segment]]):
        if isinstance(segments, Segment):
            self.segments = [segments]
        else:
            self.segments = segments

    def __len__(self):
        return len(self.segments)

    def __add__(self, other: SegmentArray):
        return SegmentArray(self.segments+other.segments)

    def __sub__(self, other: SegmentArray):
        # return the segments which NOT contain in other.segments
        # it will filter only the same segment instance, so the case to use this might be very rare
        return SegmentArray(list(filter(lambda x: x not in other.segments, self.segments)))

# not need any more
class TextFormatter(object):
    """Class for formatting a text to apply color and style on screen.
    """

    self.csi_ces = TerminalControlEscapeSequence.control_codes["CSI"]
    self.clear_ces = (TerminalControlEscapeSequence.control_codes["CSI"]
                      + TerminalControlEscapeSequence.style_codes["END"]
                      + TerminalControlEscapeSequence.style_end_code
    )
    self.end_code = TerminalControlEscapeSequence.style_end_code

    def __init__(self, theme):
        self.theme = theme

    def format(self, text, style):
        """
        NOTE:
            each styled text contains `self.clear_code` which might not needed.
        """
        
        # {self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}
        # should look like "\x1b[40;31;1;4mTEXT\x1b[0m"
        if style:
            if isinstance(style, str):
                if style in self.theme.registered_styles:
                    style = self.theme.registered_styles[segment.style]
                    return f"{self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}"
                else:
                    return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

            elif isinstance(style, TextStyle):
                return f"{self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

            else:
                return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"
        else:
            return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

class Renderable(metaclass=ABCMeta):
    def __init__(self):
        self._rendering_data = None

    @property
    def rendering_data(self):
        return self._rendering_data

class Text(Renderable):
    def __init__(self, x: int, y: int, width: int, height: int, style: TextStyle, erase_style: TextStyle):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.style = style
        self.erase_style = erase_style

        self._build_text()
        self._rendering_line = self._gen_render_segment()

        self._build_boarder_erase_string()
        self._rendering_erasing = self._gen_render_erase_segment()

        self._rendering_data = self._rendering_line

    def _build_boarder_line_string(self):
        """
        """

        self._top_line_str = self.border_chars.up_left \
                            +self.border_chars.horizontal*(self.width-2) \
                            +self.border_chars.up_right

        self._bottom_line_str = self.border_chars.down_left \
                               +self.border_chars.horizontal*(self.width-2) \
                               +self.border_chars.down_right

    def _build_boarder_erase_string(self):
        """
        """

        self._top_line_erase_str = self.border_erase_chars.up_left \
                                  +self.border_erase_chars.horizontal*(self.width-2) \
                                  +self.border_erase_chars.up_right

        self._bottom_line_erase_str = self.border_erase_chars.down_left \
                                     +self.border_erase_chars.horizontal*(self.width-2) \
                                     +self.border_erase_chars.down_right

    def _gen_render_segment(self):
        segs = [Segment(self._top_line_str,
                        style=self.style,
                        cursor_begin_pos=(self.x, self.y))]

        # I am not sure using list comprehension is faster than normal for loop
        segs += [Segment(self.border_chars.vertical, style=self.style, cursor_begin_pos=(self.x, self.y+i))
                 for i in range(1, self.height-1)]
        segs += [Segment(self.border_chars.vertical, style=self.style, cursor_begin_pos=(self.x+self.width-1, self.y+i))
                 for i in range(1, self.height-1)]

        segs.append(Segment(self._bottom_line_str,
                            style=self.style,
                            cursor_begin_pos=(self.x, self.y+self.height-1)))

        return SegmentArray(segs)

    def _gen_render_erase_segment(self):
        segs = [Segment(self._top_line_erase_str,
                        style=self.erase_style,
                        cursor_begin_pos=(self.x, self.y))]

        # I am not sure using list comprehension is faster than normal for loop
        segs += [Segment(self.border_erase_chars.vertical, style=self.erase_style, cursor_begin_pos=(self.x, self.y+i))
                 for i in range(1, self.height-1)]
        segs += [Segment(self.border_erase_chars.vertical, style=self.erase_style, cursor_begin_pos=(self.x+self.width-1, self.y+i))
                 for i in range(1, self.height-1)]

        segs.append(Segment(self._bottom_line_erase_str,
                            style=self.erase_style,
                            cursor_begin_pos=(self.x, self.y+self.height-1)))

        return SegmentArray(segs)

    def _update(self):
        # calling this might be slow for just changing some value.

        self._build_boarder_line_string()
        self._rendering_line = self._gen_render_segment()

        self._build_boarder_erase_string()
        self._rendering_erasing = self._gen_render_erase_segment()

    def update(self, text=None, x=None, y=None, width=None, height=None, style=None, erase_style=None):
        """
            update the border line content with given values
        """

        if x: self.x = x
        if y: self.y = y
        if width: self.width = width
        if height: self.height = height
        if style: self.style = style
        if border_chars: self.border_chars = border_chars
        if style: self.erase_style = erase_style
        if border_chars: self.border_erase_chars = border_erase_chars

        self._update()

    def set_draw(self):
        self._rendering_data = self._rendering_line

    def set_erase(self):
        self._rendering_data = self._rendering_erasing

class BorderLine(Renderable):
    def __init__(self, x, y, width, height, style, border_chars, erase_style, border_erase_chars):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.style = style
        self.border_chars = border_chars
        self.erase_style = erase_style
        self.border_erase_chars = border_erase_chars

        self._build_boarder_line_string()
        self._rendering_line = self._gen_render_segment()

        self._build_boarder_erase_string()
        self._rendering_erasing = self._gen_render_erase_segment()

        self._rendering_data = self._rendering_line

    def _build_boarder_line_string(self):
        """
        """

        self._top_line_str = self.border_chars.up_left \
                            +self.border_chars.horizontal*(self.width-2) \
                            +self.border_chars.up_right

        self._bottom_line_str = self.border_chars.down_left \
                               +self.border_chars.horizontal*(self.width-2) \
                               +self.border_chars.down_right

    def _build_boarder_erase_string(self):
        """
        """

        self._top_line_erase_str = self.border_erase_chars.up_left \
                                  +self.border_erase_chars.horizontal*(self.width-2) \
                                  +self.border_erase_chars.up_right

        self._bottom_line_erase_str = self.border_erase_chars.down_left \
                                     +self.border_erase_chars.horizontal*(self.width-2) \
                                     +self.border_erase_chars.down_right

    def _gen_render_segment(self):
        segs = [Segment(self._top_line_str,
                        style=self.style,
                        cursor_begin_pos=(self.x, self.y))]

        # I am not sure using list comprehension is faster than normal for loop
        segs += [Segment(self.border_chars.vertical, style=self.style, cursor_begin_pos=(self.x, self.y+i))
                 for i in range(1, self.height-1)]
        segs += [Segment(self.border_chars.vertical, style=self.style, cursor_begin_pos=(self.x+self.width-1, self.y+i))
                 for i in range(1, self.height-1)]

        segs.append(Segment(self._bottom_line_str,
                            style=self.style,
                            cursor_begin_pos=(self.x, self.y+self.height-1)))

        return SegmentArray(segs)

    def _gen_render_erase_segment(self):
        segs = [Segment(self._top_line_erase_str,
                        style=self.erase_style,
                        cursor_begin_pos=(self.x, self.y))]

        # I am not sure using list comprehension is faster than normal for loop
        segs += [Segment(self.border_erase_chars.vertical, style=self.erase_style, cursor_begin_pos=(self.x, self.y+i))
                 for i in range(1, self.height-1)]
        segs += [Segment(self.border_erase_chars.vertical, style=self.erase_style, cursor_begin_pos=(self.x+self.width-1, self.y+i))
                 for i in range(1, self.height-1)]

        segs.append(Segment(self._bottom_line_erase_str,
                            style=self.erase_style,
                            cursor_begin_pos=(self.x, self.y+self.height-1)))

        return SegmentArray(segs)

    def _update(self):
        # calling this might be slow for just changing some value.

        self._build_boarder_line_string()
        self._rendering_line = self._gen_render_segment()

        self._build_boarder_erase_string()
        self._rendering_erasing = self._gen_render_erase_segment()

    def update(self, x=None, y=None, width=None, height=None,
                     style=None, border_chars=None, erase_style=None, border_erase_chars=None):
        """
            update the border line content with given values
        """

        if x: self.x = x
        if y: self.y = y
        if width: self.width = width
        if height: self.height = height
        if style: self.style = style
        if border_chars: self.border_chars = border_chars
        if style: self.erase_style = erase_style
        if border_chars: self.border_erase_chars = border_erase_chars

        self._update()

    def set_draw(self):
        self._rendering_data = self._rendering_line

    def set_erase(self):
        self._rendering_data = self._rendering_erasing

class Renderer(object):
    def __init__(self, theme, output):
        self.theme = theme
        
        self._render_queue = []

        # printing target
        self.output = output

    def _setup_control_functions(self):
        """
        NOTE:
            if wrapping a functon to _gen_*_ces cause speed issue, we should implement in native function,
            and create a TerminalManager for each terminal/environment.

            this is for capability of switching the control escape sequence to different easily,
            and for reducing unwated `flush()` call to the screen/system.

            We can think using option flush=True, if-statement may be harmful for speed.
        """

        self.csi_ces = TerminalControlEscapeSequence.control_codes["CSI"]
        self.clear_ces = TerminalControlEscapeSequence.control_codes["CSI"] \
                        +TerminalControlEscapeSequence.style_codes["END"] \
                        +TerminalControlEscapeSequence.style_end_code
        self.end_code = TerminalControlEscapeSequence.style_end_code

    def _format_segment_to_text(self, segment) -> str:
        """
        NOTE:
            each styled text contains `self.clear_code` which might not needed.
        """

        text = segment.text
        style = segment.style
        
        # {self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}
        # should look like "\x1b[40;31;1;4mTEXT\x1b[0m"
        if style:
            if isinstance(style, str):
                if style in self.theme.registered_styles:
                    style = self.theme.registered_styles[style]
                    return f"{self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}"
                else:
                    return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

            elif isinstance(style, TextStyle):
                return f"{self.csi_ces}{style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

            else:
                return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"
        else:
            return f"{self.csi_ces}{self.theme.default_style.text_style_codes}{self.end_code}{text}{self.clear_ces}"

    def _render(self) -> None:
        for r_obj in self._render_queue:
            for seg in r_obj.rendering_data:
                # might consider to use if statement whether or not for the speed
                if seg.cursor_begin_pos:
                    self.output.write(self._gen_move_cursor_to_ces(*seg.cursor_begin_pos))

                self.output.write(self._format_segment_to_text(seg))

                if seg.cursor_end_pos:
                    self.output.write(self._gen_move_cursor_to_ces(*seg.cursor_end_pos))

        self.output.flush()
        
        self._render_queue = []

    def process(self) -> None:
        self._render()

    def flush(self) -> None:
        self.output.flush()

    def push(self, render_obj: Type[Renderable]) -> None:
        self._render_queue.append(render_obj)
