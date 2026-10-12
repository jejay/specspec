---
id: TAvql3w=
type: requirement
parents:
- f5_ViWE=
- Oou-SvU=
---
# Keep development self-reference and example Git experiments separate

Keep SpecSpec's working specification synchronized with its implementation through
SpecSpec itself. This does not require today's tools to read obsolete node schemas
in the development repository's Git history. Rejecting those revisions is expected;
do not retain overwritten schemas, old readers or compatibility functionality.

Use Gantt or similarly realistic example projects for serious end-to-end and
Git/temporal regression testing. Their working Git repositories and histories must
be independent of SpecSpec development, so opening the example and comparing its
revisions cannot accidentally select this repository's Git history or index.
Focused unit tests may use smaller independently generated current-schema projects.

Whenever the node schema changes, rewrite the entire maintained example history,
including all retained revisions, branches, tags and withdrawn nodes, as though
the example had always been developed with the current SpecSpec version. Updating
only the final working tree or adding a migration commit is insufficient. Preserve
plausible graph emergence, separately justified conclusions, meaningful revisions,
withdrawn reasoning and spec-before-code boundaries; regenerate actual verification
and update fixture references. Do not rewrite unrelated SpecSpec development history.

Fabricated AI conversations are not required. A plausible ordered construction and
revision of the specification tree/DAG is sufficient. Optional fictional narrative
must be labeled and must not masquerade as authorization, executed checks or real
CLI evidence.

Origin: the user's explicit development/example separation, recurring full-history
rewrite and no-required-fictional-conversation clarification in this conversation.
