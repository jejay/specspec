---
id: 7tMgRa8=
type: requirement
parents:
- 0dvOn3A=
---
# Expose everyday commands and focused advanced tools

The everyday vocabulary is init, query, add, update, delete, check and diff. Query
owns all specification inspection, check validates working, staged and source
state, and diff shows complete specification changes between revisions, defaulting
to freshly resolved HEAD versus the working files. Commands run in the current
project directory, like Git.

Init, add and update take literal repeatable -m/--message paragraphs and repeated
full --parent IDs. Add creates requirements by default and implementations with
--type implementation. An update's --parent list replaces the node's parents. Add,
update and delete can combine into one invocation; other commands stand alone.

Advanced groups cover source links (sources show/capture/reanchor), transaction
recovery (recover) and owner/agent spotlights (spotlight add/show/flush). Help
separates the everyday vocabulary from these tools. Integration inputs such as
source arrays, reviewed deletion plans and structured requests through a hidden api
command stay out of everyday help. Each operation has one spelling. Owners connect
check --staged to their own Git hooks and CI.
