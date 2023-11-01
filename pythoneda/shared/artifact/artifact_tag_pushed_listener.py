"""
pythoneda/shared/artifact/artifact_tag_pushed_listener.py

This file declares the ArtifactTagPushedListener class.

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
from pythoneda.shared.artifact_changes.events import (
    ArtifactChangesCommitted,
    ArtifactTagPushed,
)
from pythoneda.shared.git import (
    GitAdd,
    GitAddFailed,
    GitCommit,
    GitCommitFailed,
    GitRepo,
)
from pythoneda.shared.nix_flake import (
    FlakeUtilsNixFlake,
    License,
    PythonedaSharedPythonedaBannerNixFlake,
)


class ArtifactTagPushedListener(ArtifactEventListener):
    """
    Reacts to ArtifactTagPushed events.

    Class name: ArtifactTagPushedListener

    Responsibilities:
        - Receive ArtifactTagPushed events and react accordingly.

    Collaborators:
        - pythoneda.shared.artifact_changes.events.ArtifactTagPushed
    """

    def __init__(self):
        """
        Creates a new ArtifactTagPushedListener instance.
        """
        super().__init__()

    async def listen(
        self, event: ArtifactTagPushed, repositoryFolder: str
    ) -> ArtifactChangesCommitted:
        """
        Reacts upon given ArtifactTagPushed event to check if affects any of its dependencies.
        In such case, it creates a commit with the dependency change.
        :param event: The event.
        :type event: pythoneda.shared.artifact_changes.events.ArtifactTagPushed
        :param repositoryFolder: The repository folder of the artifact receiving this event.
        :type repositoryFolder: str
        :return: An event representing the commit.
        :rtype: pythoneda.shared.artifact_changes.events.ArtifactChangesCommitted
        """
        result = None
        ArtifactTagPushedListener.logger().info(
            f"Checking if {event.name} is one of my inputs"
        )
        dep = next((item.name == event.name for item in self.inputs), None)
        if dep is None:
            ArtifactTagPushedListener.logger().info(
                f"Checking if {event.name} is one of my inputs"
            )
        else:
            git_repo = GitRepo.from_folder(repositoryFolder)
            org, repo = GitRepo.extract_repo_owner_and_repo_name(git_repo.url)
            ArtifactTagPushedListener.logger().info(
                f"Updating {org}/{repo} since {event.name} updated to version {event.version}"
            )
            # update the affected dependency
            updated_dep = dep.for_version(event.version)
            # generate the flake
            self.generate_flake(repositoryFolder)
            # refresh flake.lock
            self.__class__.update_flake_lock(repositoryFolder, "domain")
            # add the change
            git_add = GitAdd(repositoryFolder)
            git_add.add(os.path.join(repositoryFolder, "domain", "flake.nix"))
            git_add.add(os.path.join(repositoryFolder, "domain", "flake.lock"))
            git_add.add(os.path.join(repositoryFolder, "domain", "pyproject.toml"))
            # commit the change
            commit_hash, commit_diff = GitCommit(repositoryFolder).commit(
                "Updated {dep.name} to {event.version}"
            )
            # generate the ArtifactChangesCommitted event
            result = ArtifactChangesCommitted(
                Change.from_undiff_text(
                    commit_diff,
                    git_repo.url,
                    git_repo.rev,
                    repositoryFolder,
                )
            )
        return result
