from ht1632cpy import HT1632C
import time


# Example turns on LEDs and cycles through the colors.
interface = HT1632C(2, 0)
interface.pwm(15)
interface.clear()

# interface.add(0xfffffffffffffffffff00000000000000000000000000000000000000000000000)
# interface.send_frame()

# all orange
interface.add(0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff)
interface.send_frame()

time.sleep(3)

# all green
interface.add(0xfffffffffffffffffffffffffffffff00000000000000000000000000000000f)
interface.send_frame()

time.sleep(3)

# all red
interface.add(0x0000000000000000000000000000000ffffffffffffffffffffffffffffffff0)
interface.send_frame()

time.sleep(3)

interface.add(0x000000000000000000000000000000000000000000000000000000000000000f)
interface.send_frame()

# 0xfffffffffffffffffff00000000000000000000000000000000000000000000000
# 0x0000000000000000000fffffffffffffffffff0000000000000000000000000000
# 0xfffffffffffffffffffffffffffffffffff0000000000000000000000000000000  # All Green
# 0x00000000000000000000000000000000000000ffffffffffffffffffffffffffffffff  # All Red
# 0xfffffffffffffffffffffffffffffffffff000fffffffffffffffffffffffffffff

# # Green
# print("GREEN")
# interface.box(0, 0, interface.width(), interface.height(), interface.GREEN)
# interface.sendframe()
# time.sleep(3)
#
# # Red
# print("RED")
# interface.box(0, 0, interface.width(), interface.height(), interface.RED)
# interface.sendframe()
# time.sleep(3)
#
# # Orange
# print("ORANGE")
# interface.box(0, 0, interface.width(), interface.height(), interface.ORANGE)
# interface.sendframe()
# time.sleep(3)
#
# # Black
# print("BLACK")
# interface.box(0, 0, interface.width(), interface.height(), interface.BLACK)
# interface.sendframe()
