---
id: WpYvGUo=
type: requirement
parents:
- 1T-fMcs=
---
# Distribute an isolated global Python command-line application

Install specspec as a user-wide command available across product directories, with
its dependencies isolated from each product's runtime. The specspec distribution on
PyPI is the normal installation source: uv tool install specspec or pipx install
specspec. Local-checkout, Git URL and wheel alternatives are available for development or
explicit artifact qualification, and an importable Python library for integration. A persistent installation is the normal human and
visual-host prerequisite; one-shot uvx use is available too. The CLI needs Python
3.11 or newer and uses Git for versioned operations. Publishing is a separately
authorized release action.
