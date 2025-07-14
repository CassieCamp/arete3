# Arete Design System — Source of Truth

This file defines the locked brand design system. All colors, typography, shadows, and spacing decisions are documented here.

## Rules:
- Do NOT override color tokens without explicit approval.
- Do NOT introduce arbitrary styles or unapproved variables.
- Do NOT modify `theme.css` without updating this file first.

## Colors:
- Color system based on OKLCH tokens
- Light and Dark modes strictly defined
- Source originally derived from TweakCN color calculator
- Exact tokens detailed in `/app/theme.css`

## Fonts:
- Inter (sans-serif) for system text
- Playfair Display (serif) for headings
- Roboto Mono for monospace code

## Tailwind Configuration:
- Tailwind `theme.extend` must reference CSS variables only
- No hardcoded hex or HSL values allowed in components or utilities

## Last Reviewed: [leave blank — will be filled on review]