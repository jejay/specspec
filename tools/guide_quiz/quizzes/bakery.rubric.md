The agent was given the owner's brief below and asked to draw the graph for a product
that is not built yet. "ROOT" is the manifesto. For every node you get its key, type, parents,
the list of all its ancestors, its title and its body.

Fill in this JSON object. Use null where no such node exists.

{
 "pc": {
  "node": "key of the node that records that the app has to run on the mini PC under the counter (no other hardware, no paid hosting), or null",
  "own_node": "true if that mandate has a node of its own (it is the main subject of that node)",
  "has_descendants": "true if at least one other node has that node among its ancestors"
 },
 "lang": {
  "node": "key of the node that records that everything a customer sees is in German and in Turkish, or null",
  "own_node": "true if it has a node of its own"
 },
 "email_wording_node": "key of the node that settles what the e-mail says (its wording or content), or null",
 "mail_sender": {
  "node": "key of the node that records how or through which mailbox or service the e-mails are sent, or null if no node settles that",
  "own_node": "true if that choice is the main subject of a node of its own; false if it is only a sentence in a broader node",
  "left_open_explicitly": "true if a node says that this is deliberately left open"
 },
 "ready": {
  "outcome_node": "key of a node that states the purpose of the notice (customers know when their order is ready / nobody waits in the shop for nothing), or null",
  "means_node": "key of the node that says the customer is told by e-mail, or null",
  "separate_nodes": "true if outcome_node and means_node are two different nodes and means_node has outcome_node among its ancestors",
  "outcome_text_free_of_means": "true if neither the title nor the body of outcome_node says that the notice is an e-mail"
 },
 "board": {
  "outcome_node": "key of a node that states the purpose (the bakers know what to bake, or what to bake first), or null",
  "means_node": "key of the node that settles the board on the screen in the bakehouse, or null",
  "separate_nodes": "true if these are two different nodes and means_node has outcome_node among its ancestors",
  "outcome_text_free_of_means": "true if neither title nor body of outcome_node describes a board or a screen"
 },
 "handout_once_own_node": "true if the rule that an order is handed out only once is the main subject of a node of its own",
 "limits": {
  "nodes": ["keys of the nodes that state the 20-item limit, the 18:00 order deadline or the 6:30 to 12:30 pickup window as a rule"],
  "all_three_stated": "true if the item limit, the deadline and the pickup window are all stated somewhere in the graph"
 },
 "slip_phone": {
  "nodes": ["keys of the nodes about the printed slip and about what the customer shows on the phone"],
  "separate_nodes": "true if the printed slip and the thing on the phone each have a node of their own"
 },
 "work_order": {
  "order_nodes": ["keys of nodes whose subject is an order of work, a step, a phase, a priority or a setup task"],
  "order_in_text": ["keys of other nodes whose text states when something gets built or what comes first, later or last"]
 },
 "category_nodes": ["keys of requirement nodes that are only a topic or category heading for their children and state no outcome, constraint or choice of their own"],
 "historic_contrast": [{"key": "node key", "quote": "the words that refer to the old way of working (phone calls, paper notes, lost orders) or to a change over time (now, no longer, instead of, replaces)"}],
 "root_children_means": ["keys of nodes directly under ROOT that record a means or technical choice (such as a mail service, a database, a framework, a file format or the board on a screen) rather than an outcome the owner wants or a constraint the owner imposed"],
 "email_wording": "one of: decided (a node gives what the e-mail says), left_open_stated (a node says the wording is left open), absent",
 "label_titles": ["keys of requirement nodes whose title is a bare topic label without a verb, such as 'Notifications' or 'Data storage'"],
 "implementation_nodes_that_are_choices": ["keys of nodes of type implementation whose text records a decision about the product or its technology rather than explaining files that exist"],
 "blended_nodes": [{"key": "node key", "why": "names the two or more decisions in this node that serve different purposes and could clearly be replaced independently"}],
 "report": {
  "names_own_choices": "true if the report tells the owner which choices the agent made on its own",
  "names_open_points": "true if the report names open questions or uncertainty",
  "names_added_outcomes": "true if the report says which outcomes or constraints the agent added that the owner had not asked for, or true if it added none"
 }
}

Booleans are real JSON booleans. Lists may be empty.
