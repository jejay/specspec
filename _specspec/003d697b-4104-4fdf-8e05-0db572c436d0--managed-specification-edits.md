---
id: 003d697b-4104-4fdf-8e05-0db572c436d0
type: requirement
parents:
- b8983d8c-3dc0-4588-b74f-17721bfc4f5c
---
# Recommend tool-managed specification edits without forbidding manual edits

The command-line tool and visual editor are the recommended ways to change the
specification graph. The visual editor uses the shared backend rather than a
separate canonical file-writing mechanism. Manual edits to canonical Markdown are
permitted and validated on their actual contents, not rejected for their provenance.

Origin: INTENTION_SPEC.md originally required tool-managed changes; the user's
later consenting-adults correction explicitly permits manual edits and removes
fingerprinting and managed_hash enforcement. The original source remains unchanged.
