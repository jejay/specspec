---
id: eqWEPJI=
type: requirement
parents:
- sV3uzvQ=
- yCYr-E0=
---
# Interpolate node fill toward its painted border over the overview range

Use the same clamped 12%-to-100% camera interval as ordinary arrow ink. Let
q = 1 - clamp((scale - 0.12)/0.88, 0, 1), treating invalid scales as actual size.
Mix the currently painted border ink into the theme canvas background with strength
0.15 + 0.85*q at rest and 0.24 + 0.76*q on hover. High-contrast resting cards use q.
At the minimum camera scale every fill equals its visible border, including the
white hovered neutral manifesto and contrast-theme borders. Actual-size and larger
views retain their editing-oriented tints and text. Hover darkening and exact-version
spotlight rings retain their independent paint roles. Camera updates inherited CSS
paint variables on existing cards and edges; the world and native inputs stay intact.
