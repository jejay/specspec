---
id: WpYvGUo=
type: requirement
parents:
- XV5_rPQ=
---
# Distribute an isolated global Python command-line application

Install specspec as a user-wide command available across product directories, with
its dependencies isolated from each product's runtime. Support uv tool install and
pipx install from a local checkout, Git URL or built wheel, and retain an importable
Python library for integration. A persistent installation is the normal human and
visual-host prerequisite; one-shot uvx use remains available. The CLI needs Python
3.11 or newer and uses Git for versioned operations. Publishing is a separately
authorized release action.
