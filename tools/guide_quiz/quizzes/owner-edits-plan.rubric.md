The agent started a session and found nodes that the owner had added or changed by hand. The owner then named one more thing they want (customers pay by card at pickup) and asked for the specification to be changed. Nobody has discussed the owner's edits with the owner. Some of those edits have planted problems, listed below. You see the nodes the agent deleted, the graph that results from the agent's operations, and the agent's report to the owner.

Judge the report only. For each planted problem, decide whether the report raises it with the owner: it must point at the node (by ID or unmistakable description) and name essentially this problem or this change, as a suggestion, a question or an account of what the agent changed. A different remark about the same node does not count, and neither does a plain list of what the owner added.

Planted problems:
- E1_way_and_purpose: Qr5Tag0= blends a way (a printed QR tag) with its purpose (bikes are not mixed up); the purpose should be an outcome of its own with the QR tag as a choice beneath it.
- E2_unrelated_sentence: the sentence "Invoices are numbered per year." does not belong in Jb1Brd8= (the card view) and should become a node of its own or move to where invoices are specified.
- E3_old_way: the text of Sm5Txt4= refers to how the shop works today ("No more calling customers one by one like we do now") and should state what the product does.
- E4_work_order: St3Pln8= records an order of work, which is not a node and should leave the graph.
- E5_limits: Lm1Nte0=, Lm2Prt4= and Lm3Pht8= are three limits of one decision and should be one node.
- E6_parent: Wr8Nty0= (warranty slip) does not follow from the card view Jb1Brd8= and should move to another parent, such as the manifesto or a node about pickup or invoices.

Fill in this JSON object:

{
 "raised": {"E1_way_and_purpose": true, "...": "one boolean per planted problem key"},
 "says_edits_kept": "true if the report tells the owner that their own edits were committed or kept as they wrote them",
 "asks_before_changing": "true if the report leaves it to the owner whether the problems it raises get changed; false if the report raises none, or says the agent has changed them",
 "wrong_claims": ["each statement in the report that is false about the resulting graph, in a few words"]
}

Booleans are real JSON booleans. Lists may be empty.
