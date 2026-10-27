---
id: JYMQE1c=
type: requirement
parents:
- Es6S-yg=
- Yfy0414=
---
# Publish reviewed Python artifacts through a manual GitHub identity

Use the owner's PyPI Trusted Publisher for repository jejay/specspec, workflow
.github/workflows/pipy_publish.yaml and environment pypi. An explicit manual run
on main names the expected release version. Fail if Python/runtime/workspace/lock
metadata disagree. Build and test Python wheel/source distributions in a job without
OIDC permission; validate exact contents/resources/metadata and smoke installed
artifacts before handing those two distributions to a separate publishing job.

Only the publishing job requests GitHub's short-lived OIDC identity. It downloads
the verified artifact without checking out or executing project source, and uses a
pinned PyPA publishing action with attestations and strict duplicate rejection.
PyPI matches issuer, audience, expiry and repository/workflow/environment claims;
the first authorized upload converts the pending publisher into a project publisher.
No long-lived PyPI token is stored. Ordinary pushes, PRs, CLI/UI actions and local
packaging do not publish. Preserve existing GitHub environment protections; constrain
publication to main. Report success only after checking the public index and an
isolated installation from it. Record failed/partial uploads without claiming an
all-or-nothing registry transaction or overwriting an immutable release.
