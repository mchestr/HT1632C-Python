#include <inttypes.h>

typedef struct
{
	const uint8_t width;
	const uint8_t height;
	const uint8_t map_start;
	const uint8_t map_end;
	const uint16_t* data;
	const uint8_t* metric;
} FontInfo;

// numeric-only fonts
extern const FontInfo font_3x4_num;
extern const FontInfo font_4x5_num;
extern const FontInfo font_7x8_num;

extern const FontInfo font_4x6;
extern const FontInfo font_5x8;
extern const FontInfo font_6x8;
extern const FontInfo font_7x12;
extern const FontInfo font_8x12;
extern const FontInfo font_12x16;

// symbol fonts
extern const FontInfo font_4x6_sym;

