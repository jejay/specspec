---
id: sxxzsrk=
type: requirement
parents:
- L0KGXB8=
---
# Serve the requests of a project from two reused Python processes with limits

For each active project and each trusted configuration of the executable, a graph editor reuses two Python processes of the application, started without a shell: one channel for ordinary requests of the application protocol and one independent, read-only channel for source previews. Both are started at the first authorized request. The hidden transport `api --stream` reads requests of the application protocol as newline-delimited lines of limited size and writes one ordinary envelope of the protocol for each request. A single run of the command line works on its own beside the channels.

The frames of one channel are handled one after another. The number of queued requests, the size of input and output and the time of a request are limited, and a change of the configuration or of the project gets channels of its own. Every request is validated by the backend against the current state and reads files, refs and index anew, under the rules for caches. The requests of a channel share the lifetime of its interpreter and nothing else: an edit plan for an editor document and a write to the node files have the same owners as in a single run.

The channels are disposed when the last view of a project closes and when the project is switched. A channel that fails rejects the work that is pending, and a new channel is created only for a later, deliberate request. A write that was dispatched when its channel failed is reported with an uncertain result that has to be inspected, apart from the requests that were queued and never started. A write is executed once, and sending it again takes a new, deliberate request. A reply is matched as a complete UTF-8 frame. Output that is malformed, unsolicited or too large is diagnosed, and the collected standard error is limited.
