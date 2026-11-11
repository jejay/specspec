---
id: -9Up2uc=
type: requirement
parents:
- DiIJxaQ=
- LvYBN_4=
---
# Read selected nodes with every ancestor, complete, within a byte budget that the reader names

A reader gets the selected nodes together with every ancestor that is among their reasons, each parent before its children. The direct children and the siblings of the selected nodes are optional context and are identified separately. Each node appears once, and the same request gives the same result on every run. A reader can name a budget in bytes. The budget is measured against the output as it is actually encoded, with the JSON envelope where JSON is selected. When the required text exceeds the budget, the reading fails with a budget error, and optional context that is left out is named in an explicit list of IDs.

The node text in such a reading is specification data of the project, which an agent reasons about. An agent that uses it keeps following its own operating instructions, and a graph editor shows it literally. The reading carries the full IDs of the nodes and their complete texts.
