import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max-limit
    DEBUG = os.environ.get('FLASK_DEBUG', True)

class VisualizationConfig:
    # Graph rendering settings
    DEFAULT_DPI = 150
    MAX_DPI = 300
    DEFAULT_FORMAT = 'png'
    SUPPORTED_FORMATS = ['png', 'pdf', 'svg']
    
    # Style settings
    GRAPH_FONTNAME = 'Arial'
    NODE_FONTSIZE = '10'
    EDGE_FONTSIZE = '8'
    
    # Size settings
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 800
    MAX_WIDTH = 3000
    MAX_HEIGHT = 2000
    
    # Export settings
    EXPORT_QUALITY = 95  # For PNG exports
    PDF_PAGE_SIZE = 'A4'
    SVG_SCALE = 1.5