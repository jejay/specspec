---
id: qrF-BAU=
type: implementation
parents:
- hdJaFcQ=
- EIDAkpU=
sources:
- path: tools/guide_quiz/__init__.py
- path: tools/guide_quiz/__main__.py
- path: tools/guide_quiz/commands.py
- path: tools/guide_quiz/models.py
- path: tools/guide_quiz/dilemmas.py
- path: tools/guide_quiz/tasks.py
- path: tools/guide_quiz/graphs.py
- path: tools/guide_quiz/grading.py
- path: tools/guide_quiz/results.py
- path: tools/guide_quiz/report.py
- path: tools/guide_quiz/quizzes/bakery.md
- path: tools/guide_quiz/quizzes/bakery.rubric.md
- path: tools/guide_quiz/quizzes/clinic.md
- path: tools/guide_quiz/quizzes/clinic.rubric.md
- path: tools/guide_quiz/quizzes/dilemmas.json
- path: tools/guide_quiz/quizzes/discuss.md
- path: tools/guide_quiz/quizzes/explain-cases.md
- path: tools/guide_quiz/quizzes/explain-rules.md
- path: tools/guide_quiz/quizzes/grader.md
- path: tools/guide_quiz/quizzes/owner-edits-apply.md
- path: tools/guide_quiz/quizzes/owner-edits-commands.md
- path: tools/guide_quiz/quizzes/owner-edits-plan.md
- path: tools/guide_quiz/quizzes/owner-edits-plan.rubric.md
- path: tools/guide_quiz/quizzes/owner-edits-unanswered.md
- path: tools/guide_quiz/quizzes/owner-edits.graph.json
- path: tools/guide_quiz/quizzes/owner-edits.md
- path: tools/guide_quiz/quizzes/owner-edits.rubric.md
- path: tools/guide_quiz/quizzes/review.md
- path: tools/guide_quiz/quizzes/review.rubric.md
- path: tools/guide_quiz/quizzes/revise-phones.md
- path: tools/guide_quiz/quizzes/revise.graph.json
- path: tools/guide_quiz/quizzes/revise.md
- path: tools/guide_quiz/quizzes/revise.rubric.md
- path: tests/test_guide_quiz.py
- path: CONTRIBUTING.md
- path: .gitignore
---
# Guide quiz under tools/guide_quiz

`python -m tools.guide_quiz` asks models, grades their answers and reports. `models.py`
calls the `claude` command of Claude Code once per question, with a guide version as
the system prompt, no tools, an environment free of the calling session's variables
and an empty working folder. `dilemmas.py` reads 52 dilemmas from `quizzes/dilemmas.json`,
22 about the structure of a graph and 30 about routine, phases, commands and wording, and
shuffles their options the same way for every model and guide. `tasks.py` and the briefs
in `quizzes/` define the open tasks: two briefs to draw a graph from, two requests to
revise a graph, one flawed graph to review and three questions whose answers a person
reads. Five more tasks start from nodes that the owner edited by hand: a structure review
of them, the planning after the owner accepted three suggestions and declined three or
left three unanswered, that planning written as command lines, and the planning of a
further request while the edits are unreviewed.

`graphs.py` builds the graphs that models return, checks them with
`specspec.graph.build_graph` and scans node text for build order. `commands.py` writes a
task's base graph into a temporary folder, commits it, splits each command line of an
answer into words as a POSIX shell does and passes `add`, `update` and `delete` to
`specspec.cli` in the same process. Of the shell it knows quoting, `&&`, `;` and
`NAME=$(specspec ...)`; an editing command inside any other construct counts as one that
fails. `grading.py` gives a grader the rubric, the task and the answer, never the model
or the guide, and turns its findings into criteria that both drawing briefs share. The
planning tasks are scored from the resulting graph, and drawn graphs are also measured
for negative wording. `results.py` keeps raw answers in the ignored `results/` folder,
one file per process. `report.py` prints one column per model and guide, for all of them
or for the named ones, with the share of right answers for the dilemmas about structure
and for the others. It compares two graders on the answers both graded and adds up what
the recorded calls cost.

The tool lies outside `src/` and the npm workspaces, so no artifact contains it.
`tests/test_guide_quiz.py` checks that boundary, the ignore rule and the tool's logic,
with scripted replies in place of model calls. CONTRIBUTING.md gives the procedure. The
tool reaches models only through Claude Code. What a grader finds about wording stays a
model's judgment, and the briefs and the answer key are this repository's own. Answers
are kept under the name of their task or dilemma, so one whose wording changes takes a
new name.
