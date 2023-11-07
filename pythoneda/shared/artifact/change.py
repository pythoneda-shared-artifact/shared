"""
pythoneda/shared/artifact/change.py

This file defines the Change class.

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
import json
from pythoneda import Entity, primary_key_attribute
from typing import Dict
from unidiff import PatchSet


class Change(Entity):
    """
    Represents a change in source code.

    Class name: Change

    Responsibilities:
        - Represent a change unambiguously.

    Collaborators:
        - None
    """

    def __init__(
        self,
        unidiffText: str,
        repositoryUrl: str,
        branch: str,
        repositoryFolder: str = None,
    ):
        """
        Creates a new Change instance.
        :param unidiffText: The files affected and how.
        :type unidiffText: str
        :param repositoryUrl: The url of the repository.
        :type repositoryUrl: str
        :param branch: The branch within the repository.
        :type branch: str
        :param repositoryFolder: The folder of the cloned repository.
        :type repositoryFolder: str
        """
        super().__init__()
        self._unidiff_text = unidiffText
        self._repository_url = repositoryUrl
        self._branch = branch
        self._repository_folder = repositoryFolder

    @property
    @primary_key_attribute
    def unidiff_text(self) -> str:
        """
        Retrieves the unidiff text.
        :return: The files affected and how.
        :rtype: str
        """
        return self._unidiff_text

    @property
    @primary_key_attribute
    def repository_url(self) -> str:
        """
        Retrieves the url of the repository.
        :return: Such url.
        :rtype: str
        """
        return self._repository_url

    @property
    @primary_key_attribute
    def branch(self) -> str:
        """
        Retrieves the branch within the repository.
        :return: Such branch.
        :rtype: str
        """
        return self._branch

    @property
    @primary_key_attribute
    def repository_folder(self) -> str:
        """
        Retrieves the folder of the cloned repository.
        :return: Such folder.
        :rtype: str
        """
        return self._repository_folder

    @property
    def patch_set(self) -> PatchSet:
        """
        Retrieves the unidiff information as a PatchSet.
        :return: Such instance.
        :rtype: unidiff.PatchSet
        """
        result = None
        if self._unidiff_text is not None:
            result = self.__class__._parse_diff(self._unidiff_text)
        return result

    @classmethod
    def from_unidiff_text(
        cls,
        unidiffText: str,
        repositoryUrl: str,
        branch: str,
        repositoryFolder: str = None,
    ):  # -> Change:
        """
        Creates a new Change instance from given parameters.
        :param unidiffText: The unified diff.
        :type unidiffText: str
        :param repositoryUrl: The url of the repository.
        :type repositoryUrl: str
        :param branch: The branch the change applies to, within the repository.
        :type branch: str
        :param repositoryFolder: The folder of the cloned repository.
        :type repositoryFolder: str
        :return: A Change instance.
        :rtype: pythonedaartifactsharedchanges.change.Change
        """
        return cls(unidiffText, repositoryUrl, branch, repositoryFolder)

    @classmethod
    def from_unidiff_file(
        cls,
        unidiffFile: str,
        repositoryUrl: str,
        branch: str,
        repositoryFolder: str = None,
    ):  # -> Change:
        """
        Creates a new Change instance from given parameters.
        :param unidiffFile: The unified diff file.
        :type unidiffFile: str
        :param repositoryUrl: The url of the repository.
        :type repositoryUrl: str
        :param branch: The branch the change applies to, within the repository.
        :type branch: str
        :param repositoryFolder: The folder of the cloned repository.
        :type repositoryFolder: str
        :return: A Change instance.
        :rtype: pythonedaartifactsharedchanges.change.Change
        """
        result = None

        with open(unidiffFile, "r") as file:
            result = cls(file.read(), repositoryUrl, branch, repositoryFolder)

        return result

    @classmethod
    def _parse_diff(cls, unidiffText: str) -> PatchSet:
        """
        Parses given unidiff text.
        :param unidiffText: The text to parse.
        :type unidiffText: str
        :return: A PatchSet instance.
        :rtype: unidiff.PatchSet
        """
        return PatchSet(unidiffText)

    def to_dict(self) -> Dict:
        """
        Converts this instance into a dictionary.
        :return: Such dictionary.
        :rtype: Dict
        """
        return {
            "unidiff_text": self.unidiff_text,
            "repository_url": self.repository_url,
            "branch": self.branch,
            "repository_folder": self.repository_folder,
        }

    @classmethod
    def from_dict(cls, dict: Dict):  # -> Change:
        """
        Creates a new instance with the contents of given dictionary.
        :param dict: The dictionary.
        :type dict: Dict
        :return: A Change instance.
        :rtype: pythoneda.shared.artifact_changes.change.Change
        """
        return cls(
            dict["unidiff_text"],
            dict["repository_url"],
            dict["branch"],
            dict.get("repository_folder", None),
        )

    def to_json(self) -> str:
        """
        Serializes this instance as json.
        :return: The json text.
        :rtype: str
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, jsonText: str):  # -> Change:
        """
        Reconstructs a Change instance from given json text.
        :param jsonText: The json text.
        :type jsonText: str
        :return: The Change instance.
        :rtype: pythoneda.shared.artifact_changes.change.Change
        """
        return cls.from_dict(json.loads(jsonText))
