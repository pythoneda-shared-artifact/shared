# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/artifact_repository.py

This file declares the ArtifactRepository class.

Copyright (C) 2024-today rydnr's pythoneda-shared-artifact/shared

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
from pythoneda.shared import Repo
from typing import List


class ArtifactRepository(Repo):
    """
    Repository of artifacts.

    Class name: ArtifactRepository

    Responsibilities:
        - Manage the persistence of Artifact instances.

    Collaborators:
        - pythoneda.shared.Repo
    """

    def __init__(self):
        """
        Creates a new ArtifactRepository instance.
        """
        super().__init__(AbstractArtifact)

    def find_by_attribute(
        self, attributeName: str, attributeValue: str
    ) -> List[AbstractArtifact]:
        """
        Retrieves the artifacts matching given attribute criteria.
        :param attributeName: The name of the attribute.
        :type attributeName: str
        :param attributeValue: The name of the attribute.
        :type attributeValue: str
        :return: The instances of the EntityClass matching given criteria, or an empty list if none found.
        :rtype: List[pythoneda.shared.artifact.AbstractArtifact]
        """
        pass


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
