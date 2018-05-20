import logging

LOG = logging.getLogger(__name__)


class PyFontHelper(object):

    def __init__(self, ht1632c):
        self._ht1632c = ht1632c

    # class to allow defining fonts in python versus having to do it in C
    def putchar(self, x, y, c, font, color, bg):
        char = font.get(c)
        if c is None:
            LOG.warning("character '%s' not found in font bitmap", c)
            return

        for _x, char_led_map in enumerate(char):
            line_bitmap = format(char_led_map, '0>8b')
            for _y, led in enumerate(line_bitmap):
                self._ht1632c.plot(x + _x, y + _y, color if led == '1' else bg)

    def putstr(self, x, y, s, font, color, bg):
        x_offset = x
        for index, char in enumerate(s):
            char_width = self.charwidth(char, font)
            self.putchar(x_offset, y, char, font, color, bg)
            x_offset += char_width + 1

    def charwidth(self, c, font):
        width = 0
        char_bitmap = font.get(c)
        if c is None:
            LOG.warning("character '%s' not found in font bitmap", c)
            return width
        return len(char_bitmap)
