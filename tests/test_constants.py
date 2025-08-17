"""
Unit tests for constants module.
"""

import unittest
from docx_simplifier.constants import (
    LARGE_FILE_THRESHOLD,
    VERY_LARGE_FILE_THRESHOLD,
    CHUNK_SIZE,
    PROGRESS_UPDATE_INTERVAL,
    PROGRESS_BAR_LENGTH,
    GUI_WINDOW_WIDTH,
    GUI_WINDOW_HEIGHT,
    PATTERN_PERFORMANCE_ITERATIONS,
    MAX_PROCESSING_TIME,
    REQUIRED_DOCX_FILES,
    DOCUMENT_XML_PATTERN,
    VERSION
)


class TestConstants(unittest.TestCase):
    """Test constants values and types."""
    
    def test_file_size_thresholds(self):
        """Test file size threshold constants."""
        self.assertIsInstance(LARGE_FILE_THRESHOLD, int)
        self.assertIsInstance(VERY_LARGE_FILE_THRESHOLD, int)
        self.assertGreater(VERY_LARGE_FILE_THRESHOLD, LARGE_FILE_THRESHOLD)
        self.assertEqual(LARGE_FILE_THRESHOLD, 10 * 1024 * 1024)  # 10MB
        self.assertEqual(VERY_LARGE_FILE_THRESHOLD, 50 * 1024 * 1024)  # 50MB
    
    def test_processing_configuration(self):
        """Test processing configuration constants."""
        self.assertIsInstance(CHUNK_SIZE, int)
        self.assertIsInstance(PROGRESS_UPDATE_INTERVAL, int)
        self.assertGreater(CHUNK_SIZE, 0)
        self.assertGreater(PROGRESS_UPDATE_INTERVAL, 0)
        self.assertEqual(CHUNK_SIZE, 64 * 1024)  # 64KB
        self.assertEqual(PROGRESS_UPDATE_INTERVAL, 1000)
    
    def test_gui_configuration(self):
        """Test GUI configuration constants."""
        self.assertIsInstance(PROGRESS_BAR_LENGTH, int)
        self.assertIsInstance(GUI_WINDOW_WIDTH, int)
        self.assertIsInstance(GUI_WINDOW_HEIGHT, int)
        self.assertGreater(PROGRESS_BAR_LENGTH, 0)
        self.assertGreater(GUI_WINDOW_WIDTH, 0)
        self.assertGreater(GUI_WINDOW_HEIGHT, 0)
    
    def test_performance_thresholds(self):
        """Test performance threshold constants."""
        self.assertIsInstance(PATTERN_PERFORMANCE_ITERATIONS, int)
        self.assertIsInstance(MAX_PROCESSING_TIME, float)
        self.assertGreater(PATTERN_PERFORMANCE_ITERATIONS, 0)
        self.assertGreater(MAX_PROCESSING_TIME, 0)
    
    def test_file_validation_constants(self):
        """Test file validation constants."""
        self.assertIsInstance(REQUIRED_DOCX_FILES, list)
        self.assertIsInstance(DOCUMENT_XML_PATTERN, str)
        self.assertIn('[Content_Types].xml', REQUIRED_DOCX_FILES)
        self.assertIn('_rels/.rels', REQUIRED_DOCX_FILES)
        self.assertTrue(len(DOCUMENT_XML_PATTERN) > 0)
    
    def test_version_constant(self):
        """Test version constant."""
        self.assertIsInstance(VERSION, str)
        self.assertTrue(len(VERSION) > 0)
        # Version should be in semantic versioning format
        parts = VERSION.split('.')
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == '__main__':
    unittest.main()