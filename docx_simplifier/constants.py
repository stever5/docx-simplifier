"""
Constants for docx-simplifier.

This module contains configuration constants used throughout the application.
"""

# File size thresholds (in bytes)
LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB
VERY_LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  # 50MB

# Processing configuration
CHUNK_SIZE = 64 * 1024  # 64KB chunks for streaming
PROGRESS_UPDATE_INTERVAL = 1000  # Update progress every N paragraphs

# GUI configuration
PROGRESS_BAR_LENGTH = 40  # Characters in CLI progress bar
GUI_WINDOW_WIDTH = 750
GUI_WINDOW_HEIGHT = 600

# Performance thresholds
PATTERN_PERFORMANCE_ITERATIONS = 100  # For performance comparison tests
MAX_PROCESSING_TIME = 60.0  # Maximum seconds for test timeout

# File validation
REQUIRED_DOCX_FILES = ['[Content_Types].xml', '_rels/.rels']
DOCUMENT_XML_PATTERN = r'.*\b(endnotes|foot.+?|document)\.xml$'

# Version info
VERSION = "1.0.0"