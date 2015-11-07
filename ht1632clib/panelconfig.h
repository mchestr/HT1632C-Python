// ht1632c panel configuration

// Panel's write clock (WR) pin has to be connected to SCLK (14, GPIO 11),
// DATA has to be connected to MOSI (12, GPIO 10).

#define PANEL_32x16C /* preset for bi-color 32x16 panel */
// #define PANEL_24x16  /* preset for monochrome 24x16 panel */

// Chained chip select mode.
// Define if chips are chained and connected using CLK/CS lines.
// Don't define if chip select pins are connected directly to output pins.
#ifdef PANEL_32x16C
	#define HT1632C_CS_CHAINED
#endif
#ifdef PANEL_24x16
	#undef HT1632C_CS_CHAINED
#endif

// chip select pins
#ifdef HT1632C_CS_CHAINED
	#define HT1632_CLK  10          /* chip select clock pin */
	#define HT1632_CS   11          /* chip select data pin */
#else
	#define HT1632_CS   10          /* first chip select pin; */
	                                /* successive pin numbers are used for additional chips */
#endif

// panel parameters
#ifdef PANEL_32x16C
	#define CHIPS_PER_PANEL 4       /* ht1632c chips per panel */
	#define PANEL_WIDTH 32          /* panel width (pixels) */
	#define PANEL_HEIGHT 16         /* panel height (pixels) */
	#define CHIP_WIDTH 16           /* chip width (pixels) */
	#define CHIP_HEIGHT 8           /* chip height (pixels) */
	#define COLORS 2                /* number of colors (1 or 2) */
#endif
#ifdef PANEL_24x16
	#define CHIPS_PER_PANEL 1       /* ht1632c chips per panel */
	#define PANEL_WIDTH 24          /* panel width (pixels) */
	#define PANEL_HEIGHT 16         /* panel height (pixels) */
	#define CHIP_WIDTH 24           /* chip width (pixels) */
	#define CHIP_HEIGHT 16          /* chip height (pixels) */
	#define COLORS 1                /* number of colors (1 or 2) */
#endif

#define SPI_FREQ 2560000            /* SPI frequency (Hz; up to 32000000) */
#define CS_CLK_DELAY 10             /* CS pulse length (µs) in chained CS mode */
