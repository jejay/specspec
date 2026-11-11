---
id: qowy5AI=
type: requirement
parents:
- F5JaC_4=
- DiIJxaQ=
---
# Encode IDs from five random bytes and define the fields of a node file

An ID is `secrets.token_bytes(5)` in the padded Base64url encoding of RFC 4648: seven symbols and `=`, which carry 40 random bits, with the unused bits of the last symbol set to zero. The path of a node is `.specspec/<id>.md`. A reference names the full ID and is case-sensitive. A new ID is generated inside the writer lock. It is generated again when it equals, exactly or apart from the case of ASCII letters, the ID of a current node, the name of a file in the inventory or an ID that a parsed node names as a parent. An ID that is named as a parent stays taken while its node is missing, so a new node with unrelated reasoning never lands by chance in the place of a missing parent. Validation reports IDs that differ only in the case of their letters, because a file system that ignores case cannot hold both files. A random ID is a reference within one project, and graph validation finds the collisions that a merge of branches brings.

A node file has these frontmatter fields:

- `id`, `type` and `parents` are required, and `parents` names each parent once.
- `format_version` is an integer for the tools' own use and stands on the manifesto alone.
- `sources` is optional on an implementation.
- `extensions` is optional and holds JSON-compatible values under namespaced keys.

The types are manifesto, requirement and implementation. The parents of a requirement are the manifesto or requirements, and the parents of an implementation are requirements. The tools read the one manifesto and its format version before they parse the other files in full. Each of these gets an explicit diagnostic: an unsupported version, an unknown field, a duplicate YAML key, a YAML tag or alias, a value that would have to be converted to the type of its field, a file name that differs from `<id>.md`, invalid UTF-8 and a file larger than 1 MiB. The regular files directly in `.specspec` are the node files.

A write that targets some fields keeps the frontmatter comments on the other fields and the logical content of the body. It keeps the newline style of an existing document, and a new document uses LF. The fields that the tools control are written in normal form. Command-line arguments and the graph editors take every ID in full, including an ID that begins with a hyphen. VS Code associates `**/.specspec/???????=.md` with its node editor and has the backend verify the actual file.
