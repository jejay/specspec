---
id: qrF-BAU=
type: implementation
parents:
- hdJaFcQ=
- EIDAkpU=
- wnqgWvE=
- rLiKdQU=
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
- path: tools/guide_quiz/scorecard.py
- path: tools/guide_quiz/quizzes/bakery.md
- path: tools/guide_quiz/quizzes/bakery.rubric.md
- path: tools/guide_quiz/quizzes/clinic.md
- path: tools/guide_quiz/quizzes/clinic.rubric.md
- path: tools/guide_quiz/quizzes/dilemmas.json
- path: tools/guide_quiz/quizzes/discuss.md
- path: tools/guide_quiz/quizzes/discuss.rubric.md
- path: tools/guide_quiz/quizzes/discuss-game.md
- path: tools/guide_quiz/quizzes/discuss-game.rubric.md
- path: tools/guide_quiz/quizzes/explain-cases.md
- path: tools/guide_quiz/quizzes/explain-rules.md
- path: tools/guide_quiz/quizzes/grader.md
- path: tools/guide_quiz/quizzes/manual-plan.md
- path: tools/guide_quiz/quizzes/manual-plan.rubric.md
- path: tools/guide_quiz/quizzes/owner-edits-apply.md
- path: tools/guide_quiz/quizzes/owner-edits-commands.md
- path: tools/guide_quiz/quizzes/owner-edits-plan.md
- path: tools/guide_quiz/quizzes/owner-edits-plan.rubric.md
- path: tools/guide_quiz/quizzes/owner-edits-review.md
- path: tools/guide_quiz/quizzes/owner-edits-review.rubric.md
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
- path: tools/guide_quiz/quizzes/sealed-feature.md
- path: tools/guide_quiz/quizzes/sealed-plan.md
- path: tools/guide_quiz/quizzes/sealed-plan.rubric.md
- path: tools/guide_quiz/quizzes/toolshed.md
- path: tools/guide_quiz/quizzes/toolshed.rubric.md
- path: tests/test_guide_quiz.py
- path: CONTRIBUTING.md
- path: .gitignore
---
# Guide quiz under tools/guide_quiz

`python -m tools.guide_quiz` asks models, grades their answers and reports. `models.py`
calls the `claude` command of Claude Code once per question, with a guide version as
the system prompt, no tools, an environment free of the calling session's variables
and an empty working folder. `dilemmas.py` reads 71 dilemmas from `quizzes/dilemmas.json`, 11 about intention and conclusion as a relation, 22 about the structure of a graph and 38 about routine, phases, commands and wording, and
shuffles their options the same way for every model and guide. `tasks.py` and the briefs
in `quizzes/` define the open tasks: three briefs to draw a graph from, two requests to revise a graph, one flawed graph to review, two briefs to discuss in tandem planning and two questions whose answers a person reads. The third drawing brief names ways without saying what they are for, leaves open how firmly one sentence holds and has a conclusion in its manifesto's wording. The second discussion plants a statement that works against its manifesto and a sentence of unclear firmness. Nine more tasks use a bike-shop graph with nodes that the owner wrote by hand: a structure review of them, as text and as a dry run that lists its commits; the planning after the owner accepted three suggestions and declined three or left three unanswered, also written as command lines; and the planning of a further request while those nodes are uncommitted, committed by the owner or sealed by an agent planning commit, the last also with a request that needs a sealed node restructured.

`graphs.py` builds the graphs that models return, checks them with
`specspec.graph.build_graph` and scans node text for build order. `commands.py` writes a
task's base graph into a temporary folder, commits it, splits each command line of an
answer into words as a POSIX shell does and runs `add`, `update` and `delete` with
specspec's command line, each invocation in a process of its own. Of the shell it knows quoting, `&&`, `;` and
`NAME=$(specspec ...)`; an editing command inside any other construct counts as one that
fails. `grading.py` gives a grader the rubric, the task and the answer, never the model
or the guide, and turns its findings into criteria; the first two drawing briefs share theirs. A verdict from an earlier wording of a rubric is read under its earlier field names. The planning tasks are scored from the resulting graph. Drawn graphs are also measured for negative wording, and their rubrics count the nodes that record a conclusion of the agent's own. `grade` judges the answers that have no verdict yet, for all guides or the named
ones, and judges a named task anew. `results.py` keeps raw answers in the ignored `results/` folder,
one file per process. `report.py` prints one column per model and guide, for all of them
or for the named ones, with the share of right answers for the dilemmas about structure
and for the others. It compares two graders on the answers both graded and adds up what
the recorded calls cost. `scorecard.py` prints about thirty behaviours in plain words, each with what the model was asked and what is counted, one column per named guide. Its first group holds the behaviours that show whether the agent tells intention from conclusion.

The tool lies outside `src/` and the npm workspaces, so no artifact contains it.
`tests/test_guide_quiz.py` checks that boundary, the ignore rule and the tool's logic,
with scripted replies in place of model calls. CONTRIBUTING.md gives the procedure. The
tool reaches models only through Claude Code. What a grader finds about wording is a model's judgment, and the briefs and the answer key are this repository's own. Answers are kept under the name of their task or dilemma. `tasks.py` gives every answer a mark of its brief's wording, and the tool counts the answers whose mark fits the brief as it reads now; a reworded dilemma takes a new ID.
