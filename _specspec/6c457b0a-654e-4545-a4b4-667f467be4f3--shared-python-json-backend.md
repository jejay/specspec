---
id: 6c457b0a-654e-4545-a4b4-667f467be4f3
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- f0d0d18b-b52e-4eef-ab13-da7bedfd07a2
managed_hash: a857f779f2666e895215df904359dcad6dd2f88b5acd26b1658e26e7f51318d4
---
# Share one Python validation and mutation backend

Expose graph operations through a reusable Python library and a versioned JSON CLI.
The VS Code extension invokes that CLI without a shell; it does not independently
implement schema validation, withdrawal rules, or canonical file mutations.

Use `api_version`, `ok`, `result`, and structured diagnostics in responses, with
stable exit codes and actionable errors. An editor sends its displayed fingerprint
with mutations and refreshes when the context has changed.

Origin: [CONCLUSION_SPEC.md](../CONCLUSION_SPEC.md), package and machine interface.
