"""
pythoneda/shared/artifact/tag_pushed_listener.py

This file declares the TagPushedListener class.

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
import os
from pythoneda.shared.artifact_changes import Change
from pythoneda.shared.artifact_changes.events import ArtifactChangesCommitted, TagPushed
from pythoneda.shared.git import (
    GitAdd,
    GitAddFailed,
    GitCommit,
    GitCommitFailed,
    GitRepo,
)
import requests


class TagPushedListener(Artifact):
    """
    Reacts to TagPushed events.

    Class name: TagPushedListener

    Responsibilities:
        - React to TagPushed events.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.TagPushed
        - pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
    """

    def __init__(self):
        """
        Creates a new TagPushedListener instance.
        """
        super().__init__()

    @classmethod
    async def listen(cls, event: TagPushed) -> ArtifactChangesCommitted:
        """
        Gets notified of a TagPushed event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        result = None
        Artifact.logger().debug(f"Received {event}")
        result = await cls().update_artifact_version(event)
        return result

    async def update_artifact_version(
        self, event: TagPushed
    ) -> ArtifactChangesCommitted:
        """
        Conditionally updates the artifact version.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        result = None
        artifact_repo = None
        # check if there's a flake in the root folder.
        if not self.own_flake(event.repository_folder):
            # retrieve the artifact repository, if any.
            artifact_repo_url = self.artifact_repository_url_for(event.repository_url)

        artifact_repo_folder = None
        if artifact_repo_url is not None:
            # find out the local folder for the artifact repository
            artifact_repo_folder = self.artifact_repository_folder_of(
                artifact_repo_url, event.repository_folder
            )

        flake = None
        if artifact_repo_folder is not None:
            # retrieve subfolder for the flake
            flake = self.flake_path_in_artifact_repository(
                artifact_repo_folder, event.repository_url
            )

        if flake is not None:
            # update the version and hash in the flake of the artifact repository
            version_updated = await self.update_version_in_flake(event.tag, flake)
            if version_updated:
                hash, change = await self.commit_artifact_changes(
                    artifact_repo_folder, flake, event.repository_url, event.tag
                )
                if hash:
                    result = ArtifactChangesCommitted(change, hash, event.id)

        return result

    def artifact_repository_url_for(self, url: str) -> str:
        """
        Retrieves the url of the artifact repository for given url.
        :param url: The repository url.
        :type url: str
        :return: The url of the artfifact repository, or None if not found.
        :rtype: str
        """
        result = None
        artifact_url = f"{url}-artifact"
        if self.url_exists(artifact_url):
            result = artifact_url

        return result

    def url_exists(self, url: str) -> bool:
        """
        Checks if given url exists.
        :param url: The url to check.
        :type url: str
        :return: True if the url exists.
        :rtype: bool
        """
        result = False
        try:
            response = requests.head(url)
            if response.status_code == 200:
                result = True
        except requests.RequestException as err:
            Artifact.logger().error(f"Could not check if {url} exists")
            Artifact.logger().error(err)

        return result

    def artifact_repository_folder_of(
        self, artifactRepoUrl: str, domainRepoFolder: str
    ) -> str:
        """
        Retrieves the folder of the artifact repository for the domain repository cloned in given folder.
        :param artifactRepoUrl: The url of the artifact repository.
        :type artifactRepoUrl: str
        :param domainRepoFolder: The folder where the associated domain repository is cloned.
        :type domainRepoFolder: str
        :return: The folder where the artifact repository is cloned, or None if it doesn't exist.
        :rtype: str
        """
        # TODO: make the folder layout flexible and customizable
        result = None
        _, repo = GitRepo.extract_repo_owner_and_repo_name(artifactRepoUrl)
        artifact_repo_folder = os.path.join(os.path.dirname(domainRepoFolder), repo)
        if (
            os.path.exists(artifact_repo_folder)
            and os.path.isdir(artifact_repo_folder)
            and os.path.exists(os.path.join(artifact_repo_folder, ".git"))
        ):
            result = artifact_repo_folder

        return result

    def flake_path_in_artifact_repository(
        self, artifactRepoFolder: str, domainRepoUrl: str
    ) -> str:
        """
        Retrieves the path of the domain flake within its artifact repository.
        :param artifactRepoFolder: The folder where the artifact repository is cloned.
        :type artifactRepoFolder: str
        :param domainRepoUrl: The url of the domain repository.
        :type domainRepoUrl: str
        :return: The flake path, or None if not found.
        :rtype: str
        """
        result = None
        _, repo = GitRepo.extract_repo_owner_and_repo_name(domainRepoUrl)
        flake = os.path.join(artifactRepoFolder, repo, "flake.nix")
        if os.path.exists(flake):
            result = flake
        return result

    async def commit_artifact_changes(
        self, artifactRepoFolder: str, flake: str, domainRepoUrl: str, domainTag: str
    ):
        """
        Commits the changes in the artifact repository.
        :param artifactRepoFolder: The folder where the artifact repository is cloned.
        :type artifactRepoFolder: str
        :param flake: The flake.nix file.
        :type flake: str
        :param domainRepoUrl: The url of the domain repository.
        :type domainRepoUrl: str
        :param domainTag: The tag of the domain repository triggering the flake.nix changes.
        :type domainTag: str
        :return: A tuple with the commit and the change, or (None, None).
        :rtype: (str, pythoneda.shared.artifact_changes.Change)
        """
        result = (None, None)
        try:
            GitAdd(artifactRepoFolder).add(flake)
            hash, diff = GitCommit(artifactRepoFolder).commit(
                f"New tag {domainTag} in {domainRepoUrl}"
            )
            repo = GitRepo.from_folder(artifactRepoFolder)
            result = (
                hash,
                Change.from_unidiff_text(diff, repo.url, repo.rev, artifactRepoFolder),
            )
        except GitAddFailed as err:
            TagPushedListener.logger().error(err)
        except GitCommitFailed as err:
            TagPushedListener.logger().error(err)
        return result
