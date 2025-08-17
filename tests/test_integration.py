"""
Integration tests to verify the complete system works together.
"""

import unittest
import tempfile
import os
from pathlib import Path

from docx_simplifier import DocxSimplifier, LEVEL_DESCRIPTIONS
from docx_simplifier.utils import format_file_size
from docx_simplifier.constants import LARGE_FILE_THRESHOLD, VERSION


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_version_consistency(self):
        """Test that version is consistent across modules."""
        from docx_simplifier import __version__
        self.assertEqual(__version__, VERSION)
        self.assertTrue(len(VERSION) > 0)
    
    def test_constants_usage(self):
        """Test that constants are properly used throughout the system."""
        # Test that large file threshold is properly configured
        self.assertEqual(LARGE_FILE_THRESHOLD, 10 * 1024 * 1024)
        
        # Test that all levels have descriptions
        for level in range(9):
            self.assertIn(level, LEVEL_DESCRIPTIONS)
            self.assertGreater(len(LEVEL_DESCRIPTIONS[level]), 10)
    
    def test_utility_functions_integration(self):
        """Test that utility functions work correctly."""
        # Test file size formatting with realistic values
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(LARGE_FILE_THRESHOLD), "10.0 MB")
        self.assertEqual(format_file_size(0), "0.0 B")
        self.assertEqual(format_file_size(-100), "0 B")
    
    def test_simplifier_initialization(self):
        """Test that DocxSimplifier initializes correctly with all components."""
        # Test basic initialization
        simplifier = DocxSimplifier()
        self.assertIsNotNone(simplifier)
        
        # Test with progress callback
        progress_calls = []
        def progress_callback(message, percentage):
            progress_calls.append((message, percentage))
        
        simplifier_with_progress = DocxSimplifier(
            debug=True,
            progress_callback=progress_callback
        )
        self.assertIsNotNone(simplifier_with_progress)
        self.assertTrue(simplifier_with_progress.debug)
        self.assertIsNotNone(simplifier_with_progress.progress_callback)
    
    def test_performance_stats_integration(self):
        """Test that performance statistics work correctly."""
        simplifier = DocxSimplifier()
        stats = simplifier.get_performance_stats()
        
        # Verify all expected keys are present
        expected_keys = ['compiled_patterns', 'chunk_size', 'large_file_threshold', 
                        'optimizations', 'performance_gains']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Verify reasonable values
        self.assertGreater(stats['compiled_patterns'], 30)  # Should have many patterns
        self.assertEqual(stats['chunk_size'], "64KB")
        self.assertEqual(stats['large_file_threshold'], "10MB")
        self.assertGreater(len(stats['optimizations']), 5)
        self.assertIsInstance(stats['performance_gains'], dict)
    
    def test_error_handling_integration(self):
        """Test that error handling works across the system."""
        simplifier = DocxSimplifier()
        
        # Test invalid level
        with self.assertRaises(ValueError) as context:
            simplifier.simplify_file("nonexistent.docx", level=10)
        self.assertIn("Level must be 0-8", str(context.exception))
        
        # Test nonexistent file
        with self.assertRaises(FileNotFoundError):
            simplifier.simplify_file("nonexistent.docx", level=1)
        
        # Test invalid file (not a real test without a valid DOCX structure)
        invalid_file = Path(self.temp_dir) / "invalid.docx"
        invalid_file.write_text("not a docx file")
        
        with self.assertRaises(ValueError) as context:
            simplifier.simplify_file(str(invalid_file), level=1)
        self.assertIn("not a valid ZIP/DOCX archive", str(context.exception))
    
    def test_module_imports(self):
        """Test that all modules can be imported without issues."""
        # Test main imports
        from docx_simplifier import DocxSimplifier, LEVEL_DESCRIPTIONS
        from docx_simplifier.core import DocxSimplifier as CoreSimplifier
        from docx_simplifier.utils import format_file_size
        from docx_simplifier.constants import VERSION, LARGE_FILE_THRESHOLD
        from docx_simplifier.levels import get_level_description, get_all_descriptions
        
        # Verify they're all accessible
        self.assertTrue(callable(format_file_size))
        self.assertTrue(callable(get_level_description))
        self.assertTrue(callable(get_all_descriptions))
        self.assertEqual(DocxSimplifier, CoreSimplifier)
    
    def test_lxml_integration(self):
        """Test that LXML-based processing is properly integrated."""
        from docx_simplifier.core import DocxSimplifier
        from docx_simplifier.core import DocxNamespaces
        
        simplifier = DocxSimplifier()
        namespaces = DocxNamespaces()
        
        # Test that namespaces are properly configured
        nsmap = namespaces.to_dict()
        self.assertIn('w', nsmap)
        self.assertIn('wps', nsmap)
        
        # Test that simplifier has LXML components
        self.assertIsNotNone(simplifier.namespaces)
        self.assertIsNotNone(simplifier.nsmap)
        
        # Test that performance stats work with LXML
        stats = simplifier.get_performance_stats()
        self.assertEqual(stats['approach'], 'lxml')
        self.assertIn('lxml', ' '.join(stats['optimizations']).lower())


if __name__ == '__main__':
    unittest.main()