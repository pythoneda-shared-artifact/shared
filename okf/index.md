---
okf_version: "0.2"
---

# pythoneda-shared-artifact/shared

* [shared](pythoneda-shared-artifact-shared.md) - Shared Kernel: Shared kernel for Artifacts.

## Nix Flake
* [AbstractArtifact](abstract-artifact.md) - Represents Artifacts.

## Port
* [ArtifactRepository](artifact-repository.md) - Repository of artifacts.

## Shared Kernel
* [PythonPackage](python-package.md) - Represents a Python package.

## Value Object
* [ArchitecturalRole](architectural-role.md) - An enumerated type to identify the different roles each repository plays architecture-wise.
* [ArtifactEventListener](artifact-event-listener.md) - Provides common Artifact-related operations.
* [Commit](commit.md) - Reacts to ChangeStaged events.
* [CommitPush](commit-push.md) - Reacts to StagedChangesCommitted events.
* [CommitTag](commit-tag.md) - Reacts to CommittedChangesTagged events.
* [HexagonalLayer](hexagonal-layer.md) - An enumerated type to identify layers in hexagonal architectures.
* [PescioSpace](pescio-space.md) - An enumerated type to identify Carlo Pescio's spaces (https://www.youtube.com/watch?v=WPgYju3KnIY)
* [RepositoryFolderHelper](repository-folder-helper.md) - Provides some utilities when working with repository folders.
* [StageInputUpdate](stage-input-update.md) - Stages updates in flake inputs.
* [TagPush](tag-push.md) - Reacts to CommittedChangesTagged events.
