import functools
import os
import struct

import wiringpi


def locked(lock_id):
    """Decorator to lock resource before calling function
    :param lock_id: ID of the lock
    """
    def on_decorate(func):
        @functools.wraps(func)
        def on_call(*args, **kwargs):
            wiringpi.piLock(lock_id)
            try:
                return func(*args, **kwargs)
            finally:
                wiringpi.piUnlock(lock_id)
        return on_call
    return on_decorate


class HT1632C(object):
    LOCK_ID = 0

    ID_LEN = 3
    ID_CMD = 4  # send cmd
    ID_WR = 5  # write RAM
    ID_RD = 6  # read RAM

    CS_NONE = 0x00
    CS_ALL = 0xff

    CMD_SYSDIS = 0x00  # 0000-0000-x Turn off oscil
    CMD_SYSON = 0x01  # 0000-0001-x Enable system oscil
    CMD_LEDOFF = 0x02  # 0000-0010-x LED duty cycle gen off
    CMD_LEDON = 0x03  # 0000-0011-x LEDs ON
    CMD_BLOFF = 0x08  # 0000-1000-x Blink ON
    CMD_BLON = 0x09  # 0000-1001-x Blink Off
    CMD_SLVMD = 0x10  # 0001-00xx-x Slave Mode
    CMD_MSTMD = 0x14  # 0001-01xx-x Master Mode
    CMD_RCCLK = 0x18  # 0001-10xx-x Use on-chip clock
    CMD_EXTCLK = 0x1C  # 0001-11xx-x Use external clock
    CMD_COMS00 = 0x20  # 0010-ABxx-x commons options
    CMD_COMS01 = 0x24  # 0010-ABxx-x commons options
    CMD_COMS10 = 0x28  # 0010-ABxx-x commons options
    CMD_COMS11 = 0x2C  # 0010-ABxx-x commons options
    CMD_PWM = 0xA0  # 101x-PPPP-x PWM duty cycle

    def __init__(self, panels: int, rotation: int, clk_delay: int = 10,
                 clk_pin: int = 10, cs_pin: int = 11, chips_per_panel: int = 4,
                 panel_width: int = 32, panel_height: int = 16,
                 chip_width: int = 16, chip_height: int = 8, colors: int = 2):
        """Initialize HT1632C Panels using SPI and chained chip select
        :param panels: number of panels
        :param rotation: rotation of panels
        :param clk_delay: delay between clock pulses in microseconds
        :param clk_pin: wiringPi clock pin (CE0)
        :param cs_pin: wiringPi clock (CE1)
        :param chips_per_panel: number of HT1632C chips per panel
        :param panel_width: width of a single panel in pixels
        :param panel_height: height of a single panel in pixels
        :param chip_width: width in pixels an HT1632C chip controls
        :param chip_height: height in pixels an HT1632C chip controls
        :param colors: number of distinct colors per pixel
        """
        self.__clk_delay = clk_delay
        self.__spi_freq = 2560000
        self.__clk_pin = clk_pin
        self.__cs_pin = cs_pin

        self.__panels = panels
        self.__rotation = rotation % 3
        self.__num_chips = panels * chips_per_panel
        self.__panel_height = panel_height
        self.__panel_width = panel_width
        self.__chip_width = chip_width
        self.__chip_height = chip_height
        self.__colors = colors

        color_size = self.__chip_width * self.__chip_height // 8
        self.__chip_size = color_size * self.__colors
        self.__frame_buffer = [0 for _ in range(self.__num_chips)]

        # calculate this once, to be or'd with each chip data
        self.__wr_cmd = self.ID_WR << (self.__chip_size * 8 + 13)
        print('wr:', self.__wr_cmd)

        wiringpi.wiringPiSetup()
        self.__spi_fd = wiringpi.wiringPiSPISetup(0, self.__spi_freq)

        # set CLK and CS pins to OUTPUT and low
        wiringpi.pinMode(self.__clk_pin, wiringpi.OUTPUT)
        wiringpi.pinMode(self.__cs_pin, wiringpi.OUTPUT)
        wiringpi.digitalWrite(self.__clk_pin, wiringpi.LOW)
        wiringpi.digitalWrite(self.__cs_pin, wiringpi.LOW)

        self.command(self.CS_ALL, self.CMD_SYSDIS)
        self.command(self.CS_ALL, self.CMD_COMS00 if chip_height <= 8 else self.CMD_COMS01)
        self.command(self.CS_ALL, self.CMD_MSTMD)
        self.command(self.CS_ALL, self.CMD_RCCLK)
        self.command(self.CS_ALL, self.CMD_SYSON)
        self.command(self.CS_ALL, self.CMD_LEDON)
        self.command(self.CS_ALL, self.CMD_BLOFF)
        self.command(self.CS_ALL, self.CMD_PWM)

    def _clear_frame_buffer(self):
        for i in range(self.__num_chips):
            self.__frame_buffer[i] = 0

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

    @property
    def height(self):
        """Returns height of display"""
        return self.__panel_height

    @property
    def width(self):
        """Returns width of display"""
        return self.__panel_width

    def blink(self, on: bool):
        """Turn BLINK on/off for display
        :param on: boolean indicating whether blink is on or off
        """
        self.command(self.CS_ALL, self.CMD_BLON if on else self.CMD_BLOFF)

    def led(self, on: bool):
        """Turn LEDs on/off for display
        :param on: boolean indicating whether led is on or off
        """
        self.command(self.CS_ALL, self.CMD_LEDON if on else self.CMD_LEDOFF)

    def close(self):
        """Close connection to display"""
        os.close(self.__spi_fd)

    def pwm(self, value: int):
        """Set PWM of panel displays (brightness)
        :param value: pwm value between [1-15]
        """
        self.command(self.CS_ALL, self.CMD_PWM | (value & 0x0f))

    def clear(self):
        """Clear the display"""
        self._clear_frame_buffer()
        self.send_frame()

    @locked(LOCK_ID)
    def command(self, cs: int, cmd: int):
        """Write command to provided chip
        :param cs: chip to select
        :param cmd: CMD to write
        """
        data = ((self.ID_CMD << 8) | cmd) << 5
        self._chip_select(cs)
        self._send(struct.pack('>H', data))
        self._chip_select(self.CS_NONE)

    @locked(LOCK_ID)
    def send_frame(self):
        for cs, buffer in enumerate(self.__frame_buffer):
            self._chip_select(cs + 1)
            data = (self.__wr_cmd | buffer << 2)
            self._send(data.to_bytes(34, byteorder='big'))
            self._chip_select(self.CS_NONE)

    def add(self, value):
        for cs, buffer in enumerate(self.__frame_buffer):
            self.__frame_buffer[cs] = value
