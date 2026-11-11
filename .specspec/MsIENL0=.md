---
id: MsIENL0=
type: requirement
parents:
- MPOzb8A=
- ZIpsXgo=
---
# Commit the owner's hand edits first, exactly as they wrote them

When the agent finds uncommitted specification edits of the owner, it commits them before it questions or changes anything, under the title `Owner specspec changes: <the agent's understanding of them>`. Finding the edits is reason enough for this commit. It holds exactly what the owner wrote, so their words stay on record even where the agent misunderstands them. The agent runs the staged check on exactly these edits and takes what the check reports into its review.

The commit seals nothing: the edits stay open for the structure review that follows.
