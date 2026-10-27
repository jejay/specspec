"""Concise static task help; no project or input is opened to display it."""

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
    """Scope formatting to all command and subgroup help."""
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

    Run commands inside the intended project, like Git. Direct Markdown nodes in
    .specspec/ record goals, conclusions and implementation links; .specspec/local/
    holds ignored runtime state. NODE_ID and PARENT_ID mean full IDs, including the
    final '='. Start with query in an existing project, or init in a new one.

    \b
    Read and review:
      specspec query --max-distance 2
      specspec query NODE_ID --max-distance 0 --with-ancestors --human
      specspec diff --with-context
      specspec check

    \b
    Create and edit:
      specspec init -m "# Product goal"
      specspec add --parent PARENT_ID -m "# Conclusion" -m "Explain why."
      specspec update NODE_ID --replace "old wording" "new wording"
      specspec delete NODE_ID --dry-run

    Messages are literal Markdown; absent messages use UTF-8 stdin. Combine only
    add/update/delete for one candidate and recoverable transaction. New nodes can
    have local --as names; --parent '$goal' references an add named goal. Quote '$'
    for your shell. Editing flags apply to the whole invocation.

    Receipts group full IDs under Added, Modified, Deleted or Unchanged; previews
    use Would add/modify/delete. Invalid intermediate graphs remain editable;
    --require-valid checks the final candidate, while check stays strict.
    Node writes retain local newline style and append only a missing final newline,
    preserving trailing blank lines. Reads stay non-writing. Init initializes Git
    and creates or appends AGENTS.md; nothing stages, commits or installs hooks.
    Run COMMAND --help for task-specific examples and safety details.
    """,
    "init": """Initialize Git and a graph with one manifesto: the product's core goal.

    Requires Git. Creates .specspec/ and a randomly identified manifesto.
    Creates AGENTS.md or appends the packaged guide after existing instructions.
    Unsafe targets are rejected. Existing graphs are never overwritten; use query/update.

    -m/--message is literal Markdown, not a filename. Repeat it for paragraphs.
    Without messages, reads UTF-8 stdin; shell redirection supplies a file.
    The body must be nonempty. No editor opens automatically.

    \b
    Examples:
      specspec init -m "Test"
      specspec init -m "# Plan a trip" -m "Agree on a schedule."
      specspec init < manifesto.md

    Reports Added: NODE_ID. Keep the full ID, including '=', for parent arguments.
    Node files are limited to 1 MiB; shell argument limits can be smaller.
    Initialization does not stage, commit, configure Git identity or install hooks.
    Recover interrupted graph writes before retrying; Git metadata remains.
    """,
    "query": """Read specifications, relationships and revision-change context.

    No selection reads the complete graph. NODE_ID includes that node and its
    descendants; --max-distance 0 reads just it. --with-ancestors adds every parent
    path needed to understand the selected conclusions, printing shared records once.

    Comparisons default to fresh Git HEAD versus saved workspace files.
    --base/--target choose refs; target also accepts workspace. Deleted records are
    historical context, not current justification. Unsaved buffers are not read.

    \b
    Examples:
      specspec query --max-distance 2
      specspec query NODE_ID --max-distance 0 --with-ancestors --human
      specspec query NODE_ID
      specspec query --base main~1 --target main
      specspec query --issues --with-ancestors

    Default bodies occupy one compact line; --human keeps logical body lines and
    lists sources separately. Use diff for canonical-text patches. Normal headers
    omit internal schema details.

    Metrics are relative to NODE_ID, or the manifesto when omitted. Min-distance
    uses the shortest path; max-distance the longest. Integer distance limits include
    nodes at or below that distance. Influence counts nodes including themselves
    plus unique descendants; integer limits select at or above that count.
    Percentages choose a population share, rounded up: nearest first for distances,
    highest first for influence, with full-ID ties. Criteria combine by UNION,
    not intersection; ancestors are added afterwards without consuming quotas.

    \b
    Selection examples:
      specspec query --max-distance 50%
      specspec query NODE_ID --influence 5
      specspec query --min-distance 25% --influence 25% --with-ancestors

    --issues selects faults and potential downstream effects. Invalid graphs stay
    inspectable; incomplete evidence can return nonzero status. Validity is not
    semantic proof.

    --raw instead reads exact documents, including malformed Markdown. Select an ID
    or direct .specspec/ID.md --path; --target chooses a commit and --staged the index.
    Raw reads reject unrelated selection/comparison flags. Non-UTF-8 uses Base64.

    \b
    Repair examples:
      specspec query NODE_ID --raw
      specspec query --raw --path .specspec/NODE_ID.md --staged

    Read-only: no edits, commits or fetching Git objects.
    """,
    "add": """Create a conclusion or implementation node.

    Supply Markdown with -m/--message, or omit messages to read UTF-8 stdin.
    Repeated --parent IDs are its immediate justifications. Default type is
    requirement; implementations are leaves justified by requirements. IDs and
    filenames are generated independently of headings.

    \b
    Examples:
      specspec add --parent PARENT_ID -m "# Clear timeline" -m "Explain why."
      specspec add --type implementation --parent REQUIREMENT_ID < implementation.md
      specspec add --as goal --parent PARENT_ID -m "# Goal" \\
        add --parent '$goal' -m "# Detail" --require-valid

    Messages are literal; repeated values join with one blank line. --as names a
    new node only within this invocation, including forward parent references.
    Aliases are not stored and cannot be update/delete targets.

    Combine add/update/delete for one candidate. --dry-run previews without writes;
    preview IDs are not reservations. --require-valid checks the whole final graph.
    Otherwise invalid intermediate relationships can be saved with diagnostics;
    schema, path and transaction safeguards remain. Receipts group generated IDs
    under Added, or Would add for previews. Node files stay within 1 MiB; invocation
    body material is bounded separately. No staging, commits or linked-code edits.
    """,
    "update": """Change an existing node's body, parents or source references.

    NODE_ID is the full existing ID, including '='. Messages replace the WHOLE body;
    --replace OLD NEW edits selected passages. Without either, reads UTF-8 stdin.
    Empty stdin with explicit metadata edits preserves the body. Interactive
    metadata-only updates do not wait for text. Explicit empty -m is still an edit.

    \b
    Examples:
      specspec update NODE_ID -m "# Revised heading" -m "Complete replacement."
      specspec update NODE_ID < revised.md
      specspec update NODE_ID --replace "old wording" "new wording"
      specspec update NODE_ID --replace "remove this sentence" ""
      specspec update NODE_ID --parent FIRST_ID --parent SECOND_ID --require-valid

    OLD must identify exactly one passage across supported layouts. Line endings
    compare equally; ordinary prose soft wraps can match spaces. Words, other
    whitespace and Markdown structure matter. Pairs address the SAME original body,
    must not overlap and do not cascade. NEW keeps literal content with target
    newline encoding; empty NEW deletes. Ambiguity or analysis limits reject the
    whole invocation. Replacements do not read stdin.

    --parent REPLACES the complete parent list; it does not append. Repeat every
    parent to retain; omission keeps parents. Body and parent edits can combine.
    The manifesto stays parentless; source arrays belong to implementations.

    Combine add/update/delete for one candidate, with one step per existing ID.
    --dry-run writes nothing; --require-valid checks the whole final graph.
    Saved logical changes are Modified, equal text Unchanged; previews use Would
    modify. Locks, exact-byte checks and recovery remain enforced independently of
    graph validity. No Git staging, commit or linked-source edits.
    """,
    "delete": """Remove exactly the named specification node files.

    Supply full NODE_IDS, including '='. Descendants are NOT selected automatically:
    their files and parent declarations remain, including missing-parent references.
    The manifesto is protected. Linked implementation code stays untouched.

    \b
    Workflow:
      specspec delete NODE_ID --dry-run
      specspec delete FIRST_ID SECOND_ID --dry-run
      specspec delete NODE_ID --yes
      specspec query --issues --with-ancestors
      specspec diff --with-context

    Preview reports Would delete; execution reports Deleted. Missing references,
    potential survivor scope and resulting validity/completeness remain explicit.
    Affected scope invites reconsideration, not automatic removal.

    Selected uncommitted files, staged changes or unavailable Git status warn.
    Interactive terminals request consent; warned noninteractive use needs --yes.
    Consent never bypasses manifesto, path, byte or validity safeguards.

    Default edits may leave invalid relationships. --require-valid checks the WHOLE
    final candidate before writes. Chains can repair survivors with explicit updates;
    editing flags, consent and recovery apply invocation-wide. Files are journaled
    for interrupted-write recovery, not permanent Undo. Use Git/backups for later
    restoration. HEAD-based deleted context survives staging and vanishes on commit.
    Reviewed plans remain a standalone integration operation.
    """,
    "check": """Validate graph structure and optional implementation source links.

    Checks the whole selected graph and reports node/error/warning counts. An
    optional NODE_ID focuses --sources inspection, not graph validation. Passing
    checks establishes consistency, not correctness of the owner's intent.

    \b
    Examples:
      specspec check
      specspec check --sources
      specspec check IMPLEMENTATION_ID --sources
      specspec check --staged --sources --warnings-as-errors
      specspec check --ref main~1

    Default input is saved workspace files. --staged checks exact index blobs,
    including partial staging; working-tree checks cannot substitute before commit.
    --ref selects an immutable commit. Do not combine it with --staged. --sources
    resolves code ranges and blob retention in the same selected version.

    Completed graphs have one root, legal parents, no cycles and no redundant
    direct parent already implied indirectly. Identity, schema and safe-path checks
    remain strict. --warnings-as-errors makes warnings fail too.
    Read-only: no repair, staging, commit or hooks. Use query --issues and deliberate
    edits. Exit 0 means valid, 1 failed checks, 2 invocation/I/O failure.
    """,
    "diff": """Review specification changes and relationship context.

    BASE defaults to fresh HEAD. Omit TARGET for saved workspace files; supply it
    for two commits/branches without checkout. Linked-source impact is separate;
    ordinary git diff supplies implementation-code patches.

    \b
    Examples:
      specspec diff
      specspec diff main~1 main
      specspec diff --with-context
      specspec diff --node NODE_ID
      specspec diff --summary

    Default output includes complete logical canonical-text hunks: bindings,
    metadata, comments, whitespace, EOF and added/deleted nodes. LF/CRLF/CR encoding
    alone is equivalent. Patches use LF; query --raw retains physical evidence.
    --summary explicitly abridges output. Relationship changes identify both ends;
    linked-code effects stay distinct from directly modified specifications.

    --with-context adds deduplicated old/current justifications, ancestors, broken
    references and potential cause paths. Repeated --node focuses that context and
    implies --with-context. Evidence does not establish motives or correctness.

    Invalid/unavailable revisions stay explicit. Incomplete comparisons can retain
    useful evidence with nonzero status. Output budgets fail rather than truncate.
    No changes to files, checkout, index, refs or linked code; no missing-object fetch.
    """,
    "recover": """Roll back an interrupted managed write while preserving external edits.

    Recognizes original/intended/absent states, restores originals and removes new
    files. Original graphs may remain invalid.

    \b
    Examples:
      specspec recover
      specspec recover --force-lock

    Keep .specspec/local/ until recovery finishes. Unknown intervening bytes are
    protected: inspect and back them up instead of deleting recovery state.
    --force-lock clears a stale lock only after you confirm no writer is running;
    it never authorizes overwriting unknown text. Successful writes retain no Undo
    journal. Initialization rollback restores amended instructions but keeps Git
    metadata. No staging, commits or linked-code deletion.
    """,
    "sources": """Inspect and maintain implementation-to-code links.

    Links cite whole files or Git-anchored inclusive ranges. Source numbers are
    1-based; links provide context, not proof.

    \b
    Examples:
      specspec sources show IMPLEMENTATION_ID --source 1
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --dry-run

    show is read-only. capture/reanchor deliberately update CURRENT implementation
    metadata, never linked code. Preview with --dry-run. These commands stay
    standalone; only add/update/delete can chain. Use SUBCOMMAND --help for details.
    """,
    "sources show": """Resolve source links or preview a linked region's actual text.

    Omit NODE_ID for all links; supply it for one node. --source N previews its Nth
    source with nearby lines and mapping outcome. Select an implementation.

    \b
    Examples:
      specspec sources show
      specspec sources show IMPLEMENTATION_ID --source 1
      specspec sources show IMPLEMENTATION_ID --ref main~1
      specspec sources show --staged

    Defaults read saved declarations and code. --staged selects the index; --ref a
    commit, for both. Uncertain mapping can preview original anchored text and says
    so, rather than inventing a current location. Missing objects, ambiguity,
    binary/LFS data and limits stay explicit. Read-only. Use capture for new anchors
    and reanchor for deliberate moves.
    """,
    "sources capture": """Record an implementation's link to committed or staged code.

    NODE_ID selects a CURRENT implementation; PATH is project-relative code, not
    binding text. Supply inclusive 1-based START:END ranges; repeat --range for
    separate regions in one file/reference.

    \b
    Examples:
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict --dry-run
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 10:25 --mode strict
      specspec sources capture IMPLEMENTATION_ID src/main.py --range 1:80 --mode expanding --staged

    Strict reports internal changes as conflicts. Expanding absorbs internal
    additions/contained replacements, excluding outer-boundary insertions and gaps.
    Modes describe permitted evolution, not confidence or approval.

    Code defaults to committed HEAD; --ref chooses another commit and --staged exact
    index code. Unstaged code is not an immutable anchor. Unless --dry-run, metadata
    changes through the managed writer; code and Git staging/commits stay untouched.
    Retain blobs through Git and check --staged --sources before committing.
    """,
    "sources reanchor": """Replace an existing region anchor with a deliberate new Git anchor.

    Select a CURRENT implementation and --source N (1-based). Captures trustworthy
    ranges mapped into HEAD. For uncertain/conflicting code, inspect and supply
    explicit --range START:END replacements; this does not certify fulfillment.

    \b
    Examples:
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --range 12:30 --dry-run
      specspec sources reanchor IMPLEMENTATION_ID --source 1 --range 12:30

    --ref selects a commit, --staged the index; otherwise HEAD. Retains mode and
    descriptive symbol. Whole-file references need capture to acquire an anchor.
    --dry-run previews; execution updates only the selected node's sources through
    the managed writer. Linked code, staging and commits stay untouched. Deliberate
    blob retention, graph validity and physical transaction safeguards still apply.
    """,
    "spotlight": """Attach checkout-local messages to nodes and comparison context.

    Records one message, unique full IDs and revision context for UIs and agents.
    Data lives in ignored .specspec/local/, not the canonical graph. Messages are
    neither approval states nor node copies.

    \b
    Examples:
      specspec spotlight add NODE_ID "Reconsider this conclusion."
      specspec spotlight show
      specspec spotlight flush --yes

    add records an immutable message; show resolves members and drift; flush clears
    retained records with explicit consent. Spotlight IDs identify messages, not
    nodes. Use SUBCOMMAND --help for comparison defaults and consequences.
    """,
    "spotlight add": """Attach one local message to nodes in a comparison.

    Start with full NODE_ID values, including '='; finish with a quoted MESSAGE.
    Supply 1-500 nonblank characters. IDs can be added, changed, deleted or unchanged
    members visible on either side. No color argument is needed.

    \b
    Examples:
      specspec spotlight add NODE_ID "Why this conclusion?"
      specspec spotlight add FIRST_ID SECOND_ID "Consider these together."
      specspec spotlight add NODE_ID "Earlier intent" --base main~2 --target main

    Defaults follow live HEAD/workspace. Explicit refs pin commits; target workspace
    stays live. Sparse uncommitted-state hints support drift warnings without copied
    node bodies. Writes local metadata only, not buffers, specifications, code or
    Git state. Records remain until explicit flush; corrections use new messages.
    """,
    "spotlight show": """Read spotlight messages and resolve their comparison members.

    Omit SPOTLIGHT_ID for all records; supply a message ID for one. Shows messages,
    comparisons, member statuses and drift. Message IDs are not node IDs.

    \b
    Examples:
      specspec spotlight show
      specspec spotlight show SPOTLIGHT_ID

    A/M/D/= mean added/modified/deleted/unchanged in that record's comparison.
    Unavailable members stay explicit. Drift means text/context changed since
    capture, not message editing or approval. Historical text remains
    context. This read changes neither documents, nodes, spotlights nor Git state.
    """,
    "spotlight flush": """Clear every retained spotlight in this checkout.

    Removes messages for both UIs, keeping specifications, code, history and recovery.

    \b
    Examples (review first):
      specspec spotlight show
      specspec spotlight flush
      specspec spotlight flush --yes

    Interactive terminals request confirmation; noninteractive use requires --yes.
    No individual deletion or automatic expiry. Messages stay immutable until this
    whole-store operation. Review before confirming; no staging or commit.
    """,
    "api": """Private integration transport; ordinary users should use everyday commands.

    Reads a bounded UTF-8 request from stdin. One-shot mode consumes one request;
    --stream reads one request per line and emits a corresponding response.
    Protocol details belong to the integration guide, not normal authoring.

    \b
    Example:
      specspec api < request.json

    Operations read current context, plan native edits, preview/capture sources and
    inspect/create/flush local spotlights. Plans do not save native documents, and
    this is not a bulk node-mutation endpoint. Hosts retain their communication and
    persistence owners. Input is limited to 16 MiB. Malformed or incompatible frames
    fail explicitly; delivered operations and graph validity remain separate facts.
    Help never consumes stdin or opens a project.
    """,
}
