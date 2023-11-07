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

from .architectural_role import ArchitecturalRole
from .artifact import Artifact
from .artifact_commit_from_artifact_tag_pushed import (
    ArtifactCommitFromArtifactTagPushed,
)
from .artifact_commit_from_tag_pushed import ArtifactCommitFromTagPushed
from .artifact_commit_from_artifact_tag_pushed import (
    ArtifactCommitFromArtifactTagPushed,
)
from .artifact_commit_push import ArtifactCommitPush
from .artifact_commit_tag import ArtifactCommitTag
from .artifact_event_listener import ArtifactEventListener
from .artifact_tag_push import ArtifactTagPush
from .commit_push import CommitPush
from .commit_tag import CommitTag
from .hexagonal_layer import HexagonalLayer
from .local_artifact import LocalArtifact
from .pescio_space import PescioSpace
from .python_package import PythonPackage
from .tag_push import TagPush

# regular flow:
# 0. (commit)
# 1. CommitPush
# 2. CommitTag
# 3. TagPush
# 4. ArtifactCommitFromTagPushed
# 5. ArtifactCommitPush
# 6. ArtifactCommitTag
# 7. ArtifactTagPush
# 8. ArtifactCommitFromArtifactTagPushed
