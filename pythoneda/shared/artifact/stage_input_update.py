"""
pythoneda/shared/artifact/stage_input_update.py

This file declares the StageInputUpdate class.

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
from pythoneda.shared.artifact.events import ChangeStaged, TagPushed
from pythoneda.shared.git import GitAdd, GitAddFailed, GitDiff, GitRepo


class StageInputUpdate(ArtifactEventListener):
    """
    Stages updates in flake inputs.

    Class name: StageInputUpdate

    Responsibilities:
        - Update flake input versions and stage the changes.

    Collaborators:
        - pythoneda.shared.artifact.events.ChangeStaged
    """

    def __init__(self, folder: str):
        """
        Creates a new StageInputUpdate instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)

    async def listen(self, event: TagPushed) -> ChangeStaged:
        """
        Gets notified of a TagPushed event.
        :param event: The event.
        :return: An event notifying the change has been staged.
        :rtype: pythoneda.shared.artifact.events.ChangeStaged
        """
        if not self.enabled:
            return None
        StageInputUpdate.logger().debug(f"Received {event}")
        return await self.stage(event.repository_url, event.tag, event.id)

    async def stage(self, url: str, tag: str, tagPushedId: str) -> ChangeStaged:
        """
        Stages the changes of given files.
        :param url: The repository url of the dependency.
        :type url: str
        :param tag: The new tag of the dependency.
        :type tag: str
        :param tagPushedId: The id of the TagPushed event.
        :type tagPushedId: str
        :return: An event notifying the change has been staged.
        :rtype: pythoneda.shared.artifact.events.ChangeStaged
        """
        StageInputUpdate.logger().info(f"Staging changes in input {self.folder}")
        # 1. find out the repository folder from given url
        dependency_folder = RepositoryFolderHelper.find_out_repository_folder(
            self.folder, url
        )

        # 2. Create the artifact instance of the dependency
        artifact = NixFlake.from_folder(dependency_folder, tag)

        # 3. update this artifact's inputs, replacing the old one with this new version
        artifact.update_input(dependency.to_input())

        # 4. serialize this artifact to nix flake
        artifact.generate_flake(self.folder)

        # 5. update flake.lock
        NixFlake.update_flake_lock(self.folder)

        # 6. retrieve the Change
        change = Change.from_unidiff_text(
            GitDiff(self.folder).diff(),
            artifact.repository_url,
            artifact.branch,
            self.folder,
        )

        # 7. create the event
        result = ChangeStaged(change, tagPushedId)

        return result
