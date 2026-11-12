---
id: 49Qjg3U=
type: requirement
parents:
- BCA1lyI=
---
# Replace an earlier shipped guide in AGENTS.md by exact match

specspec guide brings AGENTS.md to the guide of the installed release. It looks for the exact text of the guide this release ships and of every guide an earlier release shipped, with LF or CRLF line endings, and replaces an earlier guide with the current one in the same line endings. Every other byte of the file stays as it is. With the current guide in place it reports that the guide is current. Without an AGENTS.md, or with one that holds no specspec guide heading, it adds the guide as init does.

When the file holds a guide heading but none of the shipped texts, because the guide was edited by hand, the command changes nothing. Its message says so and names the way forward: specspec guide --print writes the current guide, and the owner or agent puts it in place of the edited one.

The Python package carries the text of the guide that each earlier release shipped. Before a release is published, a check confirms that the guide of the newest release on PyPI is either the current guide or one of these texts. The README tells owners to run specspec guide after an upgrade.
