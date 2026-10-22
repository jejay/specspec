---
id: P2i_png=
type: requirement
parents:
- DG-JpDc=
- 0dvOn3A=
---
# Keep immutable spotlight metadata in a checkout-local store

Store each complete addition in .specspec-local/annotations/<shot-id>.json. This
persistent local metadata is shared by the CLI and both hosts in one checkout.
Git's local exclude protects the directory when project ignore rules require it;
refuse writes over Git-tracked local-state files.

Validate a bounded message, comparison and member list before publishing one atomic
immutable file under the cooperating workspace writer lock. Complete shot files
are the list source of truth. Protect malformed records with actionable errors;
limits reject additions rather than evicting existing records. Explicit flush
removes spotlight metadata and obsolete blob files while preserving recovery and
other local state. Publication retains ordinary lock and recovery behavior.

The public commands are spotlight add/show/flush. CLI capture reads saved files;
UI capture includes trusted native overlays and the current comparison. A spotlight
stores references and sparse workspace drift metadata, with independently generated
identity and capture time. Git owns committed node text.
