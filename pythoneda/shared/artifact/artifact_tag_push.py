"""
pythoneda/shared/artifact/artifact_tag_push.py

This file declares the ArtifactTagPush class.

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
from pythoneda.shared.artifact.events.artifact import (
    ArtifactCommitTagged,
    ArtifactTagPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class ArtifactTagPush(ArtifactEventListener):
    """
    Reacts to ArtifactCommitTagged events.

    Class name: ArtifactTagPush

    Responsibilities:
        - React to ArtifactCommitTagged events.

    Collaborators:
        - pythoneda.shared.artifact.events.artifact.ArtifactCommitTagged
        - pythoneda.shared.artifact.events.artifact.ArtifactTagPushed
    """

    def __init__(self, folder: str):
        """
        Creates a new ArtifactTagPush instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)
        self._enabled = True

    async def listen(self, event: ArtifactCommitTagged) -> ArtifactTagPushed:
        """
        Gets notified of an ArtifactCommitTagged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.artifact.ArtifactCommitTagged
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact.events.artifact.ArtifactTagPushed
        """
        result = None
        ArtifactTagPush.logger().debug(f"Received {event}")
        result = await self.push_tag_artifact(event)
        return result

    async def push_tag_artifact(self, event: ArtifactCommitTagged) -> ArtifactTagPushed:
        """
        Tags an artifact repository.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.artifact.ArtifactCommitCommitted
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact.events.artifact.ArtifactTagPushed
        """
        if not self.enabled:
            return None
        result = None
        try:
            GitPush(event.repository_folder).push_tags()
            result = ArtifactTagPushed(
                event.tag,
                event.commit,
                event.repository_url,
                event.branch,
                event.repository_folder,
                event.id,
            )
        except GitPushFailed as err:
            ArtifactTagPush.logger().error(f"Error pushing tags")
            ArtifactTagPush.logger().error(err)
        return result
