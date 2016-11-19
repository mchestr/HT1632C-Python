#define HT1632C_H

#include <inttypes.h>

#include "fonts.h"

//
// constants
//

#define BLACK        0
#define GREEN        1
#define RED          2
#define ORANGE       3
#define TRANSPARENT 0xff

//
// public functions
//

/// Initializes library and display.
/// rot: rotation of display content in multiples of 90° clockwise
int ht1632c_init(const int num_panels, const int rot);

/// Shuts down library.
int ht1632c_close(void);

/// Returns logical display width in pixels.
int ht1632c_width(void);

/// Returns logical display height in pixels.
int ht1632c_height(void);

/// Sets display brightness.
void ht1632c_pwm(const uint8_t value);

/// Sends frame buffer to display; required to bring any drawing operations to the display.
void ht1632c_sendframe(void);

/// Clears the whole frame. Also reset clipping area.
void ht1632c_clear(void);

/// Puts a single pixel in the coordinates x, y.
void ht1632c_plot(const int x, const int y, const uint8_t color);

/// Gets pixel value at the coordinates x, y.
uint8_t ht1632c_peek(const int x, const int y);

/// Restricts modification to the clipping area (x1/y1-exclusive).
/// Negative values translate to min/max values.
void ht1632c_clip(const int x0, const int y0, const int x1, const int y1);

/// Reset clipping.
#define ht1632c_clip_reset(void) ht1632c_clip(-1, -1, -1, -1)

/// Draws a line from (x0, y0) to (x1, y1).
void ht1632c_line(const int x0, const int y0, const int x1, const int y1, const uint8_t color);

/// Draws a box from (x0, y0) to (x1, y1).
void ht1632c_box(const int x0, const int y0, const int x1, const int y1, const uint8_t color);

/// Prints a character.
int ht1632c_putchar(const int x, const int y, const char c, const FontInfo* font, const uint8_t color, const uint8_t bg);

/// Prints a string.
int ht1632c_putstr(const int x, const int y, const char* s, const FontInfo* font, const uint8_t color, const uint8_t bg);

/// Returns the character width (pixels) of given font.
int ht1632c_fontwidth(const FontInfo* font);

/// Returns the character height (pixels) of given font.
int ht1632c_fontheight(const FontInfo* font);
