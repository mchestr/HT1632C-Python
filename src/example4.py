import datetime
import time

from ht1632c import HT1632C


interface = HT1632C(2, 0)
interface.pwm(15)


def clock():
    now = datetime.datetime.now()
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)
    interface.clear()

    x = 5
    dividers = 2
    for section in (hour, minute, second):
        for c in section:
            interface.putchar(x, 4, c, interface.font7x8num, interface.GREEN, interface.BLACK)
            x += interface.fontwidth(interface.font7x8num)
        if dividers > 0:
            interface.putchar(x, 4, ':', interface.font6x8, interface.GREEN, interface.BLACK)
            x += interface.fontwidth(interface.font6x8) - 1
            dividers -= 1
    interface.sendframe()

# Displays a 24h clock across 2 16x32 LED boards
while True:
    clock()
    time.sleep(0.5)
