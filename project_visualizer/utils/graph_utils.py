import graphviz
import base64
from typing import Dict, Set
from ..core.models import FileNode
import logging

logger = logging.getLogger(__name__)

class GraphGenerator:
    """Enhanced graph generator with modern styling and better organization."""
    
    # File type icons and colors mapping
    FILE_STYLES = {
        'py': ('🐍', '#3870A4', '#EBF4FA'),   # Python - Blue theme
        'js': ('📜', '#F7DF1E', '#FFFDF1'),   # JavaScript - Yellow theme
        'html': ('🌐', '#E44D26', '#FDF2F1'),  # HTML - Orange theme
        'css': ('🎨', '#264DE4', '#F1F2FD'),   # CSS - Blue theme
        'md': ('📝', '#083fa1', '#F1F4FC'),    # Markdown - Blue theme
        'json': ('📋', '#000000', '#F8F8F8'),  # JSON - Neutral theme
        'txt': ('📄', '#4A4A4A', '#F8F8F8'),   # Text - Gray theme
        'yml': ('⚙️', '#4A4A4A', '#F8F8F8'),   # YAML - Gray theme
        'gitignore': ('🔒', '#4A4A4A', '#F8F8F8'),  # Git - Gray theme
        'unknown': ('📄', '#4A4A4A', '#F8F8F8')  # Default
    }
    
    def __init__(self, dpi=200):
        self.dot = graphviz.Digraph(comment='Project Structure')
        self.dot.attr(
            rankdir='LR',
            splines='polyline',  # Use straight lines with bends
            nodesep='0.5',
            ranksep='1.2',
            fontname='Arial',
            dpi=str(dpi),
            bgcolor='transparent'
        )
        
        # Global node settings
        self.dot.attr('node',
            shape='box',
            style='rounded,filled',
            fontname='Arial',
            margin='0.3,0.1',
            height='0.5'
        )
        
        # Global edge settings
        self.dot.attr('edge',
            color='#666666',
            penwidth='1.2',
            arrowsize='0.8'
        )

    def add_directory_nodes(self, directories: Set[str]):
        for directory in sorted(directories):
            parts = directory.split('/')
            depth = len(parts)
            indent = '    ' * (depth - 1) if depth > 1 else ''
            display_name = parts[-1]
            
            label = f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2" CELLPADDING="4">
                         <TR>
                           <TD WIDTH="24" FIXEDSIZE="TRUE">📁</TD>
                           <TD ALIGN="LEFT">{indent}{display_name}</TD>
                         </TR>
                       </TABLE>>"""
            
            self.dot.node(
                f'dir_{directory}',
                label=label,
                shape='box',
                style='filled,rounded',
                fillcolor='#F0F7FF',
                color='#2563eb',
                penwidth='1.5',
                fontcolor='#1E40AF'
            )

    def add_file_nodes(self, files: Dict[str, FileNode]):
        for file_path, file_node in sorted(files.items()):
            file_type = self._get_file_type(file_node)
            icon, border_color, bg_color = self._get_style(file_node)
            
            # Create gradient effect
            gradient_color = self._adjust_color(bg_color, -10)
            
            label = f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="2" CELLPADDING="4">
                         <TR>
                           <TD WIDTH="24" FIXEDSIZE="TRUE">{icon}</TD>
                           <TD ALIGN="LEFT" BALIGN="LEFT">{file_node.filename}</TD>
                         </TR>
                       </TABLE>>"""
            
            # Add node with enhanced styling
            self.dot.node(
                file_path,
                label=label,
                shape='box',
                style=f'filled,rounded',
                fillcolor=f'{bg_color}:{gradient_color}',
                gradientangle='315',
                color=border_color,
                penwidth='1.2'
            )
            
            # Add edge with improved styling
            if file_node.directory != '.':
                self.dot.edge(
                    f'dir_{file_node.directory}',
                    file_path,
                    color='#6B7280:black',
                    penwidth='1.0',
                    arrowhead='vee'
                )

    def _get_file_type(self, file_node: FileNode) -> str:
        if file_node.path.endswith('.gitignore'):
            return 'gitignore'
        return file_node.file_type

    def _get_style(self, file_node: FileNode) -> tuple:
        file_type = self._get_file_type(file_node)
        
        if file_node.is_entry_point:
            return '🚀', '#059669', '#ECFDF5'  # Green theme for entry points
        elif file_node.is_test:
            return '🧪', '#DC2626', '#FEF2F2'  # Red theme for tests
            
        return self.FILE_STYLES.get(file_type, self.FILE_STYLES['unknown'])

    def _adjust_color(self, hex_color: str, adjustment: int) -> str:
        """Adjust color brightness."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        adjusted = tuple(max(0, min(255, c + adjustment)) for c in rgb)
        
        return f'#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}'

    def generate_base64(self, format='png') -> str:
        try:
            self.dot.attr(size='12,8!')
            graph_data = self.dot.pipe(format=format)
            return base64.b64encode(graph_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating graph: {str(e)}")
            raise