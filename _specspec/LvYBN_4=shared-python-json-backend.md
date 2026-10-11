---
id: LvYBN_4=
type: requirement
parents:
- eLTZ3sg=
- apEb_pM=
- WpYvGUo=
---
# Share one Python validation and mutation backend

Expose graph operations through a reusable Python library and versioned JSON CLI.
Host adapters invoke the CLI without a shell; they do not implement separate schema
validation, withdrawal rules or Markdown mutation planning. API 3 exposes api_version,
ok, result and structured diagnostics, with stable exit codes and actionable errors,
without fingerprints or managed hashes. Editors refresh through watchers and optional
polling, re-read before mutations, and preserve drafts across external changes.

Origin: CONCLUSION_SPEC.md package/machine interface and the user's manual-edit
correction. Version and synchronization mechanisms remain separate choices.

## Native-document persistence correction

The later user-authorized native-document conclusion revises Python-only persistence for ordinary VS Code file saves. Python now also exposes non-writing overlay reads and Markdown edit plans; adapters still do not fork schema/DAG/withdrawal rules or serialization. VS Code applies those plans to its TextDocuments and owns native persistence/recovery; these saves are not the managed writer transaction. Explicit CLI/Electron operations retain that writer. This is a scoped revision of the earlier canonical-mutation sentence, not a claim that native saves acquire locks/journals.
