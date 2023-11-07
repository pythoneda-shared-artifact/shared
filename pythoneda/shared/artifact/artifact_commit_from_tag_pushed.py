"""
pythoneda/shared/artifact/artifact_commit_from_tag_pushed.py

This file declares the ArtifactCommitFromTagPushed class.

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
import os
from pythoneda.shared.artifact.events import Change, TagPushed
from pythoneda.shared.artifact.events.artifact import ArtifactChangesCommitted
from pythoneda.shared.git import (
    GitAdd,
    GitAddFailed,
    GitCommit,
    GitCommitFailed,
    GitRepo,
)
import requests


class ArtifactCommitFromTagPushed(ArtifactEventListener):
    """
    Reacts to TagPushed events.

    Class name: ArtifactCommitFromTagPushed

    Responsibilities:
        - React to TagPushed events.

    Collaborators:
        - pythoneda.shared.artifact.events.TagPushed
        - pythoneda.shared.artifact.events.artifact.ArtifactChangesCommitted
    """

    def __init__(self, folder: str):
        """
        Creates a new ArtifactCommitFromTagPushed instance.
        :param folder: The artifact's repository folder.
        :type folder: str
        """
        super().__init__(folder)
        self._enabled = True

    async def listen(self, event: TagPushed) -> ArtifactChangesCommitted:
        """
        Gets notified of a TagPushed event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact.events.artifact.ArtifactChangesCommitted
        """
        if not self.enabled:
            return None
        result = None
        ArtifactCommitFromTagPushed.logger().debug(f"Received {event}")
        result = await self.update_artifact_version(event)
        return result

    async def update_artifact_version(
        self, event: TagPushed
    ) -> ArtifactChangesCommitted:
        """
        Conditionally updates the artifact version.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact.events.artifact.ArtifactChangesCommitted
        """
        result = None
        artifact_repo = None
        # First, check if the event refers to the domain space of this artifact.
        if self.refers_to_my_decision_space(event.repository_url):
            flake = None
            # retrieve subfolder for the flake
            flake = self.flake_path(event.repository_url)

            if flake is not None and self.retrieve_version_in_flake(flake) != event.tag:
                # update the version and hash in the flake of the artifact repository
                version_updated = await self.update_version_in_flake(event.tag, flake)
                if version_updated:
                    hash, change = await self.commit_artifact_changes(
                        flake, event.repository_url, event.tag
                    )
                    if hash:
                        result = ArtifactChangesCommitted(change, hash, event.id)

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
            ArtifactCommitFromTagPushed.logger().error(
                f"Could not check if {url} exists"
            )
            ArtifactCommitFromTagPushed.logger().error(err)

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
        self, flake: str, domainRepoUrl: str, domainTag: str
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
        :rtype: (str, pythoneda.shared.artifact.events.Change)
        """
        result = (None, None)
        try:
            GitAdd(self.repository_folder).add(flake)
            hash, diff = GitCommit(self.repository_folder).commit(
                f"New tag {domainTag} in {domainRepoUrl}"
            )
            repo = GitRepo.from_folder(self.repository_folder)
            result = (
                hash,
                Change.from_unidiff_text(
                    diff, repo.url, repo.rev, self.repository_folder
                ),
            )
        except GitAddFailed as err:
            ArtifactCommitFromTagPushed.logger().error(err)
        except GitCommitFailed as err:
            ArtifactCommitFromTagPushed.logger().error(err)
        return result
