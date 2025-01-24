# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/commit.py

This file declares the Commit class.

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
from pythoneda.shared.artifact.events import ChangeStaged, StagedChangesCommitted
from pythoneda.shared.git import GitAdd, GitAddFailed, GitDiff, GitRepo
from typing import List


class Commit(ArtifactEventListener):
    """
    Reacts to ChangeStaged events.

    Class name: Commit

    Responsibilities:
        - React to ChangeStaged events.

    Collaborators:
        - pythoneda.shared.artifact.events.ChangeStaged
        - pythoneda.shared.artifact.events.StagedChangesCommitted
    """

    def __init__(self, folder: str):
        """
        Creates a new Commit instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)

    async def listen(self, event: ChangeStaged) -> StagedChangesCommitted:
        """
        Gets notified of a ChangeStaged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.ChangeStaged
        :return: An event notifying the change has been staged.
        :rtype: pythoneda.shared.artifact.events.StagedChangesCommitted
        """
        if not self.enabled:
            return None
        CommitPush.logger().debug(f"Received {event}")
        return await self.stage(event.files, event.repository_folder)

    async def stage(self, files: List, folder: str) -> StagedChangesCommitted:
        """
        Stages the changes of given files.
        :param files: The files with the changes to stage.
        :type files: List[str]
        :param folder: The folder.
        :type folder: str
        :return: An event notifying the change has been staged.
        :rtype: pythoneda.shared.artifact.events.StagedChangesCommitted
        """
        result = None
        try:
            Commit.logger().info(f"Committing changes in folder {folder}")
            for file in files:
                GitAdd(folder).add(file)
            urls = GitRepo.remote_urls(folder)
            if len(urls) > 0:
                result = ChangeStaged(
                    Change.from_unidiff_text(
                        GitDiff(folder).diff(),
                        urls[0],
                        GitRepo.current_branch(folder),
                        folder,
                    )
                )
        except GitAddFailed as err:
            Commit.logger().error("Could not stage changes in {files}")
            Commit.logger().error(err)
        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
