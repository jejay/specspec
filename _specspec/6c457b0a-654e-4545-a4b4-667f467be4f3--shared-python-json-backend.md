---
id: 6c457b0a-654e-4545-a4b4-667f467be4f3
type: requirement
status: proposed
parents:
- f0d0d18b-b52e-4eef-ab13-da7bedfd07a2
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- d51d6da3-4142-4fc7-b593-d935ee5fdf6f
managed_hash: 72158e6ee79a1d58885fdcb223546c7f384b19e28aeb35c4b7dbcd5d6cbf77a8
---
# Share one Python validation and mutation backend

Expose graph operations through a reusable Python library and a versioned JSON CLI.
The VS Code extension invokes that CLI without a shell; it does not independently
implement schema validation, lifecycle rules, or canonical file mutations.

Use `api_version`, `ok`, `result`, and structured diagnostics in responses, with
stable exit codes and actionable errors. An editor sends its displayed fingerprint
with mutations and refreshes when the context has changed.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), package and machine interface.
