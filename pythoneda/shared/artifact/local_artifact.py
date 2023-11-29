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
from .abstract_artifact import AbstractArtifact
from .commit_push import CommitPush
from .commit_tag import CommitTag
from .repository_folder_helper import RepositoryFolderHelper
from .tag_push import TagPush
import abc
from pythoneda.shared.artifact.events import (
    CommittedChangesPushed,
    CommittedChangesTagged,
    StagedChangesCommitted,
    TagPushed,
)
from pythoneda.shared.git import GitTag
from typing import Callable, List


class LocalArtifact(AbstractArtifact, abc.ABC):
    """
    Represents Artifacts whose repository is available locally.

    Class name: LocalArtifact

    Responsibilities:
        - Artifact persisted in a local folder.

    Collaborators:
        - None
    """

    def __init__(
        self,
        name: str,
        version: str,
        urlFor: Callable[[str], str],
        inputs: List,
        templateSubfolder: str,
        description: str,
        homepage: str,
        licenseId: str,
        maintainers: List,
        copyrightYear: int,
        copyrightHolder: str,
        repositoryFolder: str,
    ):
        """
        Creates a new LocalArtifact instance.
        :param name: The name of the artifact.
        :type name: str
        :param version: The version of the artifact.
        :type version: str
        :param urlFor: The function to obtain the url of the artifact for a given version.
        :type urlFor: Callable[[str],str]
        :param inputs: The flake inputs.
        :type inputs: List[pythoneda.shared.nix_flake.NixFlakeInput]
        :param templateSubfolder: The template subfolder, if any.
        :type templateSubfolder: str
        :param description: The flake description.
        :type description: str
        :param homepage: The project's homepage.
        :type homepage: str
        :param licenseId: The id of the license of the project.
        :type licenseId: str
        :param maintainers: The maintainers of the project.
        :type maintainers: List[str]
        :param copyrightYear: The copyright year.
        :type copyrightYear: year
        :param copyrightHolder: The copyright holder.
        :type copyrightHolder: str
        :param repositoryFolder: The repository folder.
        :type repositoryFolder: str
        """
        super().__init__(
            name,
            version,
            urlFor,
            inputs,
            templateSubfolder,
            description,
            homepage,
            licenseId,
            maintainers,
            copyrightYear,
            copyrightHolder,
        )
        self._repository_folder = repositoryFolder

    @property
    def repository_folder(self) -> str:
        """
        Retrieves the repository folder.
        :return: Such location.
        :rtype: str
        """
        return self._repository_folder

    @classmethod
    def find_out_version(cls, repositoryFolder: str) -> str:
        """
        Retrieves the version of the flake under given folder.
        :param repositoryFolder: The repository folder.
        :type repositoryFolder: str
        :return: The version
        :rtype: str
        """
        return RepositoryFolderHelper.find_out_version(repositoryFolder)

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
        return RepositoryFolderHelper.find_out_repository_folder(
            referenceRepositoryFolder, url
        )

    async def commit_push(
        self, event: StagedChangesCommitted
    ) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesPushed
        """
        return await CommitPush(self.repository_folder).listen(event)

    async def commit_tag(self, event: CommittedChangesPushed) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommitedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesTagged
        """
        result = await CommitTag(self.repository_folder).listen(event)
        return result

    async def tag_push(self, event: CommittedChangesTagged) -> TagPushed:
        """
        Gets notified of a CommittedChangesTagged event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommittedChangesTagged
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.TagPushed
        """
        return await TagPush(self.repository_folder).listen(event)
