The agent was given the owner's brief below and asked to draw the graph for a product
that is not built yet. "ROOT" is the manifesto. For every node you get its key, type, parents,
the list of all its ancestors, its title and its body.

Fill in this JSON object. Use null where no such node exists.

{
 "pg": {
  "node": "key of the node that records the PostgreSQL mandate, or null",
  "own_node": "true if the PostgreSQL mandate has a node of its own (it is the main subject of that node)",
  "has_descendants": "true if at least one other node has that node among its ancestors"
 },
 "eu": {
  "node": "key of the node that records that patient data stays in the EU, or null",
  "own_node": "true if it has a node of its own"
 },
 "sms_provider": {
  "node": "key of the node that records which provider or gateway sends the text messages (Twilio or another), or null if no node names or settles a provider",
  "own_node": "true if the provider is the main subject of a node of its own; false if it is only a sentence in a broader node",
  "left_open_explicitly": "true if a node says that the provider is deliberately left open"
 },
 "reminder": {
  "intention_node": "key of a node that states the purpose of reminding (patients are reminded in time / fewer forgotten appointments), or null",
  "way_node": "key of the node that says the reminder is a text message, or null",
  "separate_nodes": "true if intention_node and way_node are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither the title nor the body of intention_node says that the reminder is a text message or SMS"
 },
 "week": {
  "intention_node": "key of a node that states that everyone sees the week at a glance, or null",
  "way_node": "key of the node that settles the week grid with therapists as columns, or null",
  "separate_nodes": "true if these are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither title nor body of intention_node describes the grid or the columns"
 },
 "double_booking_own_node": "true if the rule that a therapist or a room has one appointment at a time is the main subject of a node of its own",
 "limits": {
  "nodes": ["keys of the nodes that state the allowed durations (20/30/45/60 minutes), the hours (7:00 to 20:00) or the days (Monday to Saturday) as a rule"],
  "all_three_stated": "true if durations, hours and days are all stated somewhere in the graph"
 },
 "paper_phone": {
  "nodes": ["keys of the nodes about the week on paper and about the phone calendar"],
  "separate_nodes": "true if the paper/print solution and the phone-calendar solution each have a node of their own"
 },
 "work_order": {
  "order_nodes": ["keys of nodes whose subject is an order of work, a step, a phase, a priority or a setup task, e.g. a node that exists to say 'set up CI first'"],
  "order_in_text": ["keys of other nodes whose text states when something gets built or what comes first or last"]
 },
 "category_nodes": ["keys of requirement nodes that are only a topic or category heading for their children and state nothing of their own about the product"],
 "historic_contrast": [{"key": "node key", "quote": "the words that refer to the old way of working (paper calendar, phone tag) or to a change over time (now, no longer, instead of, replaces)"}],
 "root_children_ways": ["keys of nodes directly under ROOT whose main subject is a way that could be another (such as a provider, a framework, a file format or the week grid) rather than something the owner intends or holds as fixed"],
 "reminder_wording": "one of: decided (a node gives what the reminder says), left_open_stated (a node says the wording is left open), absent",
 "label_titles": ["keys of requirement nodes whose title is a bare topic label without a verb, such as 'Reminders' or 'Data storage'"],
 "implementation_nodes_that_conclude": ["keys of nodes of type implementation whose text records a conclusion about the product or its technology rather than explaining files that exist"],
 "blended_nodes": [{"key": "node key", "why": "names the two or more statements in this node that serve different intentions and could clearly be replaced independently"}],
 "own_conclusion_nodes": ["keys of nodes whose main subject is a conclusion that the owner's brief neither states nor suggests, so that the agent drew it on its own, such as what a cancelled appointment leaves behind or who may move an appointment; leave out nodes that record what the owner said, the intention behind it or a way the owner suggested"],
 "report": {
  "names_own_conclusions": "true if the report tells the owner which conclusions the agent drew on its own",
  "names_open_points": "true if the report names open questions or uncertainty",
  "names_read_intentions": "true if the report tells the owner which intentions the agent worded itself or read into the owner's words, such as the purpose it placed above something the owner named, so that the owner can correct them; false if the report presents everything as what the owner asked for"
 }
}

Booleans are real JSON booleans. Lists may be empty.
