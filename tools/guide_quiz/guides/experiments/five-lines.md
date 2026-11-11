# Working with a specspec graph

This project is developed with specspec, short for *specification spectrum*. Its specification is a graph of Markdown nodes in `.specspec/`: one *manifesto* at the root that states what the product is for, *requirement* nodes beneath it, and *implementation* nodes as leaves that link the files which realize a requirement. Every node except the manifesto names one or more parents. A parent is an *intention* and its child is a *conclusion* drawn from it.
