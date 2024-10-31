from flask import Blueprint, render_template, request, jsonify, send_file
from ..core.analyzer import ProjectAnalyzer
import logging
from io import BytesIO
import base64
from PIL import Image
import os
from pathlib import Path

logger = logging.getLogger(__name__)
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/analyze', methods=['POST'])
def analyze_project():
    if 'path' not in request.json:
        return jsonify({'error': 'No path provided'}), 400
    
    project_path = request.json['path']
    
    try:
        analyzer = ProjectAnalyzer(project_path)
        results = analyzer.analyze()
        
        return jsonify({
            'visualization': results.visualization,
            'stats': {
                'total_files': results.total_files,
                'total_directories': results.total_directories,
                'file_types': results.file_types
            },
            'structure': results.structure
        })
    except Exception as e:
        logger.error(f"Error analyzing project: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/export', methods=['POST'])
def export_visualization():
    try:
        if 'visualization' not in request.json or 'format' not in request.json:
            return jsonify({'error': 'Missing required data'}), 400

        # Decode base64 image
        img_data = base64.b64decode(request.json['visualization'])
        img_format = request.json['format'].lower()
        
        # Create BytesIO object
        img_io = BytesIO(img_data)
        
        # Create a unique filename
        filename = f'project_structure.{img_format}'
        
        if img_format == 'pdf':
            # Convert PNG to PDF
            img = Image.open(img_io)
            pdf_io = BytesIO()
            img.save(pdf_io, 'PDF', resolution=100.0)
            pdf_io.seek(0)
            return send_file(
                pdf_io,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            # For PNG and other formats
            img_io.seek(0)
            return send_file(
                img_io,
                as_attachment=True,
                download_name=filename,
                mimetype=f'image/{img_format}'
            )
            
    except Exception as e:
        logger.error(f"Error exporting visualization: {str(e)}")
        return jsonify({'error': 'Failed to export visualization'}), 500