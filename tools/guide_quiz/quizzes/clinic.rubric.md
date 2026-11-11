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
  "own_node": "true if the provider choice is the main subject of a node of its own; false if it is only a sentence in a broader node",
  "left_open_explicitly": "true if a node says that the provider is deliberately left open"
 },
 "reminder": {
  "outcome_node": "key of a node that states the purpose of reminding (patients are reminded in time / fewer forgotten appointments), or null",
  "means_node": "key of the node that says the reminder is a text message, or null",
  "separate_nodes": "true if outcome_node and means_node are two different nodes and means_node has outcome_node among its ancestors",
  "outcome_text_free_of_means": "true if neither the title nor the body of outcome_node says that the reminder is a text message or SMS"
 },
 "week": {
  "outcome_node": "key of a node that states that everyone sees the week at a glance, or null",
  "means_node": "key of the node that settles the week grid with therapists as columns, or null",
  "separate_nodes": "true if these are two different nodes and means_node has outcome_node among its ancestors",
  "outcome_text_free_of_means": "true if neither title nor body of outcome_node describes the grid or the columns"
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
 "category_nodes": ["keys of requirement nodes that are only a topic or category heading for their children and state no outcome, constraint or choice of their own"],
 "historic_contrast": [{"key": "node key", "quote": "the words that refer to the old way of working (paper calendar, phone tag) or to a change over time (now, no longer, instead of, replaces)"}],
 "root_children_means": ["keys of nodes directly under ROOT that record a means or technical choice (such as a provider, a framework, a file format or the week grid) rather than an outcome the owner wants or a constraint the owner imposed"],
 "reminder_wording": "one of: decided (a node gives what the reminder says), left_open_stated (a node says the wording is left open), absent",
 "label_titles": ["keys of requirement nodes whose title is a bare topic label without a verb, such as 'Reminders' or 'Data storage'"],
 "implementation_nodes_that_are_choices": ["keys of nodes of type implementation whose text records a decision about the product or its technology rather than explaining files that exist"],
 "blended_nodes": [{"key": "node key", "why": "names the two or more decisions in this node that serve different purposes and could clearly be replaced independently"}],
 "report": {
  "names_own_choices": "true if the report tells the owner which choices the agent made on its own",
  "names_open_points": "true if the report names open questions or uncertainty",
  "names_added_outcomes": "true if the report says which outcomes or constraints the agent added that the owner had not asked for, or true if it added none"
 }
}

Booleans are real JSON booleans. Lists may be empty.
