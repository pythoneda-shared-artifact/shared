# vim: set fileencoding=utf-8
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
import abc
from .commit import Commit
from .commit_push import CommitPush
from .commit_tag import CommitTag
from pythoneda.shared import Event, EventListener, listen, PrimaryPort
from pythoneda.shared.artifact.events import (
    ChangeStaged,
    CommittedChangesPushed,
    CommittedChangesTagged,
    StagedChangesCommitted,
    TagPushed,
)
from pythoneda.shared.git import GitRepo
from pythoneda.shared.nix.flake import NixFlake, NixFlakeInput
from .repository_folder_helper import RepositoryFolderHelper
from .stage_input_update import StageInputUpdate
from .tag_push import TagPush
from typing import Callable, List


class Artifact(NixFlake, EventListener, abc.ABC):
    """
    Represents Artifacts.

    Class name: Artifact

    Responsibilities:
        - Provide common logic for Artifacts.

    Collaborators:
        - None

    To describe the tagging flow, let's assumeThe logic is as follows:
    -
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
        :type inputs: List[pythoneda.shared.nix.flake.NixFlakeInput]
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

    def url_for(self, version: str) -> str:
        """
        Retrieves the url for given version.
        :param version: The version.
        :type version: str
        :return: The url.
        :rtype: str
        """
        return f"{self.__class__.url}/{version}"

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

    @abc.abstractmethod
    def event_refers_to_me(self, event: Event) -> bool:
        """
        Checks whether given event refers to this artifact.
        :param event: The event to check.
        :type event: pythoneda.shared.Event
        """
        pass

    def extract_input(self, event: Event) -> NixFlakeInput:
        """
        Extracts the affected input from given event.
        :param event: The event to analyze.
        :type event: pythoneda.shared.Event
        :return: The affected input, or None.
        :rtype: pythoneda.shared.nix.flake.NixFlakeInput
        """
        result = None
        for aux in self.inputs:
            if event.matches_input(aux):
                result = aux
                break
        return result

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
        :type event: pythoneda.shared.artifact_changes.events.CommittedChangesPushed
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

    async def commit_after_ChangeStaged(
        self, event: ChangeStaged
    ) -> StagedChangesCommitted:
        """
        Gets notified of a ChangeStaged event.
        If needed, commits the changes and emits a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.ChangeStaged
        :return: An event notifying a change in the artifact has been staged, if the event refers to an input
        of this artifact.
        :rtype: pythoneda.shared.artifact.events.StagedChangesCommitted
        """
        Artifact.logger().debug("5. ChangeStaged -> StagedChangesCommitted")
        result = None
        dep = self.extract_input(event)
        if dep is not None:
            Artifact.logger().debug(f"ChangeStaged for {dep}")
            result = await Commit(self.repository_folder).listen(event)
        return result

    async def push_commit_after_StagedChangesCommitted(
        self, event: StagedChangesCommitted
    ) -> CommittedChangesPushed:
        """
        Gets notified of a StagedChangesCommitted event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.StagedChangesCommitted
        :return: An event notifying the commit has been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesPushed
        """
        result = None
        proceed = self.event_refers_to_me(event)

        if proceed:
            Artifact.logger().debug(
                "1. StagedChangesCommitted -> CommittedChangesPushed"
            )
        else:
            dep = self.extract_input(event)
            if dep is not None:
                Artifact.logger().debug(
                    "11. StagedChangesCommitted -> CommittedChangesPushed"
                )
                proceed = True
        if proceed:
            Artifact.logger().debug(
                f"StagedChangesCommitted for {self.repository_folder}"
            )
            result = await CommitPush(self.repository_folder).listen(event)

        return result

    async def create_tag_after_CommittedChangesPushed(
        self, event: CommittedChangesPushed
    ) -> CommittedChangesTagged:
        """
        Gets notified of a CommittedChangesPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommittedChangesPushed
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.CommittedChangesTagged
        """
        result = None
        proceed = self.event_refers_to_me(event)

        if proceed:
            Artifact.logger().debug(
                "2. CommittedChangesPushed -> CommittedChangesTagged"
            )
        else:
            dep = self.extract_input(event)
            if dep is not None:
                Artifact.logger().debug(
                    "7. CommittedChangesPushed -> CommittedChangesTagged"
                )
                proceed = True
        if proceed:
            Artifact.logger().debug(
                f"CommittedChangesPushed for {self.repository_folder}"
            )
            result = await CommitTag(self.repository_folder).listen(event)
        return result

    async def push_tag_after_CommittedChangesTagged(
        self, event: CommittedChangesTagged
    ) -> TagPushed:
        """
        Gets notified of a CommittedChangesTagged event.
        Pushes the changes and emits a TagPushed event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.CommittedChangesTagged
        :return: An event notifying the changes have been pushed.
        :rtype: pythoneda.shared.artifact.events.TagPushed
        """
        result = None
        proceed = self.event_refers_to_me(event)

        if proceed:
            Artifact.logger().debug("3. CommittedChangesTagged -> TagPushed")
        else:
            dep = self.extract_input(event)
            if dep is not None:
                Artifact.logger().debug("8. CommittedChangesTagged -> TagPushed")
                proceed = True
        if proceed:
            Artifact.logger().debug(
                f"CommittedChangesTagged for {self.repository_folder}"
            )
            result = await TagPush(self.repository_folder).listen(event)
        return result

    async def maybe_update_flake_after_TagPushed(
        self, event: TagPushed
    ) -> ChangeStaged:
        """
        Gets notified of a TagPushed event.
        If needed, stages the change with an updated input and emits a ChangeStaged event.
        :param event: The event.
        :type event: pythoneda.shared.artifact.events.TagPushed
        :return: An event notifying a change in the artifact has been staged, if the event refers to an input
        of this artifact.
        :rtype: pythoneda.shared.artifact.events.ChangeStaged
        """
        result = None
        proceed = self.event_refers_to_me(event)

        if proceed:
            Artifact.logger().debug("4. TagPushed -> ChangeStaged")
        else:
            dep = self.extract_input(event)
            if dep is not None:
                Artifact.logger().debug("9. TagPushed -> ChangeStaged")
                proceed = True

        if proceed:
            result = await StageInputUpdate(self.repository_folder).listen(event)

        return result


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
