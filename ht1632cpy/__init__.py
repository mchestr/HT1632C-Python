import os
import struct

import wiringpi


class HT1632C(object):
    ID_LEN = 3
    ID_CMD = 4  # send cmd
    ID_WR = 5  # write RAM
    ID_RD = 6  # read RAM

    CS_NONE = 0x00
    CS_ALL = 0xff

    CMD_SYSDIS = 0x00  # CMD= 0000-0000-x Turn off oscil
    CMD_SYSON = 0x01  # CMD= 0000-0001-x Enable system oscil
    CMD_LEDOFF = 0x02  # CMD= 0000-0010-x LED duty cycle gen off
    CMD_LEDON = 0x03  # CMD= 0000-0011-x LEDs ON
    CMD_BLOFF = 0x08  # CMD= 0000-1000-x Blink ON
    CMD_BLON = 0x09  # CMD= 0000-1001-x Blink Off
    CMD_SLVMD = 0x10  # CMD= 0001-00xx-x Slave Mode
    CMD_MSTMD = 0x14  # CMD= 0001-01xx-x Master Mode
    CMD_RCCLK = 0x18  # CMD= 0001-10xx-x Use on-chip clock
    CMD_EXTCLK = 0x1C  # CMD= 0001-11xx-x Use external clock
    CMD_COMS00 = 0x20  # CMD= 0010-ABxx-x commons options
    CMD_COMS01 = 0x24  # CMD= 0010-ABxx-x commons options
    CMD_COMS10 = 0x28  # CMD= 0010-ABxx-x commons options
    CMD_COMS11 = 0x2C  # CMD= 0010-ABxx-x commons options
    CMD_PWM = 0xA0  # CMD= 101x-PPPP-x PWM duty cycle

    def __init__(self, panels, rotation, lock_id=0, clk_delay=10, spi_freq=2560000, clk_pin=10, cs_pin=11,
                 chips_per_panel=4):
        self.__panels = panels
        self.__rotation = rotation
        self.__lock_id = lock_id
        self.__clk_delay = clk_delay
        self.__spi_freq = spi_freq
        self.__num_chips = panels * chips_per_panel

        self.__clk_pin = clk_pin
        self.__cs_pin = cs_pin

        wiringpi.wiringPiSetup()
        self.__spi_fd = wiringpi.wiringPiSPISetup(0, spi_freq)

        # set CLK and CS pins to OUTPUT and low
        wiringpi.pinMode(self.__clk_pin, wiringpi.OUTPUT)
        wiringpi.pinMode(self.__cs_pin, wiringpi.OUTPUT)
        wiringpi.digitalWrite(self.__clk_pin, wiringpi.LOW)
        wiringpi.digitalWrite(self.__cs_pin, wiringpi.LOW)

        self.command(self.CS_ALL, self.CMD_SYSDIS)
        self.command(self.CS_ALL, self.CMD_COMS00)
        self.command(self.CS_ALL, self.CMD_MSTMD)
        self.command(self.CS_ALL, self.CMD_RCCLK)
        self.command(self.CS_ALL, self.CMD_SYSON)
        self.command(self.CS_ALL, self.CMD_LEDON)
        self.command(self.CS_ALL, self.CMD_BLOFF)
        self.command(self.CS_ALL, self.CMD_PWM)

    def _chip_select(self, cs):
        if cs == self.CS_ALL:
            wiringpi.digitalWrite(self.__cs_pin, wiringpi.LOW)
            self._clk(self.__num_chips)
        elif cs == self.CS_NONE:
            wiringpi.digitalWrite(self.__cs_pin, wiringpi.HIGH)
            self._clk(self.__num_chips)
        else:
            wiringpi.digitalWrite(self.__cs_pin, wiringpi.LOW)
            self._clk(1)
            wiringpi.digitalWrite(self.__cs_pin, wiringpi.HIGH)
            self._clk(cs - 1)

    def _clk(self, pulses):
        for i in range(pulses):
            wiringpi.digitalWrite(self.__clk_pin, wiringpi.HIGH)
            wiringpi.delayMicroseconds(self.__clk_delay)
            wiringpi.digitalWrite(self.__clk_pin, wiringpi.LOW)
            wiringpi.delayMicroseconds(self.__clk_delay)

    def _send(self, data):
        return os.write(self.__spi_fd, data)

    def command(self, cs, cmd):
        data = ((self.ID_CMD << 8) | cmd) << 5
        wiringpi.piLock(self.__lock_id)
        try:
            self._chip_select(cs)
            self._send(struct.pack('>H', data))
            self._chip_select(self.CS_NONE)
        finally:
            wiringpi.piUnlock(self.__lock_id)

    def clear(self):
        wiringpi.piLock(self.__lock_id)
        try:
            for chip in range(self.__num_chips):
                self._chip_select(chip + 1)
                data = bytes([self.ID_WR << (8 - self.ID_LEN), 0x00] + [0x00] * 32)
                self._send(data)
                self._chip_select(self.CS_NONE)
        finally:
            wiringpi.piUnlock(self.__lock_id)

    def close(self):
        os.close(self.__spi_fd)

    def pwm(self, value):
        self.command(self.CS_ALL, self.CMD_PWM | (value & 0x0f))
