# vim: set fileencoding=utf-8
"""
pythoneda/shared/artifact/pescio_space.py

This file declares the PescioSpace class.

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


class PescioSpace(Enum):
    """
    An enumerated type to identify Carlo Pescio's spaces (https://www.youtube.com/watch?v=WPgYju3KnIY)

    Class name: PescioSpace

    Responsibilities:
        - Define the different types of spaces.

    Collaborators:
        - None. But this class is used both by pythoneda.shared.application.bootstrap
        and pythoneda.shared.application.pythoneda.PythonEDA
    """

    DECISION = auto()
    ARTIFACT = auto()
    RUNTIME = auto()
    TENANT = auto()
# vim: syntax=python ts=4 sw=4 sts=4 tw=79 sr et
# Local Variables:
# mode: python
# python-indent-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# fill-column: 79
# End:
