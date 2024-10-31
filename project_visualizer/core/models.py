from dataclasses import dataclass, field
from typing import Set, Optional
from pathlib import Path

@dataclass
class FileNode:
    """Represents a file in the project structure."""
    path: str
    file_type: str
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    is_entry_point: bool = False
    is_test: bool = False
    size: Optional[int] = None

    @property
    def filename(self) -> str:
        return Path(self.path).name

    @property
    def directory(self) -> str:
        return str(Path(self.path).parent)

@dataclass
class AnalysisResult:
    """Contains the results of project analysis."""
    total_files: int
    total_directories: int
    file_types: dict
    structure: dict
    visualization: str  # Base64 encoded graph image