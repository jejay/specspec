---
id: 407b1a12-8984-4c99-9b7f-b920da33e31b
type: requirement
parents:
- 1fb70961-678b-4c03-a58c-8bcc98345501
- aee203cc-e68a-4b0d-af18-9920e5303e49
- 003d697b-4104-4fdf-8e05-0db572c436d0
---
# Validate the repository graph as part of development checks

Run this repository's installed validator against its own `_specspec` directory in
CI, with warnings treated as failures so source references cannot silently rot.
Exercise the actual graph in tests without freezing design choices, withdrawal history, or node IDs.

Keep a discoverable graph tour, agent editing instructions, and a development
launch configuration that opens this repository in its own graph editor.

Origin: this self-hosting implementation proposal.
