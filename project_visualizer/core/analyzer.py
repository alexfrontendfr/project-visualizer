import ast
from pathlib import Path
from typing import Dict, Set, Optional, List
import logging
from ..core.models import FileNode, AnalysisResult
from ..utils.graph_utils import GraphGenerator

logger = logging.getLogger(__name__)

class ProjectAnalyzer:
    def __init__(self, root_path: str, exclude_folders: Optional[List[str]] = None):
        self.root_path = Path(root_path)
        self.exclude_folders = set(exclude_folders or []) | {
            'node_modules', '__pycache__', '.git', 'venv', 'env',
            'dist', 'build', '.pytest_cache'
        }
        self.files: Dict[str, FileNode] = {}
        
    def analyze(self) -> AnalysisResult:
        try:
            if not self.root_path.exists():
                raise ValueError(f"Directory does not exist: {self.root_path}")
            if not self.root_path.is_dir():
                raise ValueError(f"Path is not a directory: {self.root_path}")

            self.files.clear()
            self._scan_files()
            
            graph_generator = GraphGenerator()
            graph_generator.add_directory_nodes(self._get_directories())
            graph_generator.add_file_nodes(self.files)
            
            return AnalysisResult(
                total_files=len(self.files),
                total_directories=len(self._get_directories()),
                file_types=self._get_file_type_counts(),
                structure=self._get_directory_structure(),
                visualization=graph_generator.generate_base64()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing project: {str(e)}")
            raise

    def _scan_files(self):
        for item in self.root_path.rglob('*'):
            if item.is_file() and not any(part in self.exclude_folders for part in item.parts):
                self._analyze_file(item)

    def _analyze_file(self, file_path: Path):
        try:
            relative_path = str(file_path.relative_to(self.root_path))
            
            if file_path.suffix == '.py':
                self._analyze_python_file(file_path, relative_path)
            else:
                self._analyze_regular_file(file_path, relative_path)
                
        except Exception as e:
            logger.warning(f"Error analyzing file {file_path}: {str(e)}")

    def _analyze_python_file(self, file_path: Path, relative_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.update(name.name for name in node.names)
                    else:
                        module = node.module or ''
                        imports.add(module)
            
            self.files[relative_path] = FileNode(
                path=relative_path,
                file_type='py',
                imports=imports,
                is_test='test' in relative_path.lower(),
                is_entry_point='main.py' in relative_path or 'app.py' in relative_path
            )
            
        except Exception as e:
            logger.warning(f"Error parsing Python file {file_path}: {str(e)}")
            self._analyze_regular_file(file_path, relative_path)

    def _analyze_regular_file(self, file_path: Path, relative_path: str):
        self.files[relative_path] = FileNode(
            path=relative_path,
            file_type=file_path.suffix[1:] if file_path.suffix else 'unknown'
        )

    def _get_directories(self) -> Set[str]:
        directories = set()
        for file_path in self.files.keys():
            parent = str(Path(file_path).parent)
            if parent != '.':
                directories.add(parent)
        return directories

    def _get_file_type_counts(self) -> Dict[str, int]:
        counts = {}
        for file_node in self.files.values():
            counts[file_node.file_type] = counts.get(file_node.file_type, 0) + 1
        return counts

    def _get_directory_structure(self) -> dict:
        structure = {}
        for file_path in sorted(self.files.keys()):
            parts = Path(file_path).parts
            current = structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {'files': [], 'directories': {}}
                current = current[part]['directories']
            current.setdefault('files', []).append(parts[-1])
        return structure