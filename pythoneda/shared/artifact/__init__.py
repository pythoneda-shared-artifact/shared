"""
pythoneda/shared/artifact/__init__.py

This file ensures pythoneda.shared.artifact is a namespace.

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
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from .artifact import Artifact
from .architectural_role import ArchitecturalRole
from .artifact_event_listener import ArtifactEventListener
from .commit import Commit
from .commit_push import CommitPush
from .commit_tag import CommitTag
from .hexagonal_layer import HexagonalLayer
from .pescio_space import PescioSpace
from .python_package import PythonPackage
from .repository_folder_helper import RepositoryFolderHelper
from .stage_input_update import StageInputUpdate
from .tag_push import TagPush
