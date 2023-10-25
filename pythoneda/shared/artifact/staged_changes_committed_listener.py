"""
pythoneda/shared/artifact/staged_changes_committed_listener.py

This file declares the StagedChangesCommittedListener class.

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
    StagedChangesCommitted,
    CommittedChangesPushed,
)
from pythoneda.shared.git import GitPush, GitPushFailed


class StagedChangesCommittedListener(Artifact):
    """
    Reacts to StagedChangesCommitted events.

    Class name: StagedChangesCommittedListener

    Responsibilities:
        - React to StagedChangesCommitted events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.StagedChangesCommitted
        - pythoneda.shared.artifact_changes.events.CommittedChangesPushed
    """

    def __init__(self):
        """
        Creates a new StagedChangesCommittedListener instance.
        """
        super().__init__()

    @classmethod
    async def listen(cls, event: StagedChangesCommitted) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.CommittedChangesPushed
        """
        result = None
        StagedChangesCommittedListener.logger().debug(f"Received {event}")
        pushed = await cls().push(event.change.repository_folder)
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
        result = False
        try:
            GitPush(folder).push_all()
            result = True
        except GitPushFailed as err:
            StagedChangesCommittedListener.logger().error("Could not push commits")
            StagedChangesCommittedListener.logger().error(err)
            result = False
        return result