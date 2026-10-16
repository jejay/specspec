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
First derive the actual-size fill from 15% semantic accent at rest or 24% on hover,
mixed with the theme canvas background. Interpolate that fill toward the currently
painted border by q. Thus ordinary resting strength is 0.15 + 0.85*q; hovered cards
retain their original accent tint at actual size and reach the emphasized border
at the overview limit. High-contrast cards use the theme background as the base, with host foreground
as the border fallback when a contrast-border token is absent.

At minimum scale every fill equals its visible border, including the white hovered
neutral manifesto and contrast-theme borders. Actual-size and larger views retain
their exact editing-oriented tints and text. Hover darkening and exact-version rings
retain their independent paint roles. Camera updates an inherited fill-progress CSS
property on existing cards in parallel with edge paint; native inputs and intrinsic
world positions stay intact. Two-stage color mixing preserves both actual-size hover
tints and the strengthened border endpoint.
