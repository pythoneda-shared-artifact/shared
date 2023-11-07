"""
pythoneda/shared/artifact/artifact_commit_push.py

This file declares the ArtifactCommitPush class.

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
from .artifact_event_listener import ArtifactEventListener
from pythoneda.shared.artifact_changes.events import (
    ArtifactChangesCommitted,
    ArtifactCommitPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class ArtifactCommitPush(ArtifactEventListener):
    """
    Reacts to ArtifactChangesCommitted events.

    Class name: ArtifactCommitPush

    Responsibilities:
        - React to ArtifactChangesCommitted events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        - pythoneda.shared.artifact_changes.events.CommittedChangesPushed
    """

    def __init__(self, folder: str):
        """
        Creates a new ArtifactCommitPush instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)
        self._enabled = True

    async def listen(self, event: ArtifactChangesCommitted) -> ArtifactCommitPushed:
        """
        Gets notified of an ArtifactChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        """
        if not self.enabled:
            return None
        ArtifactCommitPush.logger().debug(f"Received {event}")
        result = await self.push_artifact_commit(event)
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
            GitPush(event.change.repository_folder).push()
            result = ArtifactCommitPushed(event.change, event.commit, event.id)
        except GitPushFailed as err:
            ArtifactCommitPush.logger().error(err)
            result = None

        return result
