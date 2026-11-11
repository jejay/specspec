---
id: hdJaFcQ=
type: requirement
parents:
- zBmAdi4=
- DFS2oJM=
---
# Keep the quiz tool out of everything that ships

The quiz tool lives with the repository's other tools and belongs to no wheel, source
distribution, VSIX or desktop app. A test holds that boundary. The tool reaches models
through the developer's own Claude Code login and every run costs money, so the test
suites and CI check its logic without calling a model.
