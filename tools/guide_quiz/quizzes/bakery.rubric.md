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
  "own_node": "true if that is the main subject of a node of its own; false if it is only a sentence in a broader node",
  "left_open_explicitly": "true if a node says that this is deliberately left open"
 },
 "ready": {
  "intention_node": "key of a node that states the purpose of the notice (customers know when their order is ready / nobody waits in the shop for nothing), or null",
  "way_node": "key of the node that says the customer is told by e-mail, or null",
  "separate_nodes": "true if intention_node and way_node are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither the title nor the body of intention_node says that the notice is an e-mail"
 },
 "board": {
  "intention_node": "key of a node that states the purpose (the bakers know what to bake, or what to bake first), or null",
  "way_node": "key of the node that settles the board on the screen in the bakehouse, or null",
  "separate_nodes": "true if these are two different nodes and way_node has intention_node among its ancestors",
  "intention_text_free_of_way": "true if neither title nor body of intention_node describes a board or a screen"
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
 "category_nodes": ["keys of requirement nodes that are only a topic or category heading for their children and state nothing of their own about the product"],
 "historic_contrast": [{"key": "node key", "quote": "the words that refer to the old way of working (phone calls, paper notes, lost orders) or to a change over time (now, no longer, instead of, replaces)"}],
 "root_children_ways": ["keys of nodes directly under ROOT whose main subject is a way that could be another (such as a mail service, a database, a framework, a file format or the board on a screen) rather than something the owner intends or holds as fixed"],
 "email_wording": "one of: decided (a node gives what the e-mail says), left_open_stated (a node says the wording is left open), absent",
 "label_titles": ["keys of requirement nodes whose title is a bare topic label without a verb, such as 'Notifications' or 'Data storage'"],
 "implementation_nodes_that_conclude": ["keys of nodes of type implementation whose text records a conclusion about the product or its technology rather than explaining files that exist"],
 "blended_nodes": [{"key": "node key", "why": "names the two or more statements in this node that serve different intentions and could clearly be replaced independently"}],
 "own_conclusion_nodes": ["keys of nodes whose main subject is a conclusion that the owner's brief neither states nor suggests, so that the agent drew it on its own, such as how the assistant finds an order at the counter or what a customer sees after the deadline; leave out nodes that record what the owner said, the intention behind it or a way the owner suggested"],
 "report": {
  "names_own_conclusions": "true if the report tells the owner which conclusions the agent drew on its own",
  "names_open_points": "true if the report names open questions or uncertainty",
  "names_read_intentions": "true if the report tells the owner which intentions the agent worded itself or read into the owner's words, such as the purpose it placed above something the owner named, so that the owner can correct them; false if the report presents everything as what the owner asked for"
 }
}

Booleans are real JSON booleans. Lists may be empty.
