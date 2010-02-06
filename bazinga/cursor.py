# vim: set fileencoding=utf-8

from base.property import cachedproperty
from x import XObject
from color import Color


_name_to_id = {
    "num_glyphs": 154,
    "X_cursor": 0,
    "arrow": 2,
    "based_arrow_down": 4,
    "based_arrow_up": 6,
    "boat": 8,
    "bogosity": 10,
    "bottom_left_corner": 12,
    "bottom_right_corner": 14,
    "bottom_side": 16,
    "bottom_tee": 18,
    "box_spiral": 20,
    "center_ptr": 22,
    "circle": 24,
    "clock": 26,
    "coffee_mug": 28,
    "cross": 30,
    "cross_reverse": 32,
    "crosshair": 34,
    "diamond_cross": 36,
    "dot": 38,
    "dotbox": 40,
    "double_arrow": 42,
    "draft_large": 44,
    "draft_small": 46,
    "draped_box": 48,
    "exchange": 50,
    "fleur": 52,
    "gobbler": 54,
    "gumby": 56,
    "hand1": 58,
    "hand2": 60,
    "heart": 62,
    "icon": 64,
    "iron_cross": 66,
    "left_ptr": 68,
    "left_side": 70,
    "left_tee": 72,
    "leftbutton": 74,
    "ll_angle": 76,
    "lr_angle": 78,
    "man": 80,
    "middlebutton": 82,
    "mouse": 84,
    "pencil": 86,
    "pirate": 88,
    "plus": 90,
    "question_arrow": 92,
    "right_ptr": 94,
    "right_side": 96,
    "right_tee": 98,
    "rightbutton": 100,
    "rtl_logo": 102,
    "sailboat": 104,
    "sb_down_arrow": 106,
    "sb_h_double_arrow": 108,
    "sb_left_arrow": 110,
    "sb_right_arrow": 112,
    "sb_up_arrow": 114,
    "sb_v_double_arrow": 116,
    "shuttle": 118,
    "sizing": 120,
    "spider": 122,
    "spraycan": 124,
    "star": 126,
    "target": 128,
    "tcross": 130,
    "top_left_arrow": 132,
    "top_left_corner": 134,
    "top_right_corner": 136,
    "top_side": 138,
    "top_tee": 140,
    "trek": 142,
    "ul_angle": 144,
    "umbrella": 146,
    "ur_angle": 148,
    "watch": 150,
    "xterm": 152,
}


# XXX make font an X object
#_fonts = weakref.WeakValueDictionary()
_font = None


class XCursor(XObject):
    """A X cursor."""

    # This is defined in some X header file…
    _font_name = "cursor"
    _font = None


    class foreground(cachedproperty):
        def __get__(self):
            # Should not happen
            raise AttributeError

        def __delete__(self):
            raise AttributeError

        def __set__(self, value):
            color = Color(self.connection, self.colormap, value)
            self.connection.core.RecolorCursorChecked(self,
                                                      color.red,
                                                      color.green,
                                                      color.blue,
                                                      self.background.red,
                                                      self.background.green,
                                                      self.background.blue).check()
            return color

    class background(cachedproperty):
        def __get__(self):
            # Should not happen
            raise AttributeError

        def __delete__(self):
            raise AttributeError

        def __set__(self, value):
            color = Color(self.connection, self.colormap, value)
            self.connection.core.RecolorCursorChecked(self,
                                                      self.foreground.red,
                                                      self.foreground.green,
                                                      self.foreground.blue,
                                                      color.red,
                                                      color.green,
                                                      color.blue).check()

            return color

    @classmethod
    def create(cls, connection, colormap, value, foreground="black", background="white"):
        if isinstance(value, XCursor):
            return value

        # Initialize font is never done before
        if cls._font is None:
            cls._font = connection.generate_id()
            connection.core.OpenFont(cls._font, len(cls._font_name), cls._font_name)

        try:
            cursor_id = _name_to_id[value]
        except KeyError:
            raise ValueError("No such cursor.")

        cursor = super(XCursor, cls).create(connection)

        foreground = Color(connection, colormap, foreground)
        background = Color(connection, colormap, background)

        cg = cursor.connection.core.CreateGlyphCursorChecked(cursor,
                                                             cls._font, cls._font,
                                                             cursor_id, cursor_id + 1,
                                                             foreground.red,
                                                             foreground.green,
                                                             foreground.blue,
                                                             background.red,
                                                             background.green,
                                                             background.blue)

        Cursor.foreground.set_cache(cursor, foreground)
        Cursor.background.set_cache(cursor, background)
        cursor.name = value
        cursor.colormap = colormap

        cg.check()

        return cursor

    def __str__(self):
        return self.name


class Cursor(XCursor):
    def __del__(self):
        self.connection.core.FreeCursor(self)
