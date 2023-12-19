"""
pythoneda/shared/artifact/abstract_artifact.py

This file declares the AbstractArtifact class.

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
import abc
import os
from pythoneda import EventListener, listen, PrimaryPort
from pythoneda.shared.artifact.events import (
    CommittedChangesPushed,
    CommittedChangesTagged,
    StagedChangesCommitted,
    TagPushed,
)
from pythoneda.shared.git import GitRepo
from pythoneda.shared.nix_flake import NixFlake
from typing import Callable, List


class AbstractArtifact(NixFlake, EventListener, abc.ABC):
    """
    Common logic for Artifacts.

    Class name: AbstractArtifact

    Responsibilities:
        - Provide common logic for Artifacts.

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
    ):
        """
        Creates a new AbstractArtifact instance.
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

    @classmethod
    @property
    def is_one_shot_compatible(cls) -> bool:
        """
        Retrieves whether this primary port should be instantiated when
        "one-shot" behavior is active.
        It should return False if the port listens to future messages
        from outside.
        :return: True in such case.
        :rtype: bool
        """
        return True

    @classmethod
    @property
    def org(cls) -> str:
        """
        Retrieves the organization.
        :return: Such information.
        :rtype: str
        """
        result, _ = GitRepo.extract_repo_owner_and_repo_name(cls.url)
        return result

    @classmethod
    @property
    def repo(cls) -> str:
        """
        Retrieves the repo.
        :return: Such information.
        :rtype: str
        """
        _, result = GitRepo.extract_repo_owner_and_repo_name(cls.url)
        return result

    @classmethod
    @property
    @abc.abstractmethod
    def url(cls) -> str:
        """
        Retrieves the url.
        :return: Such url.
        :rtype: str
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_StagedChangesCommitted(
        cls, event: StagedChangesCommitted
    ) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.CommittedChangesPushed
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_CommittedChangesPushed(
        cls, event: CommittedChangesPushed
    ) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.CommitedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.CommittedChangesTagged
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_CommittedChangesTagged(
        cls, event: CommittedChangesTagged
    ) -> TagPushed:
        """
        Gets notified of a CommittedChangesTagged event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.CommittedChangesTagged
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.TagPushed
        """
        pass
