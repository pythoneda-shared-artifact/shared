"""
pythoneda/shared/artifact/committed_changes_tagged_listener.py

This file declares the CommittedChangesTaggedListener class.

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
from pythoneda.shared.artifact_changes.events import CommittedChangesTagged, TagPushed
from pythoneda.shared.git import GitPush, GitPushFailed


class CommittedChangesTaggedListener(Artifact):
    """
    Reacts to CommittedChangesTagged events.

    Class name: CommittedChangesTaggedListener

    Responsibilities:
        - React to CommittedChangesTagged events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.CommittedChangesTagged
        - pythoneda.shared.artifact_changes.events.TagPushed
    """

    def __init__(self):
        """
        Creates a new CommittedChangesTaggedListener instance.
        """
        super().__init__()

    @classmethod
    async def listen(cls, event: CommittedChangesTagged) -> TagPushed:
        """
        Gets notified of a CommittedChangesTagged event.
        Pushes the changes and emits a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.StagedChangesCommitted
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.CommittedChangesPushed
        """
        result = None
        CommittedChangesTaggedListener.logger().debug(f"Received {event}")
        pushed = await cls().push_tags(event.repository_folder)
        if pushed:
            result = TagPushed(
                event.tag,
                event.commit,
                event.repository_url,
                event.branch,
                event.repository_folder,
                event.id,
            )
        return result

    async def push_tags(self, folder: str) -> bool:
        """
        Pushes the tags in given folder.
        :param folder: The folder.
        :type folder: str
        :return: True if the operation succeeds.
        :rtype: bool
        """
        result = False
        try:
            GitPush(folder).push_tags()
            result = True
        except GitPushFailed as err:
            CommittedChangesTaggedListener.logger().error(err)
            result = False
        return result
