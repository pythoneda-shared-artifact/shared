"""
pythoneda/shared/artifact/committed_changes_pushed_listener.py

This file declares the CommittedChangesPushedListener class.

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
from .artifact import Artifact
from pythoneda.shared.artifact_changes.events import (
    CommittedChangesPushed,
    CommittedChangesTagged,
)


class CommittedChangesPushedListener(Artifact):
    """
    Reacts to CommittedChangesTagged events.

    Class name: CommittedChangesPushedListener

    Responsibilities:
        - React to CommittedChangesPushed events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.CommittedChangesPushed
        - pythoneda.shared.artifact_changes.events.CommittedChangesTagged
    """

    def __init__(self):
        """
        Creates a new CommittedChangesTaggedListener instance.
        """
        super().__init__()

    @classmethod
    async def listen(cls, event: CommittedChangesPushed) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.CommitedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.CommittedChangesTagged
        """
        result = None
        CommittedChangesPushedListener.logger().debug(f"Received {event}")
        version = await cls().tag(event.change.repository_folder)
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
