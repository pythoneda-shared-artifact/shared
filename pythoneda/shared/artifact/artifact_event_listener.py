"""
pythoneda/shared/artifact/artifact_event_listener.py

This file declares the ArtifactEventListener class.

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
import os
from pythoneda import BaseObject
from pythoneda.shared.git import (
    GitAdd,
    GitAddFailed,
    GitCommit,
    GitCommitFailed,
    GitRepo,
    GitTag,
    GitTagFailed,
    Version,
)
import subprocess


class ArtifactEventListener(BaseObject):
    """
    Provides common Artifact-related operations.

    Class name: ArtifactEventListener

    Responsibilities:
        - Provide operations to listeners.

    Collaborators:
        - None
    """

    def __init__(self):
        """
        Creates a new ArtifactEventListener instance.
        """
        super().__init__()

    def own_flake(self, folder: str) -> bool:
        """
        Checks if the repository has its own flake, so it doesn't have an artifact space.
        :param folder: The repository folder.
        :type folder: str
        :return: True in such case.
        :rtype: bool
        """
        return os.path.exists(os.path.join(folder, "flake.nix"))

    async def update_version_in_flake(self, version: str, flake: str) -> bool:
        """
        Updates the version in given flake file.
        :param version: The new version.
        :type version: str
        :param flake: The flake file.
        :type flake: str
        :return: True if the flake could be updated.
        :rtype: bool
        """
        result = True
        home_path = os.environ.get("HOME")
        print(
            f"***** running {home_path}/bin/update-sha256-nix-flake.sh -f {flake} -V {version} in {os.path.dirname(flake)}"
        )
        try:
            subprocess.run(
                [
                    f"{home_path}/bin/update-sha256-nix-flake.sh",
                    "-f",
                    flake,
                    "-V",
                    version,
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(flake),
            )
        except subprocess.CalledProcessError as err:
            Artifact.logger().error(err.stdout)
            Artifact.logger().error(err.stderr)
            result = False

        return True

    async def tag(self, folder: str) -> Version:
        """
        Creates a tag and emits a CommittedChangesTagged event.
        :param folder: The repository folder.
        :type folder: str
        :return: The tagged version.
        :rtype: pythoneda.shared.git.Version
        """
        git_repo = GitRepo.from_folder(folder)
        result = git_repo.increase_patch(True)
        # check if there's a flake in the root folder.
        if self.own_flake(folder):
            flake = os.path.join(folder, "flake.nix")
            # if there's a flake, change and commit the version change before tagging.
            version_updated = await self.update_version_in_flake(result.value, flake)
            if version_updated:
                try:
                    GitAdd(folder).add(flake)
                    GitCommit(folder).commit(f"Updated version to {result.value}")
                    GitTag(folder).tag(result)
                except GitAddFailed as err:
                    CommittedChangesPushedListener.logger().error(
                        "Could not stage changes"
                    )
                    CommittedChangesPushedListener.logger().error(err)
                    result = None
                except GitCommitFailed as err:
                    CommittedChangesPushedListener.logger().error(
                        "Could not commit staged changes"
                    )
                    CommittedChangesPushedListener.logger().error(err)
                    result = None
                except GitTagFailed as err:
                    CommittedChangesPushedListener.logger().error(
                        "Could not create tag"
                    )
                    CommittedChangesPushedListener.logger().error(err)
                    result = None
        return result
