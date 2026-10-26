"""Task-oriented static help: reading help never opens a project or payload."""

import textwrap

import click


class HelpfulFormatter(click.HelpFormatter):
    """Wrap prose without splitting option spellings; preserve example blocks."""

    def write_text(self, text):
        indent = " " * self.current_indent
        paragraphs = []
        for paragraph in text.split("\n\n"):
            paragraph = paragraph.strip("\n")
            if not paragraph:
                continue
            if paragraph.lstrip().startswith("\b"):
                block = textwrap.dedent(paragraph.lstrip()[1:].lstrip("\n"))
                paragraphs.append("\n".join(indent + line for line in block.splitlines()))
            else:
                paragraphs.append(
                    textwrap.fill(
                        " ".join(line.strip() for line in paragraph.splitlines()),
                        width=self.width,
                        initial_indent=indent,
                        subsequent_indent=indent,
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                )
        self.write("\n\n".join(paragraphs) + "\n")


def install_help(command):
    """Keep formatting scoped to these commands, including subgroups and hidden API."""
    original = command.get_help

    def get_help(ctx):
        ctx.formatter_class = HelpfulFormatter
        return original(ctx)

    command.get_help = get_help
    if isinstance(command, click.Group):
        for child in command.commands.values():
            install_help(child)


HELP = {
    "root": """Manage a product's intention-conclusion specification graph.

    A graph lives in .specspec/ inside your project. Its Markdown nodes describe
    goals, conclusions and implementation links. Use the seven everyday commands
    below to read, edit, validate and review it. Nothing stages or commits Git
    changes for you.

    Start with query to read an existing graph. Use init only for a project that
    does not yet have .specspec/. NODE_ID and PARENT_ID in examples mean actual
    full node IDs, including the final '='. Put --root PROJECT before the command
    to choose a project explicitly; otherwise discovery searches the current
    directory and its parents.

    \b
    Read and review:
      specspec query --max-distance 2
      specspec query NODE_ID --max-distance 0 --with-ancestors --human
      specspec diff --with-context
      specspec check

    \b
    Create and edit:
      specspec init -m "# Product goal" -m "Explain the desired outcome."
      specspec add --parent PARENT_ID -m "# Conclusion" -m "Explain why."
      specspec update NODE_ID --replace "old wording" "new wording"
      specspec delete NODE_ID --dry-run

    Combine only add/update/delete in one invocation for one complete candidate
    and one recoverable transaction. New nodes can have local --as names;
    --parent '$goal' references an add named goal (quote '$' for your shell).
    --dry-run, --require-valid, --yes and --json then apply to the whole invocation.
    Other commands are standalone.

    Default results are readable text. Editing receipts group full node IDs under
    Added, Modified, Deleted or Unchanged, with comma-separated IDs and no padding.
    Previews use Would add/modify/delete. These are invocation effects, not Git status.
    Add --json for structured API-7 output. Node comparisons ignore newline encoding;
    existing-document writes retain local style and new nodes use LF. Git settings
    and attributes stay untouched. Spaces, blank lines and EOF termination matter.
    Editing can succeed while reporting an invalid intermediate graph; check is
    strict, and --require-valid checks the whole final candidate before writes.
    Run COMMAND --help for arguments, examples, defaults and safety details.
    Multi-line/quoted examples use Bash/Git Bash conventions; other shells need
    their own quoting. Large-body integration input is described in command help.
    """,
    "init": """Create a new graph with one manifesto: the product's core goal.

    Run this in a new project's directory, or select that directory with the root
    --root option. Creates .specspec/ and a randomly identified manifesto file.
    Creates a root AGENTS.md with graph/process/CLI guidance when that name is free;
    existing instructions are preserved unchanged. Refuses to overwrite an existing
    graph; use query and update there instead.

    -m/--message is literal Markdown text, not a filename. Repeat it to join
    paragraphs with one blank line. Logical line boundaries, Unicode and whitespace
    are preserved; new-node storage uses LF. The body must be nonempty.
    No editor opens automatically.

    \b
    Examples:
      specspec init -m "# Plan a trip" -m "Help friends agree on a schedule."
      specspec --root ./my-project init -m "# Product goal"

    Output reports Added: NODE_ID for the first node. Keep the full ID, including
    '=', for future --parent arguments. Creation validates the complete initial
    graph and does not stage, commit or install hooks.

    Integration: --body FILE reads UTF-8 body text; --body - reads stdin. Choose
    that input or messages, not both. It remains available for large bodies and
    existing host tooling, without filename autodetection. Node files are limited
    to 1 MiB; shell/OS argument limits may be much smaller.
    """,
    "query": """Read specifications, their relationships and revision-change context.

    With no ID or selection options, reads the complete graph. NODE_ID starts at
    that node and includes its descendants. To read exactly one node, add
    --max-distance 0. Add --with-ancestors to include every parent path needed to
    understand the selected conclusions. Shared records are printed once.

    Every normal query compares a base and target: fresh Git HEAD versus saved
    workspace files by default. Deleted base records remain historical context,
    not current justification. --base/--target select other commits or branches;
    only --target also accepts the special value workspace. Unsaved editor buffers
    are not read by this CLI.

    \b
    Common examples:
      specspec query --max-distance 2
      specspec query NODE_ID --max-distance 0 --human
      specspec query NODE_ID --max-distance 0 --with-ancestors --human
      specspec query NODE_ID
      specspec query --base main~1 --target main
      specspec query --issues --with-ancestors

    Default bodies occupy one compact line; --human preserves logical body lines
    and lists sources separately. --json returns structured records, selection
    metadata and change facts. To see exact file patches, use diff instead.

    Selection metrics are relative to NODE_ID (or the manifesto when omitted).
    min-distance means the shortest parent-to-child path; max-distance means the
    longest. Integer distance limits include nodes at or below that distance.
    Influence counts the node itself plus unique descendants; an integer includes
    nodes at or above that count. A percentage chooses that share of the reachable
    population, rounded up: nearest first for distances, highest first for influence,
    with full-ID tie breaking. Several criteria are combined by UNION, not intersection.
    Ancestors are added afterwards and do not consume a percentage quota.

    \b
    Selection examples:
      specspec query --max-distance 50%
      specspec query NODE_ID --influence 5
      specspec query --min-distance 25% --influence 25% --with-ancestors

    --issues selects structural faults and potential downstream effects, rather
    than metrics. Invalid graphs remain inspectable; unavailable comparisons or
    incomplete scope are reported explicitly. Useful incomplete results can have
    nonzero exit status. Structural validity does not establish semantic intent.

    --raw is a separate literal-document read for repair, including malformed
    frontmatter, body whitespace and line endings. Select a full ID or a direct
    .specspec/ID.md --path. --target chooses a committed revision; --staged reads
    exact index bytes and requires --raw. Other comparison/selection/presentation
    flags do not combine with raw reads. Non-UTF-8 bytes are returned as Base64.

    \b
    Repair examples:
      specspec query NODE_ID --raw --json
      specspec query --raw --path .specspec/NODE_ID.md
      specspec query NODE_ID --raw --staged --json
      specspec query NODE_ID --raw --target main~1 --json

    Read-only: never edits, stages, commits or fetches missing Git objects.
    Integration --max-bytes N bounds the complete UTF-8 output and fails rather
    than truncating records.
    """,
    "add": """Create one new conclusion or implementation node.

    Supply its complete Markdown body with -m/--message and its immediate
    justifications with repeated --parent. The default type is requirement.
    An implementation node is a leaf justified by requirement nodes. IDs are
    generated by the tool; headings do not determine filenames.

    \b
    Examples:
      specspec add --parent PARENT_ID -m "# Clear timeline" -m "Explain the goal."
      specspec add --type implementation --parent REQUIREMENT_ID -m "# Build the view"
      specspec add --as goal --parent PARENT_ID -m "# Goal" \\
        add --parent '$goal' -m "# Detail" --require-valid

    Each -m is literal text; repeated messages join with exactly two newlines.
    --as gives this new node a local name for parent references in the same
    invocation, including forward references. It is not stored in the node.
    Configure a new node completely in its add step; aliases are parent references,
    not later update/delete targets.

    Combine with add/update/delete for one candidate and transaction. --dry-run
    previews without canonical writes; preview IDs are not reservations.
    --require-valid rejects an invalid complete result before writes. Without it,
    a structurally invalid intermediate graph can be saved with diagnostics;
    document schema, path safety and transaction safeguards still apply.

    Output groups generated full IDs under Added (Would add for previews), with
    alias mappings when requested and potential affected scope.
    Git staging/commits and linked code are untouched.
    Integration --body FILE|- is an alternative UTF-8 file/stdin body source;
    --parents-json and --sources are advanced complete-field inputs. At most one
    chained body can consume stdin. Node files stay within 1 MiB; supplied body
    material and arguments have separate 16 MiB bounds and smaller OS limits.
    """,
    "update": """Change an existing node's body, parents or source references.

    NODE_ID is the complete existing ID, including '='. Omitted fields stay
    unchanged. Choose exactly one way to edit body text: message paragraphs replace
    the WHOLE body; repeated --replace OLD NEW edits selected original passages;
    integration --body FILE|- reads a whole replacement body from a file/stdin.

    \b
    Examples:
      specspec update NODE_ID -m "# Revised heading" -m "Complete replacement body."
      specspec update NODE_ID --replace "old wording" "new wording"
      specspec update NODE_ID --replace "remove this sentence" ""
      specspec update NODE_ID --parent FIRST_ID --parent SECOND_ID --require-valid
      specspec update NODE_ID --replace "old phrase" "new phrase" --dry-run

    Replacement OLD must identify exactly one passage across supported newline
    layouts. Line endings compare equally; ordinary prose soft wraps can match
    spaces. Words, other whitespace and Markdown structure remain significant.
    Multiple pairs address the SAME original body and must not overlap: they do
    not run sequentially on preceding insertions. NEW keeps literal content; its
    newline encoding follows the target document. Empty NEW deletes the passage.
    Ambiguity rejects the whole invocation rather than
    choosing an exact-layout occurrence over another wrapped one. Unselected text
    remains unchanged; analysis limits reject explicitly, not approximately.

    --parent REPLACES the complete parent list; it does not append one parent.
    Repeat every parent that should remain. Omitting it keeps current parents.
    The manifesto keeps empty parents; source arrays belong to implementations.
    Parents and body edits can be supplied together.

    Combine with add/update/delete for one complete candidate. Each existing ID
    receives one step; use repeated replacement pairs within that update for
    several passages. --dry-run writes nothing; --require-valid checks the entire
    final graph. Invalid intermediate graphs remain editable with diagnostics,
    while schema, locks, original-byte checks and recovery stay enforced.
    Output groups full IDs under Modified, or Unchanged when logical text matches.
    Previews use Would modify; Unchanged stays Unchanged. These describe this
    invocation relative to saved contents, not Git status. No Git staging or commit.

    Integration: --body FILE|- reads UTF-8 instead of messages/replacements;
    --parents-json '[]' explicitly clears parents for an invalid intermediate;
    --sources JSON replaces the complete implementation source array. These are
    explicit field inputs, not filename/text guessing. Body input limits and
    smaller shell/OS argv limits still apply.
    """,
    "delete": """Remove exactly the named specification node files.

    NODE_IDS are complete IDs including '='. Repeat IDs in this command or combine
    editing steps in one invocation. The manifesto cannot be deleted. Descendants
    are NOT selected automatically: their files and parent declarations remain,
    including references to the removed parents. Linked implementation code stays.

    \b
    Safe workflow:
      specspec delete NODE_ID --dry-run
      specspec delete FIRST_ID SECOND_ID --dry-run --json
      specspec delete NODE_ID --yes
      specspec query --issues --with-ancestors
      specspec diff --with-context

    Preview lists selected full IDs under Would delete; successful deletion uses
    Deleted. Unresolved parent references, potentially affected survivors and
    resulting graph validity/completeness remain explicit. Affected scope is
    evidence for reconsideration, not permission to delete surviving conclusions.

    Selected uncommitted files (including staged changes) or unavailable Git status
    produce warnings. An interactive terminal asks for consent; JSON/noninteractive
    use needs --yes when warned. --yes supplies consent, not a bypass of schema,
    manifesto, path, byte or optional graph-validity safeguards.

    Default execution can leave an invalid intermediate graph. --require-valid
    checks the WHOLE final candidate before writes. In a chain, other updates can
    repair surviving references and all selected deletions share one consent and
    recovery scope. --dry-run, --yes, --require-valid and --json apply invocation-wide.

    Files are journaled for interrupted-write recovery, not permanent Undo. Successful
    commands clean their journals; use Git/backups for later restoration. HEAD-based
    deleted-node context persists through staging and disappears after commit.
    Integration --reviewed-plan FILE|- binds one standalone reviewed deletion;
    it is rechecked under lock and cannot be combined with editing steps.
    """,
    "check": """Validate graph structure and optionally implementation source links.

    With no ID, checks the complete selected graph. Reports node/error/warning
    counts and exits nonzero when invalid. An optional NODE_ID focuses source-link
    inspection when --sources is supplied; graph validation still covers the whole
    snapshot. Passing checks is evidence of consistency, not proof of owner intent.

    \b
    Examples:
      specspec check
      specspec check --warnings-as-errors
      specspec check --sources
      specspec check IMPLEMENTATION_ID --sources
      specspec check --staged --sources --warnings-as-errors
      specspec check --ref main~1

    The default reads saved workspace files, not unsaved buffers. --staged reads
    exact Git index blobs, including partial staging; working-tree validation is
    not a substitute for validating the graph you will commit. --ref selects an
    immutable commit snapshot. --sources also resolves ranges and checks Git blob
    retention against that same source version. Do not combine --ref and --staged.

    Schema checks include current node format, identities, parents and safe paths.
    Completed graphs have one manifesto, legal parent types, no cycles and no
    redundant direct parent already implied through another parent path. Mapping
    uncertainty remains explicit. --warnings-as-errors makes warnings fail too.

    Read-only: no repair, staging, commit, automatic reparenting or hook installation.
    Use query --issues and diff --with-context to investigate, then edit deliberately.
    Exit 0 means valid under the selected checks, 1 a failed check, 2 invocation/I/O
    failure. --json supplies structured diagnostics and validity/completeness fields.
    """,
    "diff": """Review exact specification changes and their relationship context.

    BASE defaults to fresh HEAD. With no TARGET, compare BASE to saved workspace
    files; with TARGET, compare two commits/branches without checkout. These are
    specification differences, plus separate linked-source impact, not a code diff.
    Use ordinary git diff for implementation-code patches.

    \b
    Examples:
      specspec diff
      specspec diff main~1 main
      specspec diff --with-context
      specspec diff --with-context --node NODE_ID
      specspec diff --summary
      specspec diff HEAD --json

    Default output includes all changed logical canonical-text hunks: body,
    frontmatter, comments, whitespace, EOF termination and added/deleted records.
    LF/CRLF/CR encoding alone is equivalent; patches use LF and omit newline counts.
    Use query --raw for exact physical documents. No Git settings are changed.
    --summary is deliberately abridged; it is not the default. Relationship changes
    identify both ends. Source changes and their possible requirement effects are
    separate from directly modified bindings.

    --with-context adds deduplicated previous/current justifications, ancestors,
    broken references and potential downstream cause paths. Repeated --node focuses
    that contextual evidence and implies --with-context. Context helps explain a
    change; it does not establish the owner's motive or semantic correctness.

    Invalid or unavailable revisions remain explicit. An incomplete comparison can
    return useful evidence with nonzero status; do not discard its result merely
    because ok is false. Integration --max-bytes N bounds the complete UTF-8 output
    and fails instead of truncating. This command never changes checkout, files,
    index, refs or linked code and never fetches missing objects.
    """,
    "recover": """Recover an interrupted managed write, preserving external edits.

    Use this when a previous edit reports an unfinished journal/staging area.
    Recovery recognizes original/intended file states, restores the originals and
    removes new files from the interrupted transaction. The original graph may
    itself be invalid; its diagnostics remain visible.

    \b
    Examples:
      specspec recover
      specspec recover --json
      specspec recover --force-lock

    Keep .specspec-local/ until recovery finishes. Unexpected intervening edits are
    protected: recovery refuses to overwrite unrecognized bytes. Inspect and back
    up that state rather than deleting it or blindly repeating the failed command.

    --force-lock clears a stale lock ONLY after you independently confirm no writer
    is running. It does not authorize overwriting unknown file contents. Successful
    commands have no retained Undo journal; use Git/backups for later reversal.
    Recovery does not stage, commit, delete linked code or install hooks.
    """,
    "sources": """Inspect and deliberately maintain implementation-to-code links.

    Implementation nodes may cite whole files or Git-anchored inclusive line
    ranges. These links help you inspect how code realizes a conclusion; they do
    not prove correctness. Source numbers are 1-based within one node.

    \b
    Choose a task:
      specspec sources show IMPLEMENTATION_ID
      specspec sources show IMPLEMENTATION_ID --source 1
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --dry-run

    show is read-only. capture and reanchor can update source metadata on the
    CURRENT implementation node, never the linked code. Preview with --dry-run.
    Those commands stay standalone; only top-level add/update/delete can chain.
    Run sources SUBCOMMAND --help for version selection, modes and examples.
    """,
    "sources show": """Resolve source links, or preview one linked region's actual text.

    With no NODE_ID, inspects links across the selected graph. With NODE_ID,
    inspects that node's references. --source N previews its Nth source (1-based),
    with nearby lines and explicit mapping outcome. Select an implementation node
    for a useful code preview.

    \b
    Examples:
      specspec sources show
      specspec sources show IMPLEMENTATION_ID
      specspec sources show IMPLEMENTATION_ID --source 1
      specspec sources show --staged --json
      specspec sources show IMPLEMENTATION_ID --ref main~1

    Default declarations and code come from saved workspace files. --staged reads
    index graph/code; --ref selects a commit for both. An uncertain mapping can
    preview the original anchored text and labels that fact instead of pretending
    it found the current range. Integration --graph-ref deliberately separates
    declaration revision from code revision; it is not needed for normal use.

    Read-only: no metadata, source-code or Git changes. Use capture to create an
    anchor and reanchor to deliberately move one. Missing objects, ambiguous text,
    binary/LFS files and limits remain reported uncertainty, not invented locations.
    """,
    "sources capture": """Record an implementation's link to committed or staged code lines.

    NODE_ID is a current implementation node. PATH is a project-relative code file,
    not a body input file. Give inclusive 1-based START:END line ranges; repeat
    --range for separate regions of that file. All ranges belong to one reference.

    \b
    Examples:
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict --dry-run
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 1:80 --mode expanding --staged

    --mode strict reports changes inside the selected region as a conflict.
    expanding absorbs additions and contained replacements inside the region;
    outside-boundary insertions and gaps are not absorbed. The choice describes
    what kinds of source evolution the reference permits, not confidence/approval.

    Code defaults to committed HEAD; --ref chooses another commit and --staged
    uses exact index code. Working-only unstaged code is not an immutable anchor.
    The target implementation metadata is CURRENT and is updated unless --dry-run.
    Code, Git staging and commits remain untouched. Stage/retain the referenced
    blob through Git and use check --staged --sources before committing.

    Integration --symbol TEXT is descriptive; --replace N replaces an existing
    1-based source entry instead of appending. This is separate from update's
    OLD/NEW body replacement option.
    """,
    "sources reanchor": """Deliberately replace an existing region anchor with a new Git anchor.

    Select a CURRENT implementation NODE_ID and --source N (1-based). By default,
    resolves the existing reference into HEAD and captures its trustworthy mapped
    ranges. For uncertain/conflicting mapping, explicitly supply replacement
    --range START:END values after inspecting the code. This records a decision;
    it does not silently certify that changed code still fulfills the binding.

    \b
    Examples:
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --range 12:30 --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --range 12:30
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --staged

    --ref selects committed target code; --staged selects index code; otherwise
    HEAD is used. Existing mode and descriptive symbol are retained. A whole-file
    reference has no anchor to move: use capture to create a region reference.

    --dry-run previews metadata without changing the node. Otherwise only the
    selected implementation's source array is updated through the managed writer.
    Linked code, staging and commits stay untouched; Git blob retention still needs
    deliberate staging/checking. Canonical graph and transaction rules remain.
    """,
    "spotlight": """Leave checkout-local messages attached to nodes and comparison context.

    A spotlight contains a message, unique full node IDs and the revision context
    in which you selected them. Both visual hosts and agents can read it. This is
    local communication under .specspec-local/, not canonical specification text,
    approval status, a Git commit or a saved copy of every node.

    \b
    Examples:
      specspec spotlight add NODE_ID "Please reconsider this conclusion."
      specspec spotlight show
      specspec spotlight show SPOTLIGHT_ID --json
      specspec spotlight flush --yes

    add records one immutable message. show resolves current/historical membership
    and warns about drift; flush explicitly clears local records for this checkout.
    A spotlight ID identifies the message record and is different from a node ID.
    Run spotlight SUBCOMMAND --help for details and comparison examples.
    """,
    "spotlight add": """Attach one local message to one or more nodes in a comparison.

    Start with full NODE_ID values, including '='; finish with MESSAGE, normally
    quoted so your shell passes it as one argument. The message must be nonblank
    and at most 500 characters. IDs may be added, changed, deleted or unchanged
    members visible on either side. No color argument is required.

    \b
    Examples:
      specspec spotlight add NODE_ID "Why is this the chosen conclusion?"
      specspec spotlight add FIRST_ID SECOND_ID "Consider these together."
      specspec spotlight add NODE_ID "Earlier intent" --base main~2 --target main

    Defaults follow live HEAD versus workspace. Explicit --base/--target refs are
    pinned to commits at capture. The special target workspace stays live.
    Records store sparse uncommitted-state hints, not copied node bodies, so a
    later node change can produce a drift warning rather than rewriting the message.

    Writes local spotlight metadata only. It does not save unsaved editor buffers,
    edit nodes/code, stage or commit. Spotlights remain until an explicit flush;
    later corrections can be expressed in a new message.
    """,
    "spotlight show": """Read local spotlight messages and resolve their comparison members.

    Without SPOTLIGHT_ID, lists all retained messages. With one, reads that local
    record. This ID is the spotlight/message ID, not one of its full node IDs.
    Each entry includes its message, comparison, member statuses and drift warnings.

    \b
    Examples:
      specspec spotlight show
      specspec spotlight show SPOTLIGHT_ID
      specspec spotlight show --json

    A/M/D/= describe added/modified/deleted/unchanged members in the spotlight's own
    comparison; unavailable or absent members are explicit. A drift warning means
    relevant workspace text/context differs from capture, not that the message was
    edited or that highlighting grants approval. Historical text remains context.
    This read neither saves documents nor changes nodes, spotlights or Git state.
    """,
    "spotlight flush": """Explicitly clear every retained spotlight in this checkout.

    Removes local spotlight metadata and obsolete local copies used by old local
    storage. It affects both UIs for this checkout. Specification Markdown, linked
    source code, Git history and transaction/recovery files are kept.

    \b
    Examples (review first):
      specspec spotlight show
      specspec spotlight flush
      specspec spotlight flush --yes --json

    An interactive terminal asks for confirmation. Noninteractive/JSON use requires
    --yes as explicit consent. There is no per-record deletion or automatic expiry;
    messages are immutable until this whole-store operation. No Git staging or commit.
    """,
    "api": """Private API-7 integration transport; normal users should use everyday commands.

    Reads bounded UTF-8 JSON from stdin, not a positional request filename. Every
    request has integer api_version: 7 and a supported op. Ordinary invocation
    consumes one complete request; --stream consumes one JSON request per line
    and emits one corresponding API-7 envelope per line.

    Operations are read, plan, source-view, source-capture, annotations,
    annotation-create and annotation-flush. read obtains fresh graph context;
    plan returns a non-writing native-document plan. Source capture returns form
    metadata. Spotlight operations inspect or deliberately change local records.
    This is not a bulk canonical-node mutation API or an editing-chain command.

    \b
    One-shot read (Bash):
      printf '%s' '{"api_version":7,"op":"read"}' | specspec api

    Visual hosts keep their existing stdin/channel and persistence ownership.
    Requests are limited to 16 MiB; malformed, incomplete and unsupported frames
    fail explicitly. JSON output contains api_version, ok, result and diagnostics;
    delivered operations and graph validity are separate facts. See docs/cli.md for
    complete integration fields. --help itself never consumes stdin or opens a project.
    """,
}
