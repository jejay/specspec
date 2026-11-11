"""Quiz models on the agent guide.

A model gets one version of the guide as its only instruction and solves quizzes: dilemmas
with one keyed answer and open tasks such as drawing a graph from an owner's brief. The
answers show whether a wording leads a lightweight model to a well-structured graph.

Run it from the repository root with ``python -m tools.guide_quiz``. It reaches models
through the Claude Code command line and costs money, so no test and no CI job calls it.
The tool is a development aid and belongs to no shipped artifact.
"""
