"""
pythoneda/shared/artifact/commit_tag.py

This file declares the CommitTag class.

Copyright (C) 2023-today rydnr's pythoneda-shared-pythoneda/domain-artifact

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
from pythoneda.shared.artifact.events import (
    CommittedChangesPushed,
    CommittedChangesTagged,
)


class CommitTag(ArtifactEventListener):
    """
    Reacts to CommittedChangesTagged events.

    Class name: CommitTag

    Responsibilities:
        - React to CommittedChangesPushed events.

    Collaborators:
        - pythoneda.shared.artifact.events.CommittedChangesPushed
        - pythoneda.shared.artifact.events.CommittedChangesTagged
    """

    def __init__(self, folder: str):
        """
        Creates a new CommitTag instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)
        self._enabled = True

    async def listen(self, event: CommittedChangesPushed) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommitedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesTagged
        """
        if not self.enabled:
            return None
        result = None
        CommitTag.logger().debug(f"Received {event}")
        version = await self.tag(event.change.repository_folder)
        if version is not None:
            result = CommittedChangesTagged(
                version.value,
                event.commit,
                event.change.repository_url,
                event.change.branch,
                event.change.repository_folder,
                event.id,
            )
        return result
