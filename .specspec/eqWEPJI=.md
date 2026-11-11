---
id: eqWEPJI=
type: requirement
parents:
- sV3uzvQ=
- yCYr-E0=
---
# Interpolate node fill toward its painted border over an independent overview range

Begin the background transition at 40% camera scale and complete it at 16%:
q = 1 - clamp((scale - 0.16) / (0.40 - 0.16), 0, 1), treating invalid scales as
actual size. Keep the background at its actual-size fill at 40% scale and above;
below that, strengthen it toward the border as magnification decreases. Ordinary
arrow ink uses its own 70%-to-16% schedule. Both treatments reach their overview
endpoints at 16%, with distinct onset scales.

First derive the actual-size fill from 15% semantic accent at rest or 24% on hover,
mixed with the theme canvas background. Interpolate that fill toward the currently
painted border by q. Thus ordinary resting strength is 0.15 + 0.85*q; hovered cards
retain their original accent tint at actual size and reach the emphasized border
at the overview limit. High-contrast cards use the theme background as the base, with host foreground
as the border fallback when a contrast-border token is absent.

At 16% scale and below every fill equals its visible border, including the white
hovered neutral manifesto and contrast-theme borders. Actual-size and larger views
retain their exact editing-oriented tints and text. Hover darkening and spotlight
rings retain their independent paint roles. Camera updates an inherited fill-progress
CSS property on existing cards independently alongside edge paint; native inputs
and intrinsic world positions stay intact. Two-stage color mixing preserves both
actual-size hover tints and the strengthened border endpoint.
