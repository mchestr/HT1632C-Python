#include "ht1632c.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>

#include <wiringPiSPI.h>
#include <wiringPi.h>

#include "panelconfig.h"

/*
 * commands written to the chip consist of a 3 bit "ID", followed by
 * either 9 bits of "Command code" or 7 bits of address + 4 bits of data.
 */
#define HT1632_ID_CMD        4	/* ID = 100 - Commands */
#define HT1632_ID_RD         6	/* ID = 110 - Read RAM */
#define HT1632_ID_WR         5	/* ID = 101 - Write RAM */

#define HT1632_CMD_SYSDIS 0x00	/* CMD= 0000-0000-x Turn off oscil */
#define HT1632_CMD_SYSON  0x01	/* CMD= 0000-0001-x Enable system oscil */
#define HT1632_CMD_LEDOFF 0x02	/* CMD= 0000-0010-x LED duty cycle gen off */
#define HT1632_CMD_LEDON  0x03	/* CMD= 0000-0011-x LEDs ON */
#define HT1632_CMD_BLOFF  0x08	/* CMD= 0000-1000-x Blink ON */
#define HT1632_CMD_BLON   0x09	/* CMD= 0000-1001-x Blink Off */
#define HT1632_CMD_SLVMD  0x10	/* CMD= 0001-00xx-x Slave Mode */
#define HT1632_CMD_MSTMD  0x14	/* CMD= 0001-01xx-x Master Mode */
#define HT1632_CMD_RCCLK  0x18	/* CMD= 0001-10xx-x Use on-chip clock */
#define HT1632_CMD_EXTCLK 0x1C	/* CMD= 0001-11xx-x Use external clock */
#define HT1632_CMD_COMS00 0x20	/* CMD= 0010-ABxx-x commons options */
#define HT1632_CMD_COMS01 0x24	/* CMD= 0010-ABxx-x commons options */
#define HT1632_CMD_COMS10 0x28	/* CMD= 0010-ABxx-x commons options */
#define HT1632_CMD_COMS11 0x2C	/* CMD= 0010-ABxx-x commons options */
#define HT1632_CMD_PWM    0xA0	/* CMD= 101x-PPPP-x PWM duty cycle */

#define HT1632_ID_LEN     3  /* IDs are 3 bits */
#define HT1632_CMD_LEN    8  /* CMDs are 8 bits */
#define HT1632_DATA_LEN   8  /* Data are 4*2 bits */
#define HT1632_ADDR_LEN   7  /* Address are 7 bits */

#define HT1632_CS_NONE 0x00  /* None of ht1632c selected */
#define HT1632_CS_ALL  0xff  /* All of ht1632c selected */

// panel parameters
#define COLOR_SIZE (CHIP_WIDTH * CHIP_HEIGHT / 8) /* size of single color data */
#define CHIP_SIZE ((COLOR_SIZE * COLORS) + 2)     /* effective size of frame buffer per chip */
#define PANEL_HEADER_BITS (HT1632_ID_LEN + HT1632_ADDR_LEN)

// use this WiringPi lock ID
#define LOCK_ID 0

#define toBit(v) ((v) ? 1 : 0)

// panel configuration
static int ht1632c_num_panels = 0;
#define NUM_CHIPS (CHIPS_PER_PANEL * ht1632c_num_panels) /* total number of chips */
#define WIDTH (PANEL_WIDTH * ht1632c_num_panels)
#define HEIGHT PANEL_HEIGHT

/// frame buffer
static uint8_t* ht1632c_framebuffer = 0;
#define FB_PTR(chip, addr) (ht1632c_framebuffer + (chip * CHIP_SIZE + addr))

static int ht1632c_spifd = -1;
static int ht1632c_clipX0, ht1632c_clipY0, ht1632c_clipX1, ht1632c_clipY1;
static int ht1632c_rot = 0;

//
// internal functions
//

void *reverse_endian(void *p, size_t size) {
  char *head = (char *)p;
  char *tail = head + size - 1;

  for(; tail > head; --tail, ++head) {
    char temp = *head;
    *head = *tail;
    *tail = temp;
  }
  return p;
}

#ifdef HT1632C_CS_CHAINED
void ht1632c_clk_pulse(int num) {
	while(num--) {
		digitalWrite(HT1632_CLK, 1);
		delayMicroseconds(CS_CLK_DELAY);
		digitalWrite(HT1632_CLK, 0);
		delayMicroseconds(CS_CLK_DELAY);
	}
}
#endif

void ht1632c_chipselect(const int cs) {
#ifdef HT1632C_CS_CHAINED
	if (cs == HT1632_CS_ALL) {
		digitalWrite(HT1632_CS, 0);
		ht1632c_clk_pulse(NUM_CHIPS);
	} else if (cs == HT1632_CS_NONE) {
		digitalWrite(HT1632_CS, 1);
		ht1632c_clk_pulse(NUM_CHIPS);
	} else {
		digitalWrite(HT1632_CS, 0);
		ht1632c_clk_pulse(1);
		digitalWrite(HT1632_CS, 1);
		ht1632c_clk_pulse(cs - 1);
	}
#else
	for (int i = 0; i < NUM_CHIPS; ++i)
		digitalWrite(HT1632_CS + i, ((cs == (i + 1)) || (cs == HT1632_CS_ALL)) ? 0 : 1);
#endif
}

void ht1632c_sendcmd(const int chip, const uint8_t cmd) {
	uint16_t data = HT1632_ID_CMD;
	data <<= 8;
	data |= cmd;
	data <<= 5;
	reverse_endian(&data, sizeof(data));

	piLock(LOCK_ID);

	ht1632c_chipselect(chip);
	write(ht1632c_spifd, &data, 2);
	ht1632c_chipselect(HT1632_CS_NONE);

	piUnlock(LOCK_ID);
}

void ht1632c_update_framebuffer(const int chip, const int addr, const uint8_t target_bitval, const uint8_t pixel_bitval) {
	uint8_t* const v = FB_PTR(chip, addr);
	if (target_bitval)
		*v |= pixel_bitval;
	else
		*v &= ~pixel_bitval;
}

uint8_t ht1632c_get_framebuffer(const int chip, const int addr, const uint8_t target_bitval) {
	uint8_t* const v = FB_PTR(chip, addr);
	return *v & target_bitval;
}

//
// public functions
//

int ht1632c_init(const int num_panels, const int rot) {
	// init WiringPi, SPI
	if (wiringPiSetup() == -1) {
		printf( "WiringPi Setup Failed: %s\n", strerror(errno));
		return 1;
	}
	if ((ht1632c_spifd = wiringPiSPISetup(0, SPI_FREQ)) < 0) {
		printf( "SPI Setup Failed: %s\n", strerror(errno));
		return 1;
	}

	// configuration
	if (num_panels <= 0) {
		printf( "Invalid parameters.");
		return 2;
	}
	ht1632c_num_panels = num_panels;
	ht1632c_rot = rot & 3;
	ht1632c_framebuffer = (uint8_t*) malloc(NUM_CHIPS * CHIP_SIZE);
	if (!ht1632c_framebuffer) {
		printf( "Framebuffer allocation failed.");
		return 3;
	}

	// configure CS pins
#ifdef HT1632C_CS_CHAINED
	pinMode(HT1632_CLK, OUTPUT);
	pinMode(HT1632_CS, OUTPUT);
#else
	for (int i = 0; i < NUM_CHIPS; ++i)
		pinMode(HT1632_CS + i, OUTPUT);
#endif

	// init display
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_SYSDIS);
	ht1632c_sendcmd(HT1632_CS_ALL, (CHIP_HEIGHT <= 8) ? HT1632_CMD_COMS00 : HT1632_CMD_COMS01);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_MSTMD);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_RCCLK);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_SYSON);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_LEDON);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_BLOFF);
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_PWM);

	ht1632c_clear();
	ht1632c_sendframe();

	return 0;
}

void ht1632c_ledoff(void) {
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_LEDOFF);
}

void ht1632c_ledon(void) {
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_LEDON);
}

void ht1632c_blon(void) {
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_BLON);
}

void ht1632c_bloff(void) {
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_BLOFF);
}

int ht1632c_close() {
	close(ht1632c_spifd);

	if (ht1632c_framebuffer) {
		free(ht1632c_framebuffer);
		ht1632c_framebuffer = 0;
	}
    return 0;
}

int ht1632c_width() {
	return (ht1632c_rot & 1) ? HEIGHT : WIDTH;
}

int ht1632c_height() {
	return (ht1632c_rot & 1) ? WIDTH : HEIGHT;
}

void ht1632c_pwm(const uint8_t value) {
	ht1632c_sendcmd(HT1632_CS_ALL, HT1632_CMD_PWM | (value & 0x0f));
}

void ht1632c_sendframe() {
	piLock(LOCK_ID);
	for (int chip = 0; chip < NUM_CHIPS; ++chip) {
		ht1632c_chipselect(chip + 1);
		write(ht1632c_spifd, FB_PTR(chip, 0), CHIP_SIZE);
		ht1632c_chipselect(HT1632_CS_NONE);
	}
	piUnlock(LOCK_ID);
}

void ht1632c_clear() {
	// clear buffer
	memset(ht1632c_framebuffer, 0, NUM_CHIPS * CHIP_SIZE);
	// init headers
	for (int i = 0; i < NUM_CHIPS; ++i) {
		*FB_PTR(i, 0) = HT1632_ID_WR << (8 - HT1632_ID_LEN);
	}
	// reset clipping
	ht1632c_clip_reset();
}

void ht1632c_clip(const int x0, const int y0, const int x1, const int y1) {
	ht1632c_clipX0 = (x0 >= 0) ? x0 : 0;
	ht1632c_clipY0 = (y0 >= 0) ? y0 : 0;
	ht1632c_clipX1 = (x1 >= 0) ? x1 : ht1632c_width();
	ht1632c_clipY1 = (y1 >= 0) ? y1 : ht1632c_height();
}

// #ifndef VERTICAL
void ht1632c_plot(const int rx, const int ry, const uint8_t color) {
	// clipping
	if (rx < ht1632c_clipX0 || rx >= ht1632c_clipX1 || ry < ht1632c_clipY0 || ry >= ht1632c_clipY1)
		return;

	// rotation
	int x = (ht1632c_rot & 1) ? ry : rx;
	if ((ht1632c_rot & 1) != (ht1632c_rot >> 1)) x = (WIDTH - 1) - x;
	int y = (ht1632c_rot & 1) ? rx : ry;
	if (ht1632c_rot & 2) y = (HEIGHT - 1) - y;

	const int xc = x / CHIP_WIDTH;
	const int yc = y / CHIP_HEIGHT;
	const int chip = xc + (xc & 0xfffe) + (yc * 2);

	const int xb = (x % CHIP_WIDTH) * (CHIP_HEIGHT / 8);
	const int yb = (y % CHIP_HEIGHT) + PANEL_HEADER_BITS;
	int addr = xb + (yb / 8);
	const uint8_t bitval = 128 >> (yb & 7);

	// first color
	ht1632c_update_framebuffer(chip, addr, (color & 1), bitval);
	if (addr <= 1 && bitval > 2) // special case: first bits must are 'wrapped' to the end
		ht1632c_update_framebuffer(chip, addr + CHIP_SIZE - 2, (color & 1), bitval);
	// other colors
	for (int i = 1; i < COLORS; ++i) {
		addr += COLOR_SIZE;
		ht1632c_update_framebuffer(chip, addr, (color & (1 << i)), bitval);
	}
}

// #ifndef VERTICAL
uint8_t ht1632c_peek(const int rx, const int ry) {
	// clipping
	if (rx < ht1632c_clipX0 || rx >= ht1632c_clipX1 || ry < ht1632c_clipY0 || ry >= ht1632c_clipY1)
		return 0;

	// rotation
	int x = (ht1632c_rot & 1) ? ry : rx;
	if ((ht1632c_rot & 1) != (ht1632c_rot >> 1)) x = (WIDTH - 1) - x;
	int y = (ht1632c_rot & 1) ? rx : ry;
	if (ht1632c_rot & 2) y = (HEIGHT - 1) - y;

	const int xc = x / CHIP_WIDTH;
	const int yc = y / CHIP_HEIGHT;
	const int chip = xc + (xc & 0xfffe) + (yc * 2);

	const int xb = (x % CHIP_WIDTH) * (CHIP_HEIGHT / 8);
	const int yb = (y % CHIP_HEIGHT) + PANEL_HEADER_BITS;
	int addr = xb + (yb / 8);
	const uint8_t bitval = 128 >> (yb & 7);

	uint8_t c;
	// first color
	c = ht1632c_get_framebuffer(chip, addr, bitval) ? 1 : 0;
	// other colors
	for (int i = 1; i < COLORS; ++i) {
		addr += COLOR_SIZE;
		c |= ht1632c_get_framebuffer(chip, addr, bitval) ? (1 << i) : 0;
	}
	return c;
}

void ht1632c_line(const int x0, const int y0, const int x1, const int y1, const uint8_t color)
{
	const int dx =  abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
	const int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
	int err = dx + dy, e2; /* error value e_xy */

	int x = x0, y = y0;
	for(;;) {
		ht1632c_plot(x, y, color);
		if (x == x1 && y == y1) break;
		e2 = 2 * err;
		if (e2 >= dy) { err += dy; x += sx; } /* e_xy+e_x > 0 */
		if (e2 <= dx) { err += dx; y += sy; } /* e_xy+e_y < 0 */
	}
}

void ht1632c_box(int x0, int y0, int x1, int y1, const uint8_t color) {
	// fix corner order
	{
		int tmp;
		if (x1 < x0) { tmp = x0; x0 = x1; x1 = tmp; };
		if (y1 < y0) { tmp = y0; y0 = y1; y1 = tmp; };
	}

	for (int y = y0; y <= y1; ++y) {
		for (int x = x0; x <= x1; ++x) {
			ht1632c_plot(x, y, color);
		}
	}
}

int ht1632c_putchar(const int x, const int y, const char c, const FontInfo* font, const uint8_t color, const uint8_t bg) {
	const int width = font->width;
	const int height = font->height;
	const int map_start = font->map_start;
	const int map_end = font->map_end;

	if (c < map_start) return 0;
	if (c > map_end) return 0;

	uint16_t const* addr = font->data + (c - map_start) * width;
	for (int col = 0; col < width; ++col) {
		uint16_t dots = addr[col];
		for (int row = height - 1; row >= 0; --row) {
			if (dots & 1)
				ht1632c_plot(x + col, y + row, color);
			else if (bg != TRANSPARENT)
				ht1632c_plot(x + col, y + row, bg);
			dots >>= 1;
		}
	}

	return x + width;
}

int ht1632c_putchar_metric(const int x, const int y, const char c, const FontInfo* font, const uint8_t color, const uint8_t bg) {
	const int width = font->width;
	const int height = font->height;
	const int map_start = font->map_start;
	const int map_end = font->map_end;

	if (c < map_start) return 0;
	if (c > map_end) return 0;

	uint16_t const* addr = font->data + (c - map_start) * width;
	uint8_t const* metric_addr = font->metric + 2*(c - map_start);
	const int left = metric_addr[0];
	const int right = metric_addr[1];
	for (int col = left; col < width - right; ++col) {
		uint16_t dots = addr[col];
		for (int row = height - 1; row >= 0; --row) {
			if (dots & 1)
				ht1632c_plot(x + col - left, y + row, color);
			else if (bg != TRANSPARENT)
				ht1632c_plot(x + col - left, y + row, bg);
			dots >>= 1;
		}
	}

	int col = width - right;
	if (bg != TRANSPARENT)
		for (int row = height - 1; row >= 0; --row)
			ht1632c_plot(x + col - left, y + row, bg);

	return x + width - left - right + 1;
}

int ht1632c_putstr(const int x, const int y, const char* s, const FontInfo* font, const uint8_t color, const uint8_t bg) {
	int p;
	for (p = x; *s; ++s) {
		p = ht1632c_putchar(p, y, *s, font, color, bg);
	}
	return p;
}

int ht1632c_putstr_metric(const int x, const int y, const char* s, const FontInfo* font, const uint8_t color, const uint8_t bg) {
	int p;
	for (p = x; *s; ++s) {
		p = ht1632c_putchar_metric(p, y, *s, font, color, bg);
	}
	return p;
}

int ht1632c_charwidth(const char c, const FontInfo* font) {
	const int width = font->width;
	const int map_start = font->map_start;
	const int map_end = font->map_end;

	if (c < map_start) return 0;
	if (c > map_end) return 0;

	uint8_t const* metric_addr = font->metric + 2*(c - map_start);
	const int left = metric_addr[0];
	const int right = metric_addr[1];
	return width - left - right + 1;
}

int ht1632c_strwidth(const char* s, const FontInfo* font) {
	int p = 0;
	for (; *s; ++s) {
		p += ht1632c_charwidth(*s, font);
	}
	return p;
}

int ht1632c_fontwidth(const FontInfo* font) {
	return font->width;
}

int ht1632c_fontheight(const FontInfo* font) {
	return font->height;
}
