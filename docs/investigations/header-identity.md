# Header identity and keyboard-save verification

This slice imports the selected optical symbol and launcher tile described in
[branding provenance](../../branding/README.md), compacts the shared header and
adds focused-form Ctrl/Command+S. The follow-up removes the linked-source file
summary beneath the toolbar while retaining node-level source cues, previews and
CLI source-change reports. [The specification tour](../own-spec.md#header-identity-and-keyboard-saving)
links the affected intentions, choices and implementation.

## Local evidence (Windows)

- Python: 565 tests passed; Ruff check and format check passed.
- Current graph and source-reference validation: 195 nodes, zero errors/warnings.
- Shared UI: 249 tests passed; VS Code adapter: 46; Electron: nine. The source-summary
  removal regression covers 0, 1, 19 and 100 source changes in both host shells,
  including retained diagnostics and node badges.
- Complete installed Electron and VS Code host suites passed against disposable
  clones of the independent Gantt bundle. New probes use real CDP Ctrl+S from the
  binding editor and verify canonical saved text, not merely a sent message.
  Header probes verify symbol-only identity, adjacent revision context, accessible
  Refresh and host-specific project-picker presence. Existing native-file checks
  cover VS Code Save/undo/redo, split synchronization and document repair.
- A separate real Electron screenshot was visually inspected: the optical symbol
  is legible at 24px, revision follows it directly and Refresh is icon-only.
- Local import digests match the final source files exactly. The optical SVG's
  non-text Git attribute preserves those bytes across checkout platforms.

The first concurrent VS Code smoke run passed the new header/keyboard probes, then
failed the existing 250%-headline comparison with an empty computed font size
versus 13px. The complete isolated rerun passed without code or assertion changes.
This is recorded as an unresolved intermittent test observation, not evidence that
concurrent host/DOM stability is guaranteed. Logs and its diagnostic profile remain
preserved locally under `.specspec/local/` and the host-reported temporary directory.

These checks do not qualify physical macOS Command gestures or Linux execution.
Command+S has synthetic-event coverage. No release installation or package
publication was performed. The authorized commit uses exact-index graph/source
validation; Git records its final contents and the preserved owner deletion.
