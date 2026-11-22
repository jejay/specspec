---
id: aJeGE5M=
type: requirement
parents:
- oasfxqc=
- YGVHbXI=
---
# Check PyPI before building a tagged release

The tag build first checks that PyPI serves specspec in the tagged version. When it does not, the build stops before any other step and names the way forward: run Publish CLI to PyPI for that version, then run the tag build again. A release therefore publishes the CLI first and pushes the tag after it.
