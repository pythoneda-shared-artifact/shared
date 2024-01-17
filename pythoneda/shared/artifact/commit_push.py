# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/commit_push.py

This file declares the CommitPush class.

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
from pythoneda.shared.artifact.events import (
    StagedChangesCommitted,
    CommittedChangesPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class CommitPush(ArtifactEventListener):
    """
    Reacts to StagedChangesCommitted events.

    Class name: CommitPush

    Responsibilities:
        - React to StagedChangesCommitted events.

    Collaborators:
        - pythoneda.shared.artifact.events.StagedChangesCommitted
        - pythoneda.shared.artifact.events.CommittedChangesPushed
    """

    def __init__(self, folder: str):
        """
        Creates a new CommitPush instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)
        self._enabled = True

    async def listen(self, event: StagedChangesCommitted) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesPushed
        """
        if not self.enabled:
            return None
        result = None
        CommitPush.logger().debug(f"Received {event}")
        pushed = await self.push(event.change.repository_folder)
        if pushed:
            result = CommittedChangesPushed(event.change, event.commit, event.id)
        return result

    async def push(self, folder: str) -> bool:
        """
        Pushes the commits in given folder.
        :param folder: The folder.
        :type folder: str
        :return: True if the operation succeeds.
        :rtype: bool
        """
        try:
            CommitPush.logger().info(f"Pushing changes in folder {folder}")
            GitPush(folder).push()
            result = True
        except GitPushFailed as err:
            CommitPush.logger().error("Could not push commits")
            CommitPush.logger().error(err)
            result = False
        return result
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
