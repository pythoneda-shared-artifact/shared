"""
pythoneda/shared/artifact/artifact_commit_tagged_listener.py

This file declares the ArtifactCommitTaggedListener class.

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
    ArtifactCommitTagged,
    ArtifactTagPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class ArtifactCommitTaggedListener(ArtifactEventListener):
    """
    Reacts to ArtifactCommitTagged events.

    Class name: ArtifactCommitTaggedListener

    Responsibilities:
        - React to ArtifactCommitTagged events.

    Collaborators:
        - pythoneda.shared.artifact_commit.events.ArtifactCommitTagged
        - pythoneda.shared.artifact_commit.events.ArtifactTagPushed
    """

    def __init__(self):
        """
        Creates a new ArtifactCommitTaggedListener instance.
        """
        super().__init__()

    async def listen(self, event: ArtifactCommitTagged) -> ArtifactTagPushed:
        """
        Gets notified of an ArtifactCommitTagged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_commit.events.ArtifactCommitTagged
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact_commit.events.ArtifactTagPushed
        """
        result = None
        ArtifactCommitTaggedListener.logger().debug(f"Received {event}")
        result = await self.push_tag_artifact(event)
        return result

    async def push_tag_artifact(self, event: ArtifactCommitTagged) -> ArtifactTagPushed:
        """
        Tags an artifact repository.
        :param event: The event.
        :type event: pythoneda.shared.artifact_commit.events.ArtifactCommitCommitted
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact_commit.events.ArtifactTagPushed
        """
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
            ArtifactCommitTaggedListener.logger().error(f"Error pushing tags")
            ArtifactCommitTaggedListener.logger().error(err)
        return result
