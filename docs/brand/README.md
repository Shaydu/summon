# Summon Brand Guidelines

This folder contains brand assets and guidelines for the Summon NFC project to ensure consistent visual identity across the app, website, and other materials.

## Brand Colors

### Primary Purple
- **Hex Code:** `#D98FF9` (RGB: 217, 143, 249)
- **RGB565 (for displays):** `0xDC7F`
- **Usage:** Primary brand color, logo, headers, accent elements

### Accent Teal/Cyan
- **Hex Code:** `#00FFFF` (RGB: 0, 255, 255)
- **Alternative Teal:** `#1BC9C3` (more muted teal option)
- **Usage:** Secondary accent color, interactive elements, GPS indicators, distance text

### Supporting Colors
- **White:** `#FFFFFF` - Text, backgrounds
- **Black:** `#000000` - Backgrounds, text
- **Yellow:** `#FFFF00` - Status messages, warnings
- **Green:** `#00FF00` - Success states, GPS lock indicator
- **Red:** `#FF0000` - Error states, GPS no-lock indicator

## Typography

### Primary Typeface: FreeSans

The Summon app uses the **FreeSans** font family, available in multiple sizes:

- **FreeSans9pt7b** - Small text, captions, details
- **FreeSans12pt7b** - Body text, medium-sized UI elements
- **FreeSans18pt7b** - Headers, titles, prominent text

**Note:** FreeSans is part of the Adafruit GFX Font library. For web use, equivalent fonts include:
- **Arial** (closest web-safe alternative)
- **Helvetica** (preferred alternative)
- **system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI"** (modern system fonts)

### Font Usage Guidelines
- **Headers:** FreeSans18pt7b / 18pt+ size
- **Body Text:** FreeSans12pt7b / 12pt size
- **Captions/Details:** FreeSans9pt7b / 9pt size
- **Style:** Clean, sans-serif, modern, highly legible

## Logo Assets

### Logo Files
- **Header Logo:** `arduino-setup/logo.h` (128x53 pixels, RGB565 format)
- **Mob Graphics:** `arduino-setup/mob_graphics.h` (128x128 icons)

The logo is stored as a C header file with pixel data in RGB565 format for embedded displays. The logo dimensions are 128x53 pixels.

### Logo Colors
The logo uses the primary purple (`#D98FF9`) as its main color against a transparent or dark background.

### Converting Logo for Web

To use the logo on the web, you'll need to:

1. **Extract the logo** from `logo.h` (pixel array)
2. **Convert RGB565 to standard RGB** format
3. **Export as PNG or SVG** with transparency

Or alternatively, recreate the logo as an SVG using the brand purple color.

## Design Principles

### Visual Style
- **Modern & Clean:** Minimal UI with clear hierarchy
- **High Contrast:** Ensure text is readable on all backgrounds
- **Colorful Accents:** Use purple and teal strategically for interest
- **Rounded Elements:** Soft corners on buttons and containers
- **Generous Spacing:** Don't crowd elements

### Color Usage Guidelines
- Use **purple** for branding and primary actions
- Use **teal/cyan** for secondary information and status indicators
- Reserve **green** for success/confirmation states
- Reserve **red** for errors and critical warnings
- Use **yellow** sparingly for attention-getting alerts

### Accessibility
- Maintain minimum contrast ratio of 4.5:1 for text
- Avoid using color alone to convey information
- Ensure interactive elements are touch-friendly (minimum 44x44px)

## Web Implementation

### CSS Variables Example

```css
:root {
  /* Brand Colors */
  --summon-purple: #D98FF9;
  --summon-teal: #00FFFF;
  --summon-teal-muted: #1BC9C3;
  
  /* Supporting Colors */
  --color-success: #00FF00;
  --color-error: #FF0000;
  --color-warning: #FFFF00;
  --color-info: #00FFFF;
  
  /* Typography */
  --font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, Helvetica, sans-serif;
  --font-size-small: 9pt;
  --font-size-medium: 12pt;
  --font-size-large: 18pt;
}
```

### Example Usage

```css
.header {
  background-color: var(--summon-purple);
  font-family: var(--font-family);
  font-size: var(--font-size-large);
  color: white;
}

.cta-button {
  background-color: var(--summon-purple);
  color: white;
  border: 2px solid var(--summon-teal);
}

.status-indicator {
  color: var(--summon-teal);
}
```

## File Structure

```
docs/brand/
├── README.md              # This file - brand guidelines
└── colors.md              # Detailed color specifications
```

For logo assets, see:
```
arduino-setup/
├── logo.h                 # Purple Summon logo (128x53px, RGB565)
└── mob_graphics.h         # Mob icons (128x128px, RGB565)
```

## Contact & Updates

For questions about brand usage or to request additional assets, please contact the project maintainer.

Last Updated: January 6, 2026
