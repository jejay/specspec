<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/jejay/specspec/main/branding/specspec-logo-dark.png">
  <img src="https://raw.githubusercontent.com/jejay/specspec/main/branding/specspec-logo-light.png" alt="SpecSpec" width="640">
</picture>

# SpecSpec

**Keep the intention. Reconsider the solution. Know what the code is meant to do.**

An agent can produce working code quickly. Keeping track of *why this solution*,
which assumptions came from whom, and what should survive a change of approach is
harder. A long conversation is a poor place to keep that understanding.

SpecSpec connects **your intentions, revisable choices and implementation** in a
Git-versioned Markdown graph. Read and edit it through a small CLI, your own VS Code
instance, or a standalone desktop window. People and coding agents use the same
specification, with full explanations rather than a pile of unchecked task titles.

> Engineering is on the spectrum now

Hands-on engineering and delegated agent work are not a binary choice. You can
direct one decision carefully and leave the next open. SpecSpec makes that reasoning
visible; it does not choose your level of delegation or run an agent for you.

**0.1 is an early, local-first release.** The CLI and both graph editors are usable;
expect rough edges and changing interfaces. There is no hosted service, Marketplace
listing, automatic coding agent, or correctness guarantee. Your specification stays
in your repository. [Scope and release notes](CHANGELOG.md) · [Install](docs/install.md)

## A spectrum, not a checklist

```text
Manifesto         Help a small team understand its plan
  Requirement     Make timing and dependencies understandable
    Requirement   Present tasks on an interactive timeline
      Requirement Use a local browser view with explicit JSON export
        Implementation  Explain the view and link its actual source/tests
```

The timeline is a choice serving an intention, not the intention itself. A later
approach can replace it without quietly losing the goal. One conclusion can serve
several intentions: the structure is a rooted DAG, not just a hierarchy.

- **Read the why.** Query a decision and every ancestor that justifies it.
- **Revise deliberately.** Keep consequential choices separately addressable;
  compare specification changes with Git and inspect potential downstream effects.
- **Connect the realization.** Implementation explanations link to files or tracked
  source regions, with explicit uncertainty when those links stop being reliable.
- **Work visually or in the terminal.** Both UIs share one renderer and Python
  backend. The CLI works well with an agent's existing shell tools.

Graph position is a relationship, not an approval or confidence score. Passing
validation establishes structure, not whether a product actually meets its purpose.

## Choose how to use it

| Entry point | What you install | What you need |
| --- | --- | --- |
| **CLI** | Global isolated Python tool | Python 3.11+, uv or pipx; Git for versioned workflows |
| **VS Code** | Build a VSIX, install into your ordinary editor | Global CLI, VS Code 1.90+, Node 22.12+ and npm 10+ for building |
| **Desktop** | Run from source or build a portable Electron app | Global CLI and Git; Node/npm for source builds |

The CLI needs **no Node, VS Code or Electron**. The UIs use `specspec` on PATH by
default; neither bundles a second Python runtime. Desktop targets Windows/Linux;
macOS users can use the CLI and VS Code. See [platform qualification](docs/platforms.md).

### Install the CLI globally

From a checkout of this monorepo:

```sh
git clone https://github.com/jejay/specspec.git
cd specspec
uv tool install .
specspec --version
specspec --help
```

Or use `pipx install .`. Both install a user-wide command in an isolated environment,
not a dependency in every project. Restart your terminal/editor after fixing PATH
with `uv tool update-shell` or `pipx ensurepath` if necessary. No administrator or
`sudo pip` installation is needed. PyPI publication is not assumed: installation
from Git or the built wheel is documented in the [installation guide](docs/install.md).

### Use it in your own VS Code — no Marketplace

From the repository root, after installing the CLI:

```sh
npm ci
npm run package:vscode
code --install-extension dist/specspec-vscode-0.1.0.vsix
```

Reload VS Code, open your project and run **SpecSpec: Open Graph** from the Command
Palette. Or use **Extensions → … → Install from VSIX…** with that file. This is a
normal installed extension, not an F5-only development window. No package is sent
to the Marketplace. [Setup and troubleshooting](vscode/README.md)

### Run the desktop

From the repository root:

```sh
npm ci
npm run desktop
# Or open this checkout's graph directly:
npm run desktop -- --project .
```

Choose **Open project**, select your project and **Trust and Open**. The explicit
`--project` launch argument authorizes that folder instead. To create a portable
Windows/Linux package, activate the development Python environment described in
[contributing](CONTRIBUTING.md) and run `npm run package:electron`. Output is under
`dist/`. End users of the portable archive need the global CLI and Git, **not Node**.
[Desktop guide](electron/README.md)

## Start a project

In a different directory — this checkout already has a graph:

```sh
mkdir my-project
cd my-project
git init
specspec init -m "# Understand our plan" -m "Help a small team agree on timing."
specspec query --max-distance 2
```

Initialization creates `.specspec/` and a root **`AGENTS.md`** with conceptual,
working-phase and CLI guidance. An existing `AGENTS.md` entry is preserved unchanged;
review the [shipped guide](src/specspec/templates/AGENTS.md) and integrate it yourself.
Add `.specspec-local/` to your project's `.gitignore`; it holds local recovery and
spotlight state, not canonical nodes. Git initialization/staging/commits remain yours.

Copy the full manifesto ID printed by `init`, including its trailing `=`, and use
it in place of `MANIFESTO_ID` below:

```sh
specspec add --parent MANIFESTO_ID -m "# Readable timing" -m "Show task timing clearly."
specspec query NODE_ID --max-distance 0 --with-ancestors
specspec update NODE_ID --replace "task timing" "timing and dependencies"
specspec check --sources
specspec diff --with-context
```

`NODE_ID` is another full ID from the result. Messages are literal Markdown; repeat
`-m` for paragraphs. `--replace` selects unique passages while tolerating ordinary
prose wrapping and line-ending differences; inserted text remains literal. Compose
add/update/delete for one recoverable transaction. See [the CLI guide](docs/cli.md)
and each command's detailed `--help`.

The hidden `.specspec/` directory contains direct `<id>.md` nodes only. Headings,
query and the graph editor provide human discovery. Node format **7** and API **7**
are current. The 0.1 directory is `.specspec`, not the pre-release underscore name;
[upgrade notes](docs/install.md#upgrading-pre-release-workspaces) explain the boundary.

## See a project change its mind

[The Gantt example](example/gantt/README.md) has a runnable local planner and an
independent eight-revision Git history with two substantial changes of direction.
Create a real example workspace outside this checkout:

```sh
python example/gantt/history/checkout.py
```

Open the resulting folder in either UI and compare `stage/01-code` → `stage/02-spec`
or `stage/02-code` → `stage/03-spec`. Existing example clones are never reset.
The tracked `example/gantt/` folder is a snapshot, not its own Git workspace.

## Ownership and boundaries

Markdown is editable directly as well as through the tools. A completed graph is
rooted and shortcut-free; intermediate invalid graphs remain diagnosable and
repairable. Deletion removes **exactly selected files** and retains surviving
conclusions and their declarations. `--require-valid` checks a complete candidate;
`check` remains strict. There are no stored approval states or parent-review gates.

VS Code file tabs retain native Save, dirty state and undo/redo. Electron and
managed project actions use locked, original-byte-checked, recoverable writes.
Interrupted edits need `specspec recover`; this is not a universal Undo or a
power-loss-safe database. Watchers are hints, with explicit Refresh available.

The renderers load bundled assets and render project text literally. CLI execution
requires trusted host/project configuration. Source symbols are descriptive; source
tracking and passing tests supply evidence, not proof of semantic fulfillment.
Large graphs are not virtualized. Signing, installers, auto-updates and hosted
agent connectors are outside this initial release.

## Go deeper

- [Installation, upgrades and PATH](docs/install.md) · [Agent process and template](docs/agents.md)
- [CLI reference](docs/cli.md) · [Query selection](docs/query.md) · [Canvas controls](docs/node-canvas.md)
- [Graph structure](docs/graph-structure.md) · [Sources](docs/source-regions.md) · [Deletion](docs/deletion.md)
- [Invalid-state repair](docs/invalid-graphs.md) · [Native documents](docs/native-editors.md) · [Remote workspaces](docs/remote-workspaces.md)
- [Architecture](docs/architecture.md) · [SpecSpec's own graph](docs/own-spec.md) · [Brand provenance](branding/README.md)
- [Contributing and monorepo commands](CONTRIBUTING.md) · [Local release procedure](docs/releasing.md) · [MIT license](LICENSE)

## Monorepo map

| Path | Responsibility |
| --- | --- |
| `src/specspec/`, `pyproject.toml` | Python library/CLI and packaged initialization guide |
| `vscode/` | VS Code adapter and local VSIX packaging |
| `electron/` | Sandboxed desktop adapter and portable packaging |
| `graph-ui-common/` | Shared renderer, session, host ports and bundled dependency notices |
| `package.json`, `package-lock.json` | One private npm workspace, locked UI/build dependencies and root commands |
| `branding/`, `docs/` | Selected identity, onboarding and detailed guides |
| `.specspec/` | This product's own intentions, choices and implementation explanations |
| `example/gantt/` | Maintained independent history fixture and runnable example snapshot |

Source and release artifacts are built here; publishing remains an explicit owner
action. The supplied original dog artwork stays archived, while the application
and documentation use the selected Spectrum flow identity.
