---
name: DakBabu Design System
colors:
  surface: '#faf8ff'
  surface-dim: '#d9d9e5'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3fe'
  surface-container: '#ededf9'
  surface-container-high: '#e7e7f3'
  surface-container-highest: '#e1e2ed'
  on-surface: '#191b23'
  on-surface-variant: '#434655'
  inverse-surface: '#2e3039'
  inverse-on-surface: '#f0f0fb'
  outline: '#737686'
  outline-variant: '#c3c6d7'
  surface-tint: '#0053db'
  primary: '#004ac6'
  on-primary: '#ffffff'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#b4c5ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#943700'
  on-tertiary: '#ffffff'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#faf8ff'
  on-background: '#191b23'
  surface-variant: '#e1e2ed'
typography:
  h1:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-padding: 32px
  stack-gap: 16px
  inline-gap: 12px
  section-margin: 40px
---

## Brand & Style
The brand personality is rooted in reliability, efficiency, and institutional trust. As a tool for bulk communication, the interface must feel like a dependable infrastructure—calm under pressure and highly organized. 

The design style follows a **Corporate / Modern** movement, blending the utilitarian clarity of a government portal with the refined whitespace of modern productivity tools like Notion. It prioritizes information density and legibility, utilizing a "Canvas and Sheet" metaphor where the workspace sits on a distinct background to provide focus and mental order.

## Colors
The palette is intentionally restrained to ensure the user's content remains the primary focus. 
- **Primary Accent:** Used for call-to-actions, active step indicators, and progress completion.
- **Canvas & Surface:** A two-tier background system. The `#F8FAFC` canvas provides a soft foundation, while `#FFFFFF` surfaces (cards/panels) elevate the working area.
- **Semantic Colors:** Reserved strictly for feedback. Success green for "Sent" status, error red for "Failed Delivery," and warning yellow for "Draft" or "Rate Limit" alerts.

## Typography
The system utilizes **Inter** for its exceptional legibility in desktop application environments. 
- **Headlines:** Use tighter letter-spacing and heavier weights to provide a strong anchor for page sections.
- **Body Text:** Standardized at 14px (body-md) for data-heavy views to balance information density with readability.
- **Labels:** Small labels (label-sm) use uppercase and increased tracking to differentiate "Metadata" or "Field Headers" from user-generated content.
- **Fallback:** In the absence of Inter, the system defaults to **Segoe UI** to maintain the native Windows application feel.

## Layout & Spacing
This design system employs a **Fixed-Fluid Hybrid** layout. The sidebar navigation remains fixed, while the main staging area fluidly expands, anchored by a maximum content width of 1200px to prevent line lengths from becoming unreadable.

A strict 4px baseline grid ensures vertical rhythm. Generous whitespace (32px container padding) is used to separate the "Configuration" panels from the "Preview" panels, mimicking the organized feel of a well-laid-out form.

## Elevation & Depth
Depth is conveyed through **Low-contrast outlines** and subtle tonal layering rather than heavy shadows. 
- **Tier 0 (Canvas):** The `#F8FAFC` base layer.
- **Tier 1 (Surface):** White cards with a 1px `#E2E8F0` border. No shadow is used here to maintain a "flat" professional aesthetic.
- **Tier 2 (Interactive):** Only active elements or dropdown menus receive a very soft, diffused shadow (`0 4px 6px -1px rgb(0 0 0 / 0.1)`) to indicate they are floating above the workspace.

## Shapes
The shape language transitions from structured to organic to differentiate between "Containers" and "Actions."
- **Containers (Cards):** Use a 10px radius, providing a modern but stable frame.
- **Inputs:** Use an 8px radius, slightly sharper than cards to suggest precision and data entry.
- **Buttons:** Use a full pill-shape (9999px). This distinct roundness makes primary actions immediately identifiable against the otherwise rectilinear grid of the desktop app.

## Components
- **Buttons:** Primary buttons are pill-shaped, `#2563EB` fill with white text. Secondary buttons use a subtle gray border with `#1E293B` text.
- **Form Inputs:** 8px corner radius. Focus states must use a 2px solid primary blue ring with a 1px offset.
- **Cards:** White background, 10px radius, 1px `#E2E8F0` border. Used to group "Email Settings," "Recipient Lists," and "Schedule."
- **Step Indicators (Steppers):** Horizontal layout. Completed steps show a checkmark in a primary blue circle; current steps show a blue ring; pending steps show a light gray ring.
- **Progress Bars:** Thin 8px height, rounded caps. Background is `#E2E8F0`, fill is `#2563EB`. For bulk sending, the bar should include a percentage label in `label-sm` style.
- **Data Lists:** For recipient lists, use alternating row tints (zebra striping) or 1px bottom borders in `#F1F5F9`.