---
id: afe92d9e-343f-4d90-8405-81eeaf4cfbeb
type: requirement
parents:
- 5e6030af-efb6-4123-a354-1afd099c5fce
- 51c3e963-674e-4d5d-bd7a-b8d63649e1c8
managed_hash: 244a4f34db8ac217c3c69f1b2303ef933c3cbb8f05790efb66c415c0638b237d
---
# Use an independent nested graph and real stage commits

Keep the app's graph in example/gantt/_specspec, independent of SpecSpec's
own graph. Use the installed authoritative CLI with explicit --root and fresh
--expect fingerprints. Commit each intention/choice revision before its code, then
commit a runnable implementation with linked evidence. Git records old code; retain
withdrawn canonical nodes instead of deleting or rewriting prior reasoning. A
checked-in dialogue, CLI receipts, and revision ledger connect each redirect to its
actual commits. Validate both worktrees and exact staged graphs, without installing
hooks or creating a nested Git repository. The final app is a dependency-free local
browser example, not a production service. Stage names/numbers are narrative/Git
navigation, never per-node review states.

Origin: separate implementation conclusion for the worked-example intention.
