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
from pythoneda import attribute, BaseObject
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

    def __init__(self, folder: str):
        """
        Creates a new ArtifactEventListener instance.
        """
        super().__init__()
        self._repository_folder = folder
        self._enabled = False

    @property
    @attribute
    def repository_folder(self) -> str:
        """
        Retrieves the repository folder of the artifact.
        :return: Such folder.
        :rtype: str
        """
        return self._repository_folder

    @property
    def enabled(self) -> bool:
        """
        Checks if this listener is enabled or not.
        :return: Such flag.
        :rtype: bool
        """
        return self._enabled

    @property
    def repository_url(self) -> str:
        """
        Retrieves the remote url of the current branch in the cloned folder.
        :return: Such url.
        :rtype: str
        """
        return GitRepo.from_folder(self.repository_folder).remote_url

    def refers_to_my_decision_space(self, url: str) -> str:
        """
        Checks whether given url matches the decision space of this artifact.
        :param url: The repository url.
        :type url: str
        :return: True if it refers to the decision space.
        :rtype: bool
        """
        return self.repository_url == f"{url}-artifact"

    def own_flake(self, folder: str) -> bool:
        """
        Checks if the repository has its own flake, so it doesn't have an artifact space.
        :param folder: The repository folder.
        :type folder: str
        :return: True in such case.
        :rtype: bool
        """
        return os.path.exists(os.path.join(folder, "flake.nix"))

    def flake_path(self, url: str) -> str:
        """
        Retrieves the path of the flake associated to given decision-space repository url.
        :param url: The repository url.
        :type url: str
        :return: The path of the flake, or None if the flake does not exist.
        :rtype: str
        """
        (owner, repo_name) = GitRepo.extract_repo_owner_and_repo_name(url)
        result = os.path.join(self.repository_folder, repo_name, "flake.nix")
        if not os.path.exists(result):
            result = None

        return result

    def retrieve_version_in_flake(self, flake: str) -> str:
        """
        Retrieves the version in given flake.
        :param flake: The flake.
        :type flake: str
        :return: The version of the package.
        :rtype: str
        """
        result = None
        home_path = os.environ.get("HOME")
        completed_process = subprocess.run(
            [f"{home_path}/bin/extract-nix-flake-version.sh", "-f", flake],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(flake),
        )
        if completed_process.returncode == 0:
            result = completed_process.stdout
        else:
            if completed_process.stdout != "":
                ArtifactEventListener.logger().error(completed_process.stdout)
            if completed_process.stderr != "":
                ArtifactEventListener.logger().error(completed_process.stderr)

        return result

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
            ArtifactEventListener.logger().error(err.stdout)
            ArtifactEventListener.logger().error(err.stderr)
            result = False

        return result

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
                    ArtifactEventListener.logger().error("Could not stage changes")
                    ArtifactEventListener.logger().error(err)
                    result = None
                except GitCommitFailed as err:
                    ArtifactEventListener.logger().error(
                        "Could not commit staged changes"
                    )
                    ArtifactEventListener.logger().error(err)
                    result = None
                except GitTagFailed as err:
                    ArtifactEventListener.logger().error("Could not create tag")
                    ArtifactEventListener.logger().error(err)
                    result = None
        return result

    @classmethod
    def build_input_name(cls, url: str) -> str:
        """
        Builds the name of the flake input for given url, based on a convention.
        :param url: The repository url.
        :type url: str
        :return: The input name.
        :rtype: str
        """
        org, repo = GitRepo.extract_repo_owner_and_repo_name(url)
        return f"{org}-{repo}"
