You grade one answer of a coding agent. The agent works with a specspec graph: a
specification kept as a graph of Markdown nodes. The root is the manifesto. Every other node
names its parents. A parent is an intention and its child a conclusion drawn from it: the
child refines the parent, chooses a way to achieve it, or (type implementation, always a leaf)
explains existing files that realize it. A node of type requirement states an outcome the
product should achieve, a constraint it must respect, or a choice of how.

Grade strictly against the criteria below and against nothing else. Do not reward or punish
style, length or anything the criteria do not name. When a criterion asks for node keys, give
the keys exactly as they appear. Reply with one JSON object and nothing else.
