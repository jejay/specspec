---
id: 7tMgRa8=
type: requirement
parents:
- 0dvOn3A=
---
# Offer seven everyday commands and three advanced tools

The everyday commands are `init`, `query`, `add`, `update`, `delete`, `check` and `diff`. `query` does all reading of the specification. `check` validates the working files, the staged index and the state of the source links. `diff` shows every change to the specification between two revisions, by default between a freshly resolved HEAD and the working files. A command runs in the directory of the project, like Git.

`init`, `add` and `update` take the text as literal `-m`/`--message` paragraphs, one option for each paragraph. `add` and `update` take each parent as a full ID in a `--parent` option of its own. `add` creates a requirement by default and an implementation with `--type implementation`. The `--parent` options of an `update` replace the parent list of the node. `add`, `update` and `delete` can be combined in one invocation, and every other command stands alone.

The advanced tools come in three groups: `sources` with `show`, `capture` and `reanchor` for source links, `recover` for an interrupted transaction, and `spotlight` with `add`, `show` and `flush` for the messages that owner and agent attach to nodes. Help lists the everyday commands apart from these tools. Everyday help leaves out the inputs of integrations: arrays of sources, reviewed deletion plans and structured requests through a hidden `api` command. Each operation has one spelling. An owner connects `check --staged` to their own Git hooks and CI.
