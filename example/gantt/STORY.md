# Simulated conversation, maintained development history

The independent history in `history/gantt.bundle` was explicitly reconstructed
with the current SpecSpec scheme. The dialogue/app evolution below is retained;
node IDs, CLI receipts and Git stage references now come from new current-tool
executions. This is not a claim that untouched original commits used today's
encoding. Inspect the bundle's `stage/01-spec` through `stage/03-code` tags.

**Every User/AI turn below is fictional.** The actual project owner asked for a
Gantt/planning example, at least two major redirects, and proper Git recording.
This narrative is an educational simulation, not a transcript of an external
customer or additional authorization. CLI operations, code, checks, and Git
commits described as completed are real. Stage numbers are narrative references,
not review stages stored on nodes. This older illustrative dialogue is optional:
maintained examples need plausible graph emergence and revision, not invented AI
conversations. The current checkout/maintenance guide is `history/WALKTHROUGH.md`.

## 01 — The initial business-portfolio hypothesis

**User (simulated):** I manage several business projects. I want a Gantt chart with
Monday-Friday durations and prerequisites, team owners, progress summaries, and
portfolio finish dates. Eventually it should avoid double-booking people and let
team members share plans through accounts.

**AI (simulated):** Those are distinct outcomes. I'll record them separately from
my choices: a topological weekday forecast, simple portfolio rollups, and possible
hosted SQL storage/resource leveling. A shared service is not inevitable just
because you want shared planning. To test the view cheaply, may I first build a
local read-only calendar prototype? Authentication and capacity scheduling would
remain explicitly unimplemented.

**User (simulated):** That experiment is worth trying. Show me a couple of projects;
don't spend the first pass on operating a service.

**AI (simulated):** I've initialized SpecSpec before writing application code. The
manifesto is about understandable, revisable planning, not a fixed market or stack.
I read each new node's ancestor context. Inputs must be validated and task names
rendered as text. Implementation records will distinguish delivered behavior from
future candidates; passing tests will not turn choices into permanent decisions.

**AI (simulated, prototype report):** The first runnable local view has two projects,
weekday prerequisite forecasts, named-owner display, and simple completion/finish
rollups. Six actual model tests passed. There are no shared accounts or resource
constraints, and I haven't claimed a real-browser test yet. The SpecSpec implementation
nodes link the source and state those limits.

## 02 — Redirect one: not a business tool after all

**User (simulated):** Stop. Seeing the prototype makes me realize I described the
wrong audience. This is for my own home renovation. Replace the portfolio/team/cloud
plan, not just its labels. I choose the dates myself, including weekends. No
prerequisites or rescheduling. Give me priorities, local autosave, and a JSON file
I can keep. I don't want accounts or a scheduling service.

**AI (simulated):** That reverses the product scope and date model. I checked impact
before changing the graph: the obsolete branch is **13 of the 17 live nodes**,
including its two implementation explanations. I'll retire that complete branch,
not delete the evidence or rewrite the original intention to claim you always
wanted a personal app. The broad manifesto, readable timeline, safe input, and
revisable-choice intentions survive. New intentions describe manual dates, weekends,
priorities, and local ownership. Separate conclusions choose inclusive date ranges,
browser storage, and a version-one JSON schema.

**User (simulated):** Yes, the manual version is the useful next experiment. Storage
can be browser-local, but don't pretend it is a backup or synchronized workspace.

**AI (simulated):** The managed retirement was one guarded batch after reading
impact, with no live dependents left on withdrawn parents. The replacement graph
is committed before rewriting the prototype. At this spec-only commit, the code
still implements stage 01; the next commit will realize stage 02. That temporary
boundary is explicit rather than a fabricated implementation claim.

**AI (simulated, prototype report):** The personal app now lets you add/edit/delete
manual ranges and priorities, including weekends, with browser-local autosave and
JSON import/export. The earlier scheduler/portfolio code has been replaced, but its
Git revision remains runnable. Seven actual Node model tests and syntax checks
passed. Corrupt saved data is left untouched until reset. I exported the real demo
as `history/personal-v1.json` for a later compatibility exercise. Real-browser
interaction and storage failure paths are still unverified at this stage.

## 03 — Redirect two: a workshop what-if planner

**User (simulated):** I showed the personal version at our makerspace. The useful
problem is planning a workshop, not renovating my house. Replace the manual-date/
priority model with workday durations, prerequisites, and optional earliest dates.
We work Monday–Friday. I need to freeze a baseline, change a duration, and see which
finish dates move. Keep local files and autosave. Still no portfolio, owner leveling,
accounts, or cloud. Don't silently reinterpret my old personal-plan JSON.

**AI (simulated):** This replaces **9 of the 16 live nodes**: personal scope, manual
ranges/weekends, priorities, independent tasks, the v1 schema choice, and both
implementation explanations. Portability, local autosave, and the browser-storage
choice survive with the common intentions. I'll withdraw the obsolete branch in
one guarded batch. Weekday dependencies resemble the initial experiment, but this
new workshop forecast is a separately justified conclusion, not restoration or
approval of the old portfolio branch.

**User (simulated):** Use the simple dependency forecast, not an optimizer. Excluding
holidays and resources is fine if the app says so. Baseline capture must be explicit;
a new edit must never quietly overwrite it. Show me an import preview and explain
what is lost when converting the personal file.

**AI (simulated):** I'll choose an iterative whole-day forecast, a deep baseline
snapshot, and a version-two envelope. V1 manual spans become weekday durations of
at least one day; start becomes an earliest bound, priority is lost, and weekend/
finish semantics change. Preview and explicit Apply are required. Imported/stored
data is validated before it replaces work; corrupt storage stays protected.
Native forms and a local DOM chart keep the prototype inspectable without a runtime
API/CDN. The graph has practical chart/task/date bounds, not production guarantees.

**AI (simulated, spec-only checkpoint):** I read contexts/impacts, recorded new
intentions separately from those choices, and committed this second replacement
before rewriting code. This checkpoint still runs the stage-02 app. The next
implementation must add real unit and browser evidence, with remaining risks stated.

**AI (simulated, final implementation report):** The local workshop app is runnable
without a build or runtime API. Tasks, durations, earliest bounds, prerequisites,
explicit baseline capture/replacement/clear, current/baseline bars, and a text date
table work. Imported markup stays literal text. A baseline-only task remains visible
when removed from the current plan. Export includes the baseline; v1 conversion is
previewed with warnings, never silently applied to stored personal data.

Twenty actual model tests passed, including forty seeded DAGs against an independent
reference, weekend/DST/leap boundaries, bounded deep graphs, malformed data, baseline
immutability, safe deletion, and the original v1 export. A real installed Windows
Chromium run passed forecast changes, baseline retention, native caret through a
narrow-screen redraw, rejected cyclic drafts/cancelled navigation, literal text,
actual file upload/download, preview/cancel/conversion, reload, protected corrupt/v1
storage, and session-only operation when storage is denied. It also launched directly
from a local file. Desktop and narrow screenshots were captured and inspected.
Inspection exposed a mobile grid min-width overflow; the fix and browser regression
keep scrolling inside the chart/table. The request assertion was corrected to allow
Chromium's inline data-URL date icons, which do not contact an external service.

This is prototype evidence, not exhaustive manual/accessibility/platform/security/
performance certification. No holidays, resource optimizer, accounts, or cloud were
smuggled back into the app. The graph contains 44 nodes, evenly divided between live
and retained withdrawn explanations. Review remains proportionate to this small,
revisable experiment; there is no invented per-node approval ceremony.

**AI (simulated, Git boundary):** This implementation is committed after its spec.
The following audit records its real hash once it exists and verifies all three
spec/code pairs and both large withdrawals against Git blobs. Recording a future
commit's hash inside itself would be fiction, so the ledger is completed afterward.

## Final audit — the history is real

The maintained final implementation is tagged `stage/03-code`; its actual current
commit ID is recorded in `history/revisions.json`, not the obsolete development
repository hash. Its following audit verifies all three spec/code pairs, the
initially absent graph/code, fresh current CLI receipt contents, large explicit
withdrawals, and retained branch semantics.
The first audit exposed the legitimate empty predecessor snapshot before `init`;
the verifier now treats that boundary explicitly rather than requiring a nonexistent
graph. Parent/nested graph tests also check exact staged blobs independently using a
disposable repository, never corrupting or installing hooks in the real checkout.

The SpecSpec parent graph links this example and its verification. CI is configured
for both graphs, full Git-history audit, model and real-browser checks; remote CI is
not claimed run. The final audit is a separate real commit, not a fabricated part of
the simulated dialogue. No files were pushed or unrelated logos staged.
