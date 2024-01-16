# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/python_package.py

This file declares the PythonPackage class.

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
from .architectural_role import ArchitecturalRole
from .hexagonal_layer import HexagonalLayer
from .pescio_space import PescioSpace
import abc
from typing import Callable, List


class PythonPackage(Artifact, abc.ABC):
    """
    Represents a Python package.

    Class name: PythonPackage

    Responsibilities:
        - Model a Python package and its metadata.

    Collaborators:
        - None
    """

    def __init__(
        self,
        name: str,
        version: str,
        url: Callable[[str], str],
        inputs: List,
        templateSubfolder: str,
        description: str,
        homepage: str,
        licenseId: str,
        maintainers: List,
        copyrightYear: int,
        copyrightHolder: str,
        pescioSpace: PescioSpace,
        architecturalRole: ArchitecturalRole,
        hexagonalLayer: HexagonalLayer,
    ):
        """
        Creates a new PythonPackage instance.
        """
        super().__init__(
            name,
            version,
            url,
            inputs,
            templateSubfolder,
            description,
            homepage,
            licenseId,
            maintainers,
            copyrightYear,
            copyrightHolder,
        )
        self._pescio_space = pescioSpace
        self._architectural_role = architecturalRole
        self._hexagonal_layer = hexagonalLayer

    @property
    def pescio_space(self) -> PescioSpace:
        """
        Retrieves the Pescio space of this package.
        :return: Such information.
        :rtype: pythoneda.shared.artifact.PescioSpace
        """
        return self._pescio_space

    @property
    def architectural_role(self) -> ArchitecturalRole:
        """
        Retrieves the architectural role of this package.
        :return: Such information.
        :rtype: pythoneda.shared.artifact.ArchitecturalRole
        """
        return self._architectural_role

    @property
    def hexagonal_layer(self) -> HexagonalLayer:
        """
        Retrieves the hexagonal layer of this package.
        :return: Such information.
        :rtype: pythoneda.shared.artifact.HexagonalLayer
        """
        return self._hexagonal_layer
