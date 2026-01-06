# Summon Color Specifications

Detailed color specifications for all platforms and formats.

## Primary Brand Colors

### Summon Purple

**Primary brand color - used for logo, headers, and primary UI elements**

| Format | Value | Notes |
|--------|-------|-------|
| Hex | `#D98FF9` | Standard web/design format |
| RGB | `rgb(217, 143, 249)` | CSS format |
| RGB (0-1) | `(0.851, 0.561, 0.976)` | Normalized for some graphics libraries |
| RGB565 | `0xDC7F` | 16-bit color format for embedded displays |
| HSL | `hsl(282, 88%, 77%)` | Hue: 282°, Saturation: 88%, Lightness: 77% |
| HSV | `hsv(282°, 43%, 98%)` | Hue: 282°, Saturation: 43%, Value: 98% |

**Color Psychology:** Purple conveys creativity, magic, and mystery - perfect for a summoning/NFC gaming experience.

### Accent Teal/Cyan

**Secondary color - used for interactive elements, status indicators, and highlights**

| Format | Value | Notes |
|--------|-------|-------|
| Hex (Bright) | `#00FFFF` | Pure cyan - high visibility |
| RGB (Bright) | `rgb(0, 255, 255)` | Maximum brightness |
| Hex (Muted) | `#1BC9C3` | Alternative softer teal |
| RGB (Muted) | `rgb(27, 201, 195)` | Less saturated option |
| RGB565 | `0x07FF` | 16-bit format for displays |
| HSL (Bright) | `hsl(180, 100%, 50%)` | Pure cyan in HSL |
| HSL (Muted) | `hsl(178, 76%, 45%)` | Muted teal in HSL |

**Usage Notes:**
- Use **bright cyan** (`#00FFFF`) for GPS indicators, distance text, and status messages
- Use **muted teal** (`#1BC9C3`) for web/marketing materials where bright cyan may be too harsh

## Supporting Colors

### Success Green
| Format | Value |
|--------|-------|
| Hex | `#00FF00` |
| RGB | `rgb(0, 255, 0)` |
| Use Case | Success messages, GPS lock indicator, positive confirmations |

### Error Red
| Format | Value |
|--------|-------|
| Hex | `#FF0000` |
| RGB | `rgb(255, 0, 0)` |
| Use Case | Error states, GPS no-lock indicator, critical warnings |

### Warning Yellow
| Format | Value |
|--------|-------|
| Hex | `#FFFF00` |
| RGB | `rgb(255, 255, 0)` |
| Use Case | Warnings, loading states, attention-getting messages |

### Neutral Colors
| Color | Hex | RGB | Use Case |
|-------|-----|-----|----------|
| White | `#FFFFFF` | `rgb(255, 255, 255)` | Text, backgrounds, UI elements |
| Black | `#000000` | `rgb(0, 0, 0)` | Backgrounds, text, UI elements |
| Light Gray | `#CCCCCC` | `rgb(204, 204, 204)` | Disabled states, borders |
| Dark Gray | `#333333` | `rgb(51, 51, 51)` | Secondary text, subtle elements |

## Color Combinations

### Recommended Pairings

**Primary Combination (High Energy)**
- Background: Black `#000000`
- Primary: Summon Purple `#D98FF9`
- Accent: Bright Cyan `#00FFFF`
- Text: White `#FFFFFF`

**Accessible Web Combination**
- Background: White `#FFFFFF`
- Primary: Summon Purple `#D98FF9` (ensure sufficient contrast)
- Accent: Muted Teal `#1BC9C3`
- Text: Dark Gray `#333333` or Black `#000000`

**Night Mode**
- Background: Black `#000000`
- Primary: Summon Purple `#D98FF9`
- Accent: Bright Cyan `#00FFFF`
- Text: White `#FFFFFF`

## Accessibility & Contrast

### WCAG Contrast Ratios

| Combination | Ratio | WCAG AA | WCAG AAA |
|-------------|-------|---------|----------|
| Purple on Black | 8.5:1 | ✓ Pass | ✓ Pass |
| Purple on White | 2.5:1 | ✗ Fail | ✗ Fail |
| Cyan on Black | 13.1:1 | ✓ Pass | ✓ Pass |
| White on Purple | 3.4:1 | ✗ Fail (large text only) | ✗ Fail |

**Recommendations:**
- For body text on purple backgrounds, use **white or light gray** with minimum 18pt size
- For critical text, always use **high contrast combinations** (purple on black, white on black)
- Consider adding a **dark background behind colored text** for better readability
- Test all color combinations with accessibility tools before deployment

## RGB565 Conversion Reference

RGB565 is a 16-bit color format commonly used in embedded displays:
- **5 bits for Red** (0-31)
- **6 bits for Green** (0-63)
- **5 bits for Blue** (0-31)

### Converting RGB to RGB565:
```
RGB565 = ((R & 0xF8) << 8) | ((G & 0xFC) << 3) | (B >> 3)
```

### Converting RGB565 to RGB:
```
R = ((RGB565 >> 11) & 0x1F) * 255 / 31
G = ((RGB565 >> 5) & 0x3F) * 255 / 63
B = (RGB565 & 0x1F) * 255 / 31
```

### Quick Reference Table:
| Color | RGB | RGB565 Hex |
|-------|-----|------------|
| Summon Purple | (217, 143, 249) | 0xDC7F |
| Bright Cyan | (0, 255, 255) | 0x07FF |
| White | (255, 255, 255) | 0xFFFF |
| Black | (0, 0, 0) | 0x0000 |
| Red | (255, 0, 0) | 0xF800 |
| Green | (0, 255, 0) | 0x07E0 |
| Yellow | (255, 255, 0) | 0xFFE0 |

## Color in Code

### Arduino/ESP32 (ILI9341 Display)
```cpp
// Define colors in RGB565 format
#define SUMMON_PURPLE 0xDC7F      // Primary brand color
#define ILI9341_CYAN  0x07FF      // Accent teal/cyan
#define ILI9341_WHITE 0xFFFF      // Text/backgrounds
#define ILI9341_BLACK 0x0000      // Backgrounds
```

### Web/CSS
```css
:root {
  --summon-purple: #D98FF9;
  --summon-teal: #00FFFF;
  --summon-teal-muted: #1BC9C3;
}
```

### JavaScript/React
```javascript
const colors = {
  primary: '#D98FF9',
  accent: '#00FFFF',
  accentMuted: '#1BC9C3',
};
```

## Print Specifications

For printed materials (business cards, stickers, etc.):

### Summon Purple
- **CMYK:** C=13% M=43% Y=0% K=2%
- **Pantone:** 2563 C (closest match)

### Accent Teal
- **CMYK:** C=100% M=0% Y=0% K=0%
- **Pantone:** Process Cyan C

**Note:** Always request a proof for printed materials as colors may vary between screens and printers.
