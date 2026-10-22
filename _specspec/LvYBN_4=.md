---
id: LvYBN_4=
type: requirement
parents:
- apEb_pM=
- WpYvGUo=
---
# Share one Python domain library and versioned JSON CLI

Use a reusable Python backend for schema validation, DAG rules, Markdown planning,
workspace transactions, Git snapshots and source-region operations. Host adapters
invoke it using shell-free argument arrays and bounded UTF-8 stdin/output.

API 6 responses contain `api_version`, `ok`, `result` and structured diagnostics.
Exit codes are 0 for success, 1 for validation/rejected actions and 2 for invocation
or I/O failure. JSON stdout contains one machine-readable envelope. Body input
supports UTF-8 files and `-` stdin; updates replace an explicitly supplied parent
list. Native editor operations return non-writing overlays/plans; host documents
own their persistence. Managed project/Electron saves use the transaction writer.

Canonical node format is 7. Compact structured presentation and shared host
read operations follow the compact-interface conclusions; native planning and
managed persistence retain their separate owners.
