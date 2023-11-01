"""
pythoneda/shared/artifact/artifact_commit_pushed_listener.py

This file declares the ArtifactCommitPushedListener class.

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
    ArtifactCommitPushed,
    ArtifactCommitTagged,
)


class ArtifactCommitPushedListener(ArtifactEventListener):
    """
    Reacts to ArtifactCommitPushed events.

    Class name: ArtifactCommitPushedListener

    Responsibilities:
        - React to ArtifactCommitPushed events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        - pythoneda.shared.artifact_changes.events.CommittedChangesPushed
    """

    def __init__(self):
        """
        Creates a new ArtifactCommitPushedListener instance.
        """
        super().__init__()

    async def listen(self, event: ArtifactCommitPushed) -> ArtifactCommitTagged:
        """
        Gets notified of an ArtifactCommitPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        :return: An event notifying the commit in the artifact repository has been tagged.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitTagged
        """
        result = None
        ArtifactCommitPushedListener.logger().debug(f"Received {event}")
        result = await self.tag_artifact(event)
        return result

    async def tag_artifact(self, event: ArtifactCommitPushed) -> ArtifactCommitTagged:
        """
        Tags an artifact repository.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        :return: An event notifying the commit in the artifact repository has been tagged.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitTagged
        """
        result = None
        version = await self.tag(event.change.repository_folder)
        if version is not None:
            result = ArtifactCommitTagged(
                version.value,
                event.commit,
                event.change.repository_url,
                event.change.branch,
                event.change.repository_folder,
                event.id,
            )
        return result
