The agent was given the owner's brief below and asked to draw the graph for a product
that is not built yet. "ROOT" is the manifesto. For every node you get its key, type, parents,
the list of all its ancestors, its title and its body.

Four of the owner's sentences name a way of doing something. Two of them say nothing about
what the way is for (scanning the code, the sheet on the shed door), one has its purpose in
the manifesto, which says that tools come back on time (the e-mail before a tool is due), and one gives its purpose itself (the notice
about a broken tool). For each, find the node that states what the way is for, the intention,
and the node that records the way.

Fill in this JSON object. Use null where no such node exists.

{
 "scan": {
  "intention_node": "key of a node that states what the scanning is for, such as that the association or the app knows which household has which tool, or that every loan and return is on record; null if the graph states this only together with the scanning",
  "way_node": "key of the node that says a member scans the QR code on a tool to borrow and to return, or null",
  "separate_nodes": "true if intention_node and way_node are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither the title nor the body of intention_node mentions scanning, a code or a phone"
 },
 "sheet": {
  "intention_node": "key of a node that states what the door sheet is for, such as that people at the shed, or members, see which tools are out and when they are due back; null if the graph states this only together with the sheet",
  "way_node": "key of the node that records the printed sheet on the shed door, or null",
  "separate_nodes": "true if these are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither title nor body of intention_node mentions a sheet, paper or printing"
 },
 "due": {
  "intention_node": "key of a node that states what the e-mail is for, such as that tools come back on time or that members know when a tool is due; null if the graph states this only together with the e-mail",
  "way_node": "key of the node that says the member gets an e-mail two days before a tool is due, or null",
  "separate_nodes": "true if these are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither title nor body of intention_node mentions an e-mail"
 },
 "broken": {
  "intention_node": "key of a node that states what the damage report is for, such as that a broken tool is taken out of lending or is not lent out; null if the graph states this only together with the report or the notice",
  "way_node": "key of the node that says the member writes what happened and the keeper gets a notice, or null",
  "separate_nodes": "true if these are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither title nor body of intention_node mentions that the member writes something or that a notice is sent"
 },
 "server": {
  "node": "key of the node that records that everything runs on the small server in the association's office (nothing else is paid for), or null",
  "own_node": "true if that is the main subject of a node of its own"
 },
 "vue": {
  "node": "key of the node that records Vue, or null if no node names it",
  "reading": "one of: asked_or_flagged (the report says how the agent read 'I would build it with Vue', for example as a preference that can change, or asks whether it is fixed), silent (the report says nothing about how firmly Vue holds), not_mentioned (neither a node nor the report names Vue)"
 },
 "limits": {
  "nodes": ["keys of the nodes that state the limit of 3 tools per household, the 14 days per loan or the 30 days of reserving ahead as a rule"],
  "all_three_stated": "true if all three limits are stated somewhere in the graph"
 },
 "safety_own_node": "true if the rule that the chainsaw and the wood chipper go only to members who did the safety briefing is the main subject of a node of its own",
 "work_order": {
  "order_nodes": ["keys of nodes whose subject is an order of work, a step, a phase or a priority"],
  "order_in_text": ["keys of other nodes whose text states when something gets built or what comes first or later"]
 },
 "historic_contrast": [{"key": "node key", "quote": "the words that refer to how lending works today or to a change over time (now, no longer, instead of, replaces)"}],
 "own_conclusion_nodes": ["keys of nodes whose main subject is a conclusion that the owner's brief neither states nor suggests, so that the agent drew it on its own, such as what happens when a tool is overdue or how a member signs in; leave out nodes that record what the owner said, the intention behind it or a way the owner suggested"],
 "report": {
  "names_read_intentions": "true if the report tells the owner which intentions the agent worded itself or read into the owner's words, such as what the scanning or the door sheet is for, so that the owner can correct them; false if the report presents everything as what the owner asked for",
  "points_out_manifesto_conclusion": "true if the report tells the owner that the manifesto's wording contains a way that could be another (the calendar view or 'web app'), and suggests a node beneath the manifesto for it or asks whether it is fixed",
  "names_own_conclusions": "true if the report tells the owner which conclusions the agent drew on its own",
  "names_open_points": "true if the report names open questions or uncertainty"
 }
}

Booleans are real JSON booleans. Lists may be empty.
