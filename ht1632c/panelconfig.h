// ht1632c panel configuration

// Panel's write clock (WR) pin has to be connected to SCLK (14, GPIO 11),
// DATA has to be connected to MOSI (12, GPIO 10).

//#define PANEL_32x16C /* preset for bi-color 32x16 panel */
// #define PANEL_24x16  /* preset for monochrome 24x16 panel */

// Chained chip select mode.
// Define if chips are chained and connected using CLK/CS lines.
// Don't define if chip select pins are connected directly to output pins.
//#define HT1632C_CS_CHAINED
#define HT1632_CLK  10          /* chip select clock pin */
#define HT1632_CS   11

// panel parameters
#define CHIPS_PER_PANEL 1       /* ht1632c chips per panel */
#define PANEL_WIDTH 32          /* panel width (pixels) */
#define PANEL_HEIGHT 8         /* panel height (pixels) */
#define CHIP_WIDTH 32           /* chip width (pixels) */
#define CHIP_HEIGHT 8           /* chip height (pixels) */
#define COLORS 1                /* number of colors (1 or 2) */

#define SPI_FREQ 2560000            /* SPI frequency (Hz; up to 32000000) */
#define CS_CLK_DELAY 10             /* CS pulse length (µs) in chained CS mode */
