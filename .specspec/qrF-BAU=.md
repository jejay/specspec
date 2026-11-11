---
id: qrF-BAU=
type: implementation
parents:
- hdJaFcQ=
sources:
- path: tools/guide_quiz/__init__.py
- path: tools/guide_quiz/__main__.py
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
and an empty working folder. `dilemmas.py` reads 22 dilemmas from
`quizzes/dilemmas.json` and shuffles their options the same way for every model and
guide. `tasks.py` and the briefs in `quizzes/` define the open tasks: two briefs to draw
a graph from, two requests to revise a graph, one flawed graph to review and three
questions whose answers a person reads.

`graphs.py` builds the graphs that models return, checks them with
`specspec.graph.build_graph` and scans node text for build order. `grading.py` gives a
grader the rubric, the task and the answer, never the model or the guide, and turns its
findings into criteria that both drawing briefs share. `results.py` keeps raw answers in
the ignored `results/` folder, one file per process, and `report.py` prints one column
per model and guide.

The tool lies outside `src/` and the npm workspaces, so no artifact contains it.
`tests/test_guide_quiz.py` checks that boundary, the ignore rule and the tool's logic,
with scripted replies in place of model calls. CONTRIBUTING.md gives the procedure. The
tool reaches models only through Claude Code. What a grader finds about wording stays a
model's judgment, and the briefs and the answer key are this repository's own.
