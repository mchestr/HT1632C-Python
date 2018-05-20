import time

from ht1632cpy import font_6x8, HT1632C


interface = HT1632C(2, 0)
interface.pwm(15)

try:
    message = "Hello World!"
    interface.putstr(0, 0, message, font_6x8, interface.GREEN, interface.BLACK)
    interface.sendframe()
    time.sleep(5)
    interface.clear()
    interface.putstr(0, 0, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(0, 8, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(8, 0, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(8, 8, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(16, 0, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(16, 8, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(24, 0, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.putstr(24, 8, ['smiley'], font_6x8, interface.RED, interface.BLACK)
    interface.sendframe()
    time.sleep(5)
finally:
    interface.clear()
    interface.sendframe()

