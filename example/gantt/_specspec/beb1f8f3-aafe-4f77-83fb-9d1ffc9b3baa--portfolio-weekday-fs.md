---
id: beb1f8f3-aafe-4f77-83fb-9d1ffc9b3baa
type: requirement
parents:
- 7fd262ae-3014-4e6e-a812-92bed9926e3b
- 928060fa-c02d-46dd-b823-b002bcf41353
managed_hash: 4b2014059d96062076e5c567c456509cfe08c65852d5b64c4a049df3621a13f1
---
# Try a weekday finish-to-start prototype

Use UTC whole-day arithmetic and a topological traversal. Each successor starts on the next weekday after every predecessor finishes; duration includes its first workday. Weekends are excluded, holidays are not modeled. This tests calendar semantics before choosing a production scheduler. Origin: STORY.md, AI opening conclusion.
