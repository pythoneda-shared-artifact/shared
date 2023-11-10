"""
pythoneda/shared/artifact/artifact.py

This file declares the Artifact class.

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
from .artifact_event_listener import ArtifactEventListener
import abc
import os
from pythoneda import EventListener, listen, PrimaryPort

from pythoneda.shared.artifact.events import (
    ArtifactChangesCommitted,
    ArtifactCommitPushed,
    ArtifactCommitTagged,
    ArtifactTagPushed,
    CommittedChangesPushed,
    CommittedChangesTagged,
    StagedChangesCommitted,
    TagPushed,
)
from pythoneda.shared.git import GitRepo
from pythoneda.shared.nix_flake import NixFlake
from typing import Callable, List


class Artifact(AbstractArtifact, abc.ABC):
    """
    Represents Artifacts.

    Class name: Artifact

    Responsibilities:
        - Provide a model for Artifacts.

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
        Creates a new Artifact instance.
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

    @classmethod
    @abc.abstractmethod
    async def listen_TagPushed(cls, event: TagPushed) -> ArtifactChangesCommitted:
        """
        Gets notified of a TagPushed event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_ArtifactChangesCommitted(
        cls, event: ArtifactChangesCommitted
    ) -> ArtifactCommitPushed:
        """
        Gets notified of an ArtifactChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_ArtifactCommitPushed(
        cls, event: ArtifactCommitPushed
    ) -> ArtifactCommitTagged:
        """
        Gets notified of an ArtifactCommitPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        :return: An event notifying the commit in the artifact repository has been tagged.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitTagged
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_ArtifactCommitTagged(
        cls, event: ArtifactCommitTagged
    ) -> ArtifactTagPushed:
        """
        Gets notified of an ArtifactCommitTagged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_commit.events.ArtifactCommitTagged
        :return: An event notifying the tag in the artifact has been pushed.
        :rtype: pythoneda.shared.artifact_commit.events.ArtifactTagPushed
        """
        pass

    @classmethod
    @abc.abstractmethod
    async def listen_ArtifactTagPushed(
        cls, event: ArtifactTagPushed
    ) -> ArtifactChangesCommitted:
        """
        Listens to ArtifactTagPushed event to check if affects any of its dependencies.
        In such case, it creates a commit with the dependency change.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactTagPushed
        :return: An event representing the commit.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        pass
