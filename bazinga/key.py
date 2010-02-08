from base.singleton import SingletonPool

import xcb.xproto

def keysym_to_keycode(keysym):


class Key(SingletonPool):

    def __init__(self, connection, modifiers, keysym):
        if isinstance(modifiers, basestring):
            # XXX add various format!
            pass
        else:
            self.modifiers = xcb.NONE
            if modifiers:
                for modifier in modifiers:
                    self.modifiers |= getattr(xcb.xproto.KeyButMask, modifier)

        if 
