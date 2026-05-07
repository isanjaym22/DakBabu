"""Design tokens for DakBabu UI.

All colors, fonts, spacing, and border radii are extracted from the Stitch
design system (stitch_ui/step1_credentials/DESIGN.md) and CLAUDE.md.

Every UI file must import tokens from here — never hardcode colors or fonts.
This file contains ZERO widget code; it is pure constants.
"""

# ---------------------------------------------------------------------------
# Font family
# ---------------------------------------------------------------------------
# Primary: Inter (Google Fonts). Fallback: Segoe UI (native Windows feel).
FONT_FAMILY: str = "Inter"
FONT_FAMILY_FALLBACK: str = "Segoe UI"


# ---------------------------------------------------------------------------
# Typography — (family, size, weight) tuples for customtkinter
# ---------------------------------------------------------------------------
# customtkinter font tuples: ("family", size_int, "weight")
# Weights: "normal" = 400, "bold" = 700.  CTk doesn't support 500/600
# natively, so we map 500→"normal", 600→"bold", 700→"bold".

FONT_H1: tuple[str, int, str] = (FONT_FAMILY, 30, "bold")       # 700
FONT_H2: tuple[str, int, str] = (FONT_FAMILY, 24, "bold")       # 600
FONT_H3: tuple[str, int, str] = (FONT_FAMILY, 20, "bold")       # 600
FONT_BODY_LG: tuple[str, int, str] = (FONT_FAMILY, 16, "normal")  # 400
FONT_BODY_MD: tuple[str, int, str] = (FONT_FAMILY, 14, "normal")  # 400
FONT_LABEL_MD: tuple[str, int, str] = (FONT_FAMILY, 14, "bold")   # 500
FONT_LABEL_SM: tuple[str, int, str] = (FONT_FAMILY, 12, "bold")   # 600


# ---------------------------------------------------------------------------
# Color palette — from DESIGN.md and Stitch HTML
# ---------------------------------------------------------------------------

# Primary
COLOR_PRIMARY: str = "#004AC6"
COLOR_PRIMARY_CONTAINER: str = "#2563EB"    # buttons, active indicators
COLOR_ON_PRIMARY: str = "#FFFFFF"
COLOR_ON_PRIMARY_CONTAINER: str = "#EEEFFF"
COLOR_INVERSE_PRIMARY: str = "#B4C5FF"
COLOR_PRIMARY_FIXED: str = "#DBE1FF"        # sending badge bg
COLOR_PRIMARY_FIXED_DIM: str = "#B4C5FF"
COLOR_ON_PRIMARY_FIXED: str = "#00174B"
COLOR_ON_PRIMARY_FIXED_VARIANT: str = "#003EA8"
COLOR_SURFACE_TINT: str = "#0053DB"

# Secondary
COLOR_SECONDARY: str = "#505F76"
COLOR_ON_SECONDARY: str = "#FFFFFF"
COLOR_SECONDARY_CONTAINER: str = "#D0E1FB"
COLOR_ON_SECONDARY_CONTAINER: str = "#54647A"
COLOR_SECONDARY_FIXED: str = "#D3E4FE"
COLOR_SECONDARY_FIXED_DIM: str = "#B7C8E1"
COLOR_ON_SECONDARY_FIXED: str = "#0B1C30"
COLOR_ON_SECONDARY_FIXED_VARIANT: str = "#38485D"

# Tertiary
COLOR_TERTIARY: str = "#943700"
COLOR_ON_TERTIARY: str = "#FFFFFF"
COLOR_TERTIARY_CONTAINER: str = "#BC4800"
COLOR_ON_TERTIARY_CONTAINER: str = "#FFEDE6"
COLOR_TERTIARY_FIXED: str = "#FFDBCD"
COLOR_TERTIARY_FIXED_DIM: str = "#FFB596"
COLOR_ON_TERTIARY_FIXED: str = "#360F00"
COLOR_ON_TERTIARY_FIXED_VARIANT: str = "#7D2D00"

# Error (semantic — failed deliveries, validation errors)
COLOR_ERROR: str = "#BA1A1A"
COLOR_ON_ERROR: str = "#FFFFFF"
COLOR_ERROR_CONTAINER: str = "#FFDAD6"      # failed badge bg
COLOR_ON_ERROR_CONTAINER: str = "#93000A"

# Success (semantic — sent badges, connection success)
COLOR_SUCCESS_BG: str = "#F0FDF4"           # green-50 (sent badge bg)
COLOR_SUCCESS_TEXT: str = "#15803D"          # green-700 (sent badge text)
COLOR_SUCCESS_BADGE_BG: str = "#ECFDF5"     # emerald-50 (connection badge bg)
COLOR_SUCCESS_BADGE_TEXT: str = "#047857"    # emerald-700 (connection badge text)
COLOR_SUCCESS_BADGE_BORDER: str = "#D1FAE5"  # emerald-100 (connection badge border)

# Warning (semantic — rate limit, duplicate warnings)
COLOR_WARNING_BG: str = "#FFFBEB"           # amber-50
COLOR_WARNING_TEXT: str = "#B45309"          # amber-700

# Surface / Background
COLOR_BACKGROUND: str = "#FAF8FF"
COLOR_ON_BACKGROUND: str = "#191B23"
COLOR_SURFACE: str = "#FAF8FF"
COLOR_SURFACE_DIM: str = "#D9D9E5"
COLOR_SURFACE_BRIGHT: str = "#FAF8FF"
COLOR_SURFACE_CONTAINER_LOWEST: str = "#FFFFFF"  # cards, panels
COLOR_SURFACE_CONTAINER_LOW: str = "#F3F3FE"     # table header bg
COLOR_SURFACE_CONTAINER: str = "#EDEDF9"
COLOR_SURFACE_CONTAINER_HIGH: str = "#E7E7F3"    # pending badge bg
COLOR_SURFACE_CONTAINER_HIGHEST: str = "#E1E2ED"
COLOR_SURFACE_VARIANT: str = "#E1E2ED"
COLOR_INVERSE_SURFACE: str = "#2E3039"
COLOR_INVERSE_ON_SURFACE: str = "#F0F0FB"

# Text
COLOR_ON_SURFACE: str = "#191B23"           # primary text
COLOR_ON_SURFACE_VARIANT: str = "#434655"   # secondary text

# Outline / Border
COLOR_OUTLINE: str = "#737686"              # muted text, table headers
COLOR_OUTLINE_VARIANT: str = "#C3C6D7"      # card borders, dividers

# Info box (from Stitch step1 HTML)
COLOR_INFO_BG: str = "#EFF6FF"              # blue-50
COLOR_INFO_BORDER: str = "#2563EB"          # blue-600 (left border)
COLOR_INFO_TEXT: str = "#1E40AF"            # blue-800
COLOR_INFO_ICON: str = "#2563EB"            # blue-600

# NavBar / Footer (from Stitch HTML)
COLOR_NAVBAR_BG: str = "#FFFFFF"
COLOR_NAVBAR_BORDER: str = "#E2E8F0"        # slate-200
COLOR_NAVBAR_TEXT: str = "#0F172A"           # slate-900
COLOR_NAVBAR_SUBTITLE: str = "#64748B"      # slate-500
COLOR_NAVBAR_INACTIVE: str = "#64748B"      # slate-500
COLOR_NAVBAR_ACTIVE: str = "#2563EB"        # blue-600

# Button — secondary / inactive (from Stitch HTML)
COLOR_BUTTON_SECONDARY_TEXT: str = "#1E293B"    # slate-800
COLOR_BUTTON_SECONDARY_BORDER: str = "#CBD5E1"  # slate-300
COLOR_BUTTON_DISABLED_TEXT: str = "#CBD5E1"      # slate-300
COLOR_BUTTON_DISABLED_BORDER: str = "#E2E8F0"   # slate-200
COLOR_PRIMARY_HOVER: str = "#1D4ED8"             # blue-700 (button hover darken)


# ---------------------------------------------------------------------------
# Border radii (px values for customtkinter corner_radius)
# ---------------------------------------------------------------------------
RADIUS_SM: int = 4           # 0.25rem — small elements
RADIUS_DEFAULT: int = 8      # 0.5rem — inputs, form fields
RADIUS_MD: int = 12          # 0.75rem — medium containers
RADIUS_LG: int = 16          # 1rem — large containers
RADIUS_XL: int = 24          # 1.5rem — extra large
RADIUS_CARD: int = 10        # cards (from DESIGN.md components)
RADIUS_INPUT: int = 8        # form inputs (from DESIGN.md)
RADIUS_PILL: int = 9999      # pill buttons (full round)


# ---------------------------------------------------------------------------
# Spacing (px values)
# ---------------------------------------------------------------------------
SPACING_UNIT: int = 4                # base spacing unit
SPACING_CONTAINER_PADDING: int = 32  # container padding
SPACING_STACK_GAP: int = 16          # vertical gap between sections
SPACING_INLINE_GAP: int = 12        # horizontal gap between elements
SPACING_SECTION_MARGIN: int = 40     # margin between major sections


# ---------------------------------------------------------------------------
# Elevation — border and shadow values (from DESIGN.md)
# ---------------------------------------------------------------------------
BORDER_WIDTH_DEFAULT: int = 1        # standard card/input border
BORDER_WIDTH_FOCUS: int = 2          # focus ring for inputs

# Shadow for interactive/floating elements (DESIGN.md Tier 2)
SHADOW_INTERACTIVE: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"

# Scrollbar colors (from Stitch HTML custom-scrollbar CSS)
COLOR_SCROLLBAR_TRACK: str = "transparent"
COLOR_SCROLLBAR_THUMB: str = "#E2E8F0"
COLOR_SCROLLBAR_THUMB_HOVER: str = "#CBD5E1"


# ---------------------------------------------------------------------------
# Window configuration
# ---------------------------------------------------------------------------
WINDOW_MIN_WIDTH: int = 900
WINDOW_MIN_HEIGHT: int = 600
WINDOW_DEFAULT_WIDTH: int = 1100
WINDOW_DEFAULT_HEIGHT: int = 750
WINDOW_TITLE: str = "DakBabu"


# ---------------------------------------------------------------------------
# Progress bar (from DESIGN.md components)
# ---------------------------------------------------------------------------
PROGRESS_BAR_HEIGHT: int = 8         # thin 8px height
COLOR_PROGRESS_BG: str = "#E2E8F0"   # background track
COLOR_PROGRESS_FILL: str = "#2563EB"  # fill (primary-container)


# ---------------------------------------------------------------------------
# Table / data list (from DESIGN.md components)
# ---------------------------------------------------------------------------
COLOR_TABLE_ROW_ALT: str = "#F1F5F9"  # zebra striping / bottom borders
COLOR_TABLE_HEADER_BG: str = "#F3F3FE"  # surface-container-low


# ---------------------------------------------------------------------------
# Unicode icon substitutes (replacing Material icons for CTk)
# ---------------------------------------------------------------------------
ICON_CHECK: str = "✓"
ICON_CROSS: str = "✗"
ICON_WARNING: str = "⚠"
ICON_INFO: str = "ℹ"
ICON_ARROW_LEFT: str = "←"
ICON_ARROW_RIGHT: str = "→"
ICON_HOURGLASS: str = "⏳"
ICON_STOP: str = "⏹"
ICON_PLAY: str = "▶"
ICON_DOWNLOAD: str = "⬇"
ICON_EYE_OPEN: str = "👁"
ICON_EYE_CLOSED: str = "🔒"
ICON_MAIL: str = "✉"
