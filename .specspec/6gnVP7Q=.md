---
id: 6gnVP7Q=
type: implementation
parents:
- s7ZgBcM=
sources:
- path: tools/social_preview.py
- path: branding/social-preview.svg
- path: branding/social-preview.png
---
# Draw the social preview from outlined Manrope and the dark logo

tools/social_preview.py writes branding/social-preview.svg and, with resvg on PATH, renders branding/social-preview.png. It outlines Manrope with the text helpers of tools/readme_figures.py and shears the outlines of Why by 10° around the baseline. It embeds branding/specspec-logo-dark.svg as a nested SVG, placed by its visible artwork, and draws the GitHub mark from the mark-github Octicon, so the SVG is self-contained. Nodes take clean spectrum stops by kind and depth, and the heavy lines share one horizontal spectrum gradient.

Like the README figures, the script runs with a Python that has fontTools and reads Manrope from the sibling branding workspace. The owner uploads the PNG under Settings › General › Social preview.
