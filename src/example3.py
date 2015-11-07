import time

from ht1632c import HT1632C


def scroll_message(msg, color, bg):
    msg_length = len(msg) * interface.fontwidth(interface.font12x16)

    start = interface.width()
    end = -msg_length - 1

    for x in xrange(start, end, -1):
        interface.clear()
        interface.box(0, 0, interface.width(), interface.height(), bg)
        interface.putstr(x, 1, msg, interface.font12x16, color, bg)
        interface.sendframe()
        time.sleep(1/30.0)


# Example scrolls the message across the screen in different colors.
interface = HT1632C(2, 0)
interface.pwm(15)

message = "Hello World!"
scroll_message(message, interface.GREEN, interface.BLACK)
scroll_message(message, interface.RED, interface.GREEN)
scroll_message(message, interface.BLACK, interface.ORANGE)
interface.clear()
interface.sendframe()
