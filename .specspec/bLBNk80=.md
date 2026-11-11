---
id: bLBNk80=
type: requirement
parents:
- pqNhV6s=
---
# Emphasize a colored border or link on hover with more lightness and chroma in its own hue

The border of a hovered colored card and the ink of an incident curve and arrowhead that is added, removed or part of a draft are derived in OKLCH from their own color: lightness plus 0.10, capped at 0.95, chroma times 1.30 and the hue as it is. Incident ink is fully opaque. The gray manifesto of the distance and type modes has a white border on hover, and a manifesto colored by revision status is emphasized in its hue like every other colored node. An ordinary neutral link is emphasized by mixing its color with the foreground color of the theme.

The emphasis changes these inks alone. The tints and the text, the darkening, the pairing and the order of curve and arrowhead, their width, dashes, path and head geometry, the camera and the form with its draft and text cursor are the same during and after a hover. The computed lightness, chroma and hue and the exact restoration of the paint are verified in dark, light and high-contrast themes, on an expanded card and at the smallest zoom. How a browser maps the colors into its gamut and how a display shows them limit what these checks prove.
