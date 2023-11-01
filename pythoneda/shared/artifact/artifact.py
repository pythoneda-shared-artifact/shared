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
from .artifact_changes_committed_listener import ArtifactChangesCommittedListener
from .artifact_commit_pushed_listener import ArtifactCommitPushedListener
from .artifact_commit_tagged_listener import ArtifactCommitTaggedListener
from .artifact_tag_pushed_listener import ArtifactTagPushedListener
from .committed_changes_pushed_listener import CommittedChangesPushedListener
from .committed_changes_tagged_listener import CommittedChangesTaggedListener
from .staged_changes_committed_listener import StagedChangesCommittedListener
from .tag_pushed_listener import TagPushedListener
import abc
import os
from pythoneda import EventListener, listen

from pythoneda.shared.artifact_changes.events import (
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


class Artifact(EventListener, abc.ABC):
    """
    Represents Artifacts.

    Class name: Artifact

    Responsibilities:
        - Provide a model for Artifacts.

    Collaborators:
        - None
    """

    def __init__(self, repositoryFolder: str):
        """
        Creates a new Artifact instance.
        """
        super().__init__()
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
        return GitTag(repositoryFolder).current_tag()

    @classmethod
    def find_out_repository_folder(cls, otherRepositoryFolder: str) -> str:
        """
        Retrieves the own repository folder based on a convention, assuming
        given folder holds another PythonEDA project.
        :param otherRepositoryFolder: The other repository folder.
        :type otherRepositoryFolder: str
        :return: The repository folder, or None if not found.
        :rtype: str
        """
        parent = os.path.dirname(otherRepositoryFolder)
        grand_parent = os.path.dirname(parent)
        git_repo = GitRepo.from_folder(otherRepositoryFolder)
        owner, repo = git_repo.repo_owner_and_repo_name()
        candidate = os.path.join(grand_parent, owner, repo)
        if os.path.isdir(os.path.join(candidate, ".git")) and (
            GitRepo(candidate).url == cls.repo_url
        ):
            result = candidate
        return result

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
    @listen(StagedChangesCommitted)
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
        return await StagedChangesCommittedListener().listen(event)

    @classmethod
    @listen(CommittedChangesPushed)
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
        return await CommittedChangesPushedListener().listen(event)

    @classmethod
    @listen(CommittedChangesTagged)
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
        return await CommittedChangesTaggedListener().listen(event)

    @classmethod
    @listen(TagPushed)
    async def listen_TagPushed(cls, event: TagPushed) -> ArtifactChangesCommitted:
        """
        Gets notified of a TagPushed event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.TagPushed
        :return: An event notifying the changes in the artifact have been committed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        return await TagPushedListener().listen(event)

    @classmethod
    @listen(ArtifactChangesCommitted)
    async def listen_ArtifactChangesCommitted(
        cls, event: TagPushed
    ) -> ArtifactCommitPushed:
        """
        Gets notified of an ArtifactChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        :return: An event notifying the commit in the artifact repository has been pushed.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactCommitPushed
        """
        return await ArtifactChangesCommittedListener().listen(event)

    @classmethod
    @listen(ArtifactCommitPushed)
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
        return await ArtifactCommitPushedListener().listen(event)

    @classmethod
    @listen(ArtifactCommitTagged)
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
        return await ArtifactCommitTaggedListener().listen(event)

    @classmethod
    @listen(ArtifactTagPushed)
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
        result = None
        folder = cls.find_out_repository_folder(event.repository_folder)
        if folder is not None:
            result = await ArtifactTagPushedListener().listen(event, folder)
        return result
