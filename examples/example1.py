import time

from ht1632cpy import HT1632C


# Example turns on LEDs and cycles through the colors.
interface = HT1632C(2, 0)
interface.pwm(15)

# Green
print "GREEN"
interface.box(0, 0, interface.width(), interface.height(), interface.GREEN)
interface.sendframe()
time.sleep(3)

# Red
print "RED"
interface.box(0, 0, interface.width(), interface.height(), interface.RED)
interface.sendframe()
time.sleep(3)

# Orange
print "ORANGE"
interface.box(0, 0, interface.width(), interface.height(), interface.ORANGE)
interface.sendframe()
time.sleep(3)

# Black
print "BLACK"
interface.box(0, 0, interface.width(), interface.height(), interface.BLACK)
interface.sendframe()
