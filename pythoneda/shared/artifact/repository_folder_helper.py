"""
pythoneda/shared/artifact/local_artifact.py

This file declares the LocalArtifact class.

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
from pythoneda.shared.git import GitRepo, GitTag


class RepositoryFolderHelper:
    """
    Provides some utilities when working with repository folders.

    Class name: RepositoryFolderHelper

    Responsibilities:
        - Provide useful methods to LocalArtifact and LocalLocalArtifact classes.

    Collaborators:
        - None
    """

    @classmethod
    def find_out_version(cls, repositoryFolder: str) -> str:
        """
        Retrieves the version of the flake under given folder.
        :param repositoryFolder: The repository folder.
        :type repositoryFolder: str
        :return: The version
        :rtype: str
        """
        return GitTag(repositoryFolder).current_tag()

    @classmethod
    def find_out_repository_folder(
        cls, referenceRepositoryFolder: str, url: str
    ) -> str:
        """
        Retrieves the non-artifact repository folder based on a convention, assuming
        given folder holds another PythonEDA project.
        :param referenceRepositoryFolder: The other repository folder.
        :type referenceRepositoryFolder: str
        :param url: The url of the repository we want to know where it's cloned.
        :type url: str
        :return: The repository folder, or None if not found.
        :rtype: str
        """
        result = None
        parent = os.path.dirname(referenceRepositoryFolder)
        grand_parent = os.path.dirname(parent)
        owner, repo = GitRepo.extract_repo_owner_and_repo_name(url)
        candidate = os.path.join(grand_parent, owner, repo)
        if os.path.isdir(os.path.join(candidate, ".git")) and (
            GitRepo(candidate).url == url
        ):
            result = candidate
        else:
            RepositoryFolderHelper.logger().error(
                f"Folder {candidate} does not exist or it's not a clone of {url}"
            )
        return result
