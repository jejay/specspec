---
id: 6c457b0a-654e-4545-a4b4-667f467be4f3
type: requirement
parents:
- adb5a4c8-f9c5-4bcc-b38b-8584d469cf25
- ca580dc7-c7fa-48bc-91b1-59243144a0bf
- f0d0d18b-b52e-4eef-ab13-da7bedfd07a2
---
# Share one Python validation and mutation backend

Expose graph operations through a reusable Python library and versioned JSON CLI.
Host adapters invoke the CLI without a shell; they do not implement separate schema
validation, withdrawal rules or canonical file mutations. API 3 exposes api_version,
ok, result and structured diagnostics, with stable exit codes and actionable errors,
without fingerprints or managed hashes. Editors refresh through watchers and optional
polling, re-read before mutations, and preserve drafts across external changes.

Origin: CONCLUSION_SPEC.md package/machine interface and the user's manual-edit
correction. Version and synchronization mechanisms remain separate choices.
