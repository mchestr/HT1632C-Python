# -*- coding: utf-8 -*-
import logging
import os
from ctypes import *

from ht1632cpy import font_helper

LOG = logging.getLogger(__name__)


# utility
def _encode_str(s):
    return c_char_p(s.encode("cp437", "ignore"))


class HT1632C(object):

    BLACK = 0
    GREEN = 1
    RED = 2
    ORANGE = 3
    TRANSPARENT = 0xff

    def __init__(self, num_panels, rotation):
        temp = os.path.abspath(__file__)
        temp = os.path.realpath(temp)
        temp = os.path.dirname(temp)
        temp = os.path.join(temp, "../ht1632c.so")
        self.lib = CDLL(temp)

        self.lib.ht1632c_init.argtypes = [c_int, c_int]
        self.lib.ht1632c_init.restype = c_int
        self.lib.ht1632c_close.argtypes = []
        self.lib.ht1632c_close.restype = None
        self.lib.ht1632c_peek.argtypes = [c_int, c_int]
        self.lib.ht1632c_peek.restype = c_int
        self.lib.ht1632c_pwm.argtypes = [c_byte]
        self.lib.ht1632c_pwm.restype = None
        self.lib.ht1632c_clip.argtypes = [c_int, c_int, c_int, c_int]
        self.lib.ht1632c_clip.restype = None
        self.lib.ht1632c_plot.argtypes = [c_int, c_int, c_byte]
        self.lib.ht1632c_plot.restype = None
        self.lib.ht1632c_line.argtypes = [c_int, c_int, c_int, c_int, c_byte]
        self.lib.ht1632c_line.restype = None
        self.lib.ht1632c_box.argtypes = [c_int, c_int, c_int, c_int, c_byte]
        self.lib.ht1632c_box.restype = None
        self.lib.ht1632c_putchar.argtypes = [c_int, c_int, c_char, c_void_p, c_byte, c_byte]
        self.lib.ht1632c_putchar.restype = c_int
        self.lib.ht1632c_putchar_metric.argtypes = [c_int, c_int, c_char, c_void_p, c_byte, c_byte]
        self.lib.ht1632c_putchar_metric.restype = c_int
        self.lib.ht1632c_putstr.argtypes = [c_int, c_int, c_char_p, c_void_p, c_byte, c_byte]
        self.lib.ht1632c_putstr.restype = c_int
        self.lib.ht1632c_putstr_metric.argtypes = [c_int, c_int, c_char_p, c_void_p, c_byte, c_byte]
        self.lib.ht1632c_putstr_metric.restype = c_int
        self.lib.ht1632c_charwidth.argtypes = [c_char, c_void_p]
        self.lib.ht1632c_charwidth.restype = c_int
        self.lib.ht1632c_strwidth.argtypes = [c_char_p, c_void_p]
        self.lib.ht1632c_strwidth.restype = c_int
        self.lib.ht1632c_fontwidth.argtypes = [c_void_p]
        self.lib.ht1632c_fontwidth.restype = c_int
        self.lib.ht1632c_fontheight.argtypes = [c_void_p]
        self.lib.ht1632c_fontheight.restype = c_int

        LOG.info("Initializing HT1632C")
        if self.lib.ht1632c_init(num_panels, rotation) != 0:
            raise IOError("Could not init display")

        self.font3x4num = self.lib.font_3x4_num
        self.font4x5num = self.lib.font_4x5_num
        self.font7x8num = self.lib.font_7x8_num
        self.font4x6 = self.lib.font_4x6
        self.font5x8 = self.lib.font_5x8
        self.font6x8 = self.lib.font_6x8
        self.font7x12 = self.lib.font_7x12
        self.font8x12 = self.lib.font_8x12
        self.font12x16 = self.lib.font_12x16
        self.font4x6sym = self.lib.font_4x6_sym

        self.pyfont = font_helper.PyFontHelper(self)

    def close(self):
        self.lib.ht1632c_close()

    def pwm(self, value):
        self.lib.ht1632c_pwm(value)

    def sendframe(self):
        self.lib.ht1632c_sendframe()

    def clear(self):
        self.lib.ht1632c_clear()

    def width(self):
        return self.lib.ht1632c_width()

    def height(self):
        return self.lib.ht1632c_height()

    def peek(self, x, y):
        return self.lib.ht1632c_peek(x, y)

    def clip(self, x0, y0, x1, y1):
        self.lib.ht1632c_clip(x0, y0, x1, y1)

    def plot(self, x, y, color):
        self.lib.ht1632c_plot(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        self.lib.ht1632c_line(x0, y0, x1, y1, color)

    def box(self, x0, y0, x1, y1, color):
        self.lib.ht1632c_box(x0, y0, x1, y1, color)

    def putchar(self, x, y, c, font, color, bg):
        if hasattr(font, 'get'):
            return self.pyfont.putchar(x, y, c, font, color, bg)
        return self.lib.ht1632c_putchar(x, y, c, font, color, bg)

    def putchar_metric(self, x, y, c, font, color, bg):
        return self.lib.ht1632c_putchar_metric(x, y, c, font, color, bg)

    def putstr(self, x, y, s, font, color, bg):
        if hasattr(font, 'get'):
            return self.pyfont.putstr(x, y, s, font, color, bg)
        return self.lib.ht1632c_putstr(x, y, _encode_str(s), font, color, bg)

    def putstr_metric(self, x, y, s, font, color, bg):
        return self.lib.ht1632c_putstr_metric(x, y, _encode_str(s), font, color, bg)

    def charwidth(self, c, font):
        if hasattr(font, 'get'):
            return self.pyfont.charwidth(c, font)
        return self.lib.ht1632c_charwidth(c, font)

    def strwidth(self, s, font):
        return self.lib.ht1632c_strwidth(_encode_str(s), font)

    def fontwidth(self, font):
        return self.lib.ht1632c_fontwidth(font)

    def fontheight(self, font):
        return self.lib.ht1632c_fontheight(font)

    def ledon(self):
        self.lib.ht1632c_ledon()

    def ledoff(self):
        self.lib.ht1632c_ledoff()

    def blinkon(self):
        self.lib.ht1632c_blon()

    def blinkoff(self):
        self.lib.ht1632c_bloff()
