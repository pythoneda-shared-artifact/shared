# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/hexagonal_layer.py

This file declares the HexagonalLayer class.

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
from enum import Enum, auto
from typing import List


class HexagonalLayer(Enum):
    """
    An enumerated type to identify layers in hexagonal architectures.

    Class name: HexagonalLayer

    Responsibilities:
        - Define the different types of layers.

    Collaborators:
        - None. But this class is used both by pythoneda.shared.application.bootstrap
        and pythoneda.shared.application.pythoneda.PythonEDA
    """

    DOMAIN = auto()
    INFRASTRUCTURE = auto()
    APPLICATION = auto()

    def all_but(self) -> List:
        """
        Returns all layers but this one.
        :return: All layers but this one.
        :rtype: List
        """
        return [l for l in HexagonalLayer if l != self]

    def __str__(self) -> str:
        """
        Returns the string representation of the layer.
        :return: The string representation of the layer.
        :rtype: str
        """
        return self.name


# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
