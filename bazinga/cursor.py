# vim: set fileencoding=utf-8

from base.object import Object
from base.property import cachedproperty
from base.singleton import SingletonPool
from color import Color

# This is defined in some X header file…
_font_name = "cursor"

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

class XCursor(Object, SingletonPool):
    """Pointer cursor."""

    _font = None

    class foreground(cachedproperty):
        def __get__(self):
            # Should not happen
            raise AttributeError

        def __delete__(self):
            raise AttributeError

        def __set__(self, value):
            from x import MainConnection
            color = Color(self.colormap, value)
            MainConnection().core.RecolorCursorChecked(self.xid,
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
            from x import MainConnection
            color = Color(self.colormap, value)
            MainConnection().core.RecolorCursorChecked(self.xid,
                                                       self.foreground.red,
                                                       self.foreground.green,
                                                       self.foreground.blue,
                                                       color.red,
                                                       color.green,
                                                       color.blue).check()

            return color

    def __init__(self, colormap, name, foreground, background):
        from x import MainConnection
        # Initialize font is never done before
        if XCursor._font is None:
            XCursor._font = MainConnection().generate_id()
            MainConnection().core.OpenFont(XCursor._font, len(_font_name), _font_name)

        try:
            cursor_id = _name_to_id[name]
        except KeyError:
            raise ValueError("No such cursor.")

        XCursor.foreground.set_cache(self, Color(colormap, foreground))
        XCursor.background.set_cache(self, Color(colormap, background))

        xid = MainConnection().generate_id()
        cg = MainConnection().core.CreateGlyphCursorChecked(xid,
                                                            XCursor._font, XCursor._font,
                                                            cursor_id, cursor_id + 1,
                                                            self.foreground.red,
                                                            self.foreground.green,
                                                            self.foreground.blue,
                                                            self.background.red,
                                                            self.background.green,
                                                            self.background.blue)
        self.name = name
        self.colormap = colormap
        cg.check()
        # Do this last, so we do not try to FreeCursor if check fail
        self.xid = xid

    def __str__(self):
        return self.name

    # This is not possible:
    # Cursor().xid will free xid...
    # We need an xid object for that :-)
    #def __del__(self):
    #    if hasattr(self, "xid"):
    #        from x import MainConnection
    #        MainConnection().core.FreeCursor(self.xid)


def Cursor(colormap, value, foreground="black", background="white"):
    if isinstance(value, XCursor):
        return value
    return XCursor(colormap, value, foreground, background)
