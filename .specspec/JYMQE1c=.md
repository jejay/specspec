---
id: JYMQE1c=
type: requirement
parents:
- Es6S-yg=
---
# Publish the verified Python distributions to PyPI from a manually started workflow with a short-lived GitHub identity

A release of the command line reaches PyPI through one GitHub workflow that is started by hand. The owner authorizes each publication with an explicit request of its own, and a request to build, to test or to commit includes none. PyPI holds the owner's Trusted Publisher for the repository `jejay/specspec`, the workflow `.github/workflows/pipy_publish.yaml` and the environment `pypi`. A manual run on `main` names the release version that it expects, and it fails when the versions in the Python metadata, the Python runtime, the npm workspaces and the lockfile disagree.

A build job without OIDC permission builds the wheel and the source distribution and runs the tests. It validates the exact contents, the packaged resources and the metadata of both files and tries out installations of them, and only then hands the two distributions to a separate publishing job.

The publishing job alone requests the short-lived OIDC identity of GitHub. It downloads the verified files, checks out no project source and executes none, and uploads with a pinned publishing action of PyPA, with attestations and with strict rejection of duplicates. PyPI matches the issuer, the audience, the expiry and the claims for repository, workflow and environment. This identity is the only credential of a publication, and the repository stores no long-lived PyPI token. The manual run is the only path to PyPI: an ordinary push, a pull request, an action of the command line or of a graph editor and local packaging publish nothing. The publishing job runs in the GitHub environment `pypi` and leaves the protections that the owner configured for that environment in force, and both jobs run on `main` alone.

A release is reported as published once its files are confirmed on the public index and a fresh isolated installation from the index works. PyPI takes the files one by one, so an upload can fail after a part of them has arrived. Such a run is recorded as failed or partial, and a file that PyPI holds is never overwritten, because a release on PyPI is immutable.
