from ht1632cpy import HT1632C


def spiral(color):
    dx = dy = 0
    count = 0
    x = y = 0
    while count < interface.width() * interface.height() + 50:
        for x in xrange(interface.width() - dx):
            interface.plot(x, y + dy, color)
            interface.sendframe()
            count += 1

        for y in xrange(interface.height() - dy):
            interface.plot(x, y, color)
            interface.sendframe()
            count += 1

        for x in xrange(interface.width() - dx, -1, -1):
            interface.plot(x, y, color)
            interface.sendframe()
            count += 1

        for y in xrange(interface.height() - dy, -1, -1):
            interface.plot(x + dx, y, color)
            interface.sendframe()
            count += 1
        dx += 1
        dy += 1

# Example will spiral the LEDs on from left to right, down and up through the colors
interface = HT1632C(2, 0)
interface.pwm(15)
interface.clear()

spiral(interface.GREEN)
spiral(interface.RED)
spiral(interface.ORANGE)
spiral(interface.BLACK)
