# vim: set fileencoding=utf-8
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
from .repository_folder_helper import RepositoryFolderHelper
import os
from pythoneda.shared import attribute, BaseObject
from pythoneda.shared.git import (
    GitAdd,
    GitAddFailed,
    GitCheckAttr,
    GitCheckAttrFailed,
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

    def refers_to_my_decision_space(self, url: str) -> bool:
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
            ArtifactEventListener.logger().debug(
                f"Running {home_path}/bin/update-sha256-nix-flake.sh -f {flake} -V {version} in {os.path.dirname(flake)}"
            )
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

    async def tag_flake_in(self, version: Version, folder: str) -> bool:
        """
        Updates the version and commits and tags the changes in the flake under given folder.
        :param version: The new version.
        :type version: pythoneda.shared.git.Version
        :param folder: The flake folder.
        :type folder: str
        :return: True if the operation succeeds; False otherwise.
        :rtype: bool
        """
        result = False
        flake = os.path.join(folder, "flake.nix")
        # if there's a flake, change and commit the version change before tagging.
        version_updated = await self.update_version_in_flake(version.value, flake)
        if version_updated:
            try:
                ArtifactEventListener.logger().debug("Updating version in {folder}")
                GitAdd(folder).add(flake)
                GitCommit(folder).commit(f"Updated version to {version.value}")
                GitTag(folder).create_tag(
                    version, f"Updated version to {version.value}"
                )
                result = True
            except GitAddFailed as err:
                ArtifactEventListener.logger().error("Could not stage changes")
                ArtifactEventListener.logger().error(err)
            except GitCommitFailed as err:
                ArtifactEventListener.logger().error("Could not commit staged changes")
                ArtifactEventListener.logger().error(err)
            except GitTagFailed as err:
                ArtifactEventListener.logger().error("Could not create tag")
                ArtifactEventListener.logger().error(err)
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
            if not await self.tag_flake_in(result, folder):
                result = None
        else:
            def_folder = self.find_def_repository_folder(folder)
            if def_folder is None:
                ArtifactEventListener.logger().error(
                    f"Could not find def repository for {folder}"
                )
                result = None
            else:
                if not await self.tag_flake_in(result, def_folder):
                    result = None

        return result

    def find_def_repository_folder(self, folder: str) -> str:
        """
        Retrieves the folder of the repository with the definition of the repository cloned in given folder.
        :param folder: The folder with the decision space repository.
        :type folder: str
        :return: The folder with the cloned repository of the definition of the source repository.
        :rtype: str
        """
        result = None
        try:
            url = GitCheckAttr(folder).check_attr("def", ".gitattributes")
            result = RepositoryFolderHelper.find_out_repository_folder(folder, url)
        except GitCheckAttrFailed as err:
            ArtifactEventListener.logger().error(err)
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
