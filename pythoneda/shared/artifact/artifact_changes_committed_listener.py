"""
pythoneda/shared/artifact/artifact_changes_committed_listener.py

This file declares the ArtifactChangesCommittedListener class.

Copyright (C) 2023-today rydnr's pythoneda-shared-artifact/shared

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from .artifact import Artifact
from pythoneda.shared.artifact_changes.events import (
    ArtifactChangesCommitted,
    ArtifactCommitPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class ArtifactChangesCommittedListener(Artifact):
    """
    Reacts to ArtifactChangesCommitted events.

    Class name: ArtifactChangesCommittedListener

    Responsibilities:
        - React to ArtifactChangesCommitted events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        - pythoneda.shared.artifact_changes.events.CommittedChangesPushed
    """

    def __init__(self):
        """
        Creates a new ArtifactChangesCommittedListener instance.
        """
        super().__init__()

    @classmethod
    async def listen(cls, event: ArtifactChangesCommitted) -> ArtifactCommitPushed:
        """
        Gets notified of an ArtifactChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        """
        result = None
        Artifact.logger().debug(f"Received {event}")
        result = await cls().push_artifact_commit(event)
        return result

    async def push_artifact_commit(
        self, event: ArtifactChangesCommitted
    ) -> ArtifactCommitPushed:
        """
        Push a commit in an artifact repository.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        """
        result = None
        try:
            GitPush(event.change.repository_folder).push_all()
            result = ArtifactCommitPushed(event.change, event.commit, event.id)
        except GitPushFailed as err:
            ArtifactChangesCommittedListener.logger().error(err)
            result = None

        return result
