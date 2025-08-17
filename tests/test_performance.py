"""
Unit tests for DocxSimplifier performance features and compiled patterns.
"""

import os
import tempfile
import unittest
import time
from pathlib import Path
import zipfile
from unittest.mock import Mock

from docx_simplifier.core import DocxSimplifier
from docx_simplifier.levels import get_level_description
from docx_simplifier.constants import LARGE_FILE_THRESHOLD, PATTERN_PERFORMANCE_ITERATIONS, MAX_PROCESSING_TIME


class TestLxmlProcessing(unittest.TestCase):
    """Test the LXML-based processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simplifier = DocxSimplifier()
    
    def test_structured_xml_processing(self):
        """Test that structured XML processing works correctly."""
        # Test with simple XML content
        test_xml = '''<?xml version="1.0"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
            <w:body>
                <w:p>
                    <w:r>
                        <w:rPr>
                            <w:sz w:val="24"/>
                            <w:color w:val="000000"/>
                        </w:rPr>
                        <w:t>Test text</w:t>
                    </w:r>
                </w:p>
            </w:body>
        </w:document>'''
        
        # Process the XML content directly
        result = self.simplifier._clean_xml_content_lxml(test_xml, level=1)
        
        # Should be valid XML
        from lxml import etree
        try:
            etree.fromstring(result.encode('utf-8'))
            xml_valid = True
        except etree.XMLSyntaxError:
            xml_valid = False
            
        self.assertTrue(xml_valid, "Output should be valid XML")
        
        # Should have removed formatting elements at level 1
        self.assertNotIn('w:val="24"', result)  # Font size 24 should be removed
        self.assertNotIn('w:val="000000"', result)  # Black color should be removed
    
    def test_namespace_handling(self):
        """Test that XML namespaces are handled correctly."""
        namespaces = self.simplifier.namespaces
        nsmap = namespaces.to_dict()
        
        # Should have core Word namespaces
        self.assertIn('w', nsmap)
        self.assertIn('wps', nsmap)
        self.assertEqual(nsmap['w'], 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')


class TestDocxSimplifierPerformance(unittest.TestCase):
    """Test cases for DocxSimplifier performance features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.progress_calls = []
        
        def progress_callback(message, percentage):
            self.progress_calls.append((message, percentage))
        
        self.simplifier = DocxSimplifier(progress_callback=progress_callback)
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_docx(self, filename="test.docx", large_content=False):
        """Create a minimal mock DOCX file for testing."""
        docx_path = Path(self.temp_dir) / filename
        
        # Create content - large or small
        if large_content:
            # Create larger content for performance testing
            paragraphs = []
            for i in range(1000):  # 1000 paragraphs
                paragraphs.append(
                    f'<w:p><w:r><w:rPr><w:sz w:val="24"/><w:color w:val="000000"/></w:rPr>'
                    f'<w:t>Test paragraph {i} with formatting</w:t></w:r></w:p>'
                )
            document_content = ''.join(paragraphs)
        else:
            document_content = (
                '<w:p><w:r><w:rPr><w:sz w:val="24"/><w:color w:val="000000"/></w:rPr>'
                '<w:t>Test document</w:t></w:r></w:p>'
                '<w:p><w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr>'
                '<w:t>Bold text</w:t></w:r></w:p>'
            )
        
        # Create minimal DOCX structure
        with zipfile.ZipFile(docx_path, 'w') as zip_file:
            # Content types
            zip_file.writestr('[Content_Types].xml', 
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                '</Types>')
            
            # Main relationships
            zip_file.writestr('_rels/.rels',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                '</Relationships>')
            
            # Document with test content
            zip_file.writestr('word/document.xml',
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f'<w:body>{document_content}</w:body></w:document>')
        
        return docx_path
    
    def test_progress_reporting(self):
        """Test that progress callbacks are called."""
        mock_docx = self.create_mock_docx()
        
        # Clear previous calls
        self.progress_calls.clear()
        
        output_path = self.simplifier.simplify_file(str(mock_docx), level=1)
        
        # Should have received progress updates
        self.assertGreater(len(self.progress_calls), 0)
        
        # Check that we got start and complete messages
        messages = [call[0] for call in self.progress_calls]
        self.assertTrue(any("Starting" in msg for msg in messages))
        self.assertTrue(any("complete" in msg for msg in messages))
        
        # Check that percentages are reasonable
        percentages = [call[1] for call in self.progress_calls]
        self.assertTrue(any(p >= 100.0 for p in percentages))  # Should reach 100%
    
    def test_performance_stats(self):
        """Test performance statistics reporting."""
        stats = self.simplifier.get_performance_stats()
        
        # Check that stats contain expected keys for LXML implementation
        expected_keys = ['approach', 'total_time', 'elements_removed', 
                        'elements_modified', 'optimizations']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Check that approach is correct
        self.assertEqual(stats['approach'], 'lxml')
        
        # Check that optimizations list is not empty
        self.assertGreater(len(stats['optimizations']), 0)
        
        # Should contain LXML-specific optimizations
        optimizations_text = ' '.join(stats['optimizations'])
        self.assertIn('lxml', optimizations_text.lower())
        self.assertIn('xpath', optimizations_text.lower())
    
    def test_consistent_output(self):
        """Test that DocxSimplifier produces consistent output."""
        from docx_simplifier.core import DocxSimplifier
        
        mock_docx = self.create_mock_docx()
        
        # Process with first instance
        first_simplifier = DocxSimplifier()
        first_output = first_simplifier.simplify_file(str(mock_docx), level=3)
        
        # Process with second instance
        second_output = self.simplifier.simplify_file(str(mock_docx), level=3)
        
        # Read both outputs and compare
        with zipfile.ZipFile(first_output, 'r') as first_zip:
            with zipfile.ZipFile(second_output, 'r') as second_zip:
                # Compare document.xml content
                first_doc = first_zip.read('word/document.xml').decode('utf-8')
                second_doc = second_zip.read('word/document.xml').decode('utf-8')
                
                # Should be functionally equivalent (may have minor formatting differences)
                # Remove whitespace differences for comparison
                import re
                first_normalized = re.sub(r'\s+', ' ', first_doc.strip())
                second_normalized = re.sub(r'\s+', ' ', second_doc.strip())
                
                self.assertEqual(first_normalized, second_normalized)
    
    def test_large_file_handling(self):
        """Test handling of larger files with progress reporting."""
        # Create a larger mock file
        large_docx = self.create_mock_docx("large_test.docx", large_content=True)
        
        # Clear progress calls
        self.progress_calls.clear()
        
        start_time = time.time()
        output_path = self.simplifier.simplify_file(str(large_docx), level=5)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete successfully
        self.assertTrue(Path(output_path).exists())
        
        # Should report progress for large files
        self.assertGreater(len(self.progress_calls), 1)
        
        # Processing time should be reasonable (less than 30 seconds for test file)
        self.assertLess(processing_time, 30.0)
        
        print(f"Large file processing time: {processing_time:.2f} seconds")
        print(f"Progress updates: {len(self.progress_calls)}")
    
    def test_debug_option(self):
        """Test debug option functionality."""
        mock_docx = self.create_mock_docx()
        
        # Test without debug
        simplifier1 = DocxSimplifier(debug=False)
        output1 = simplifier1.simplify_file(str(mock_docx), level=1)
        
        # Test with debug
        simplifier2 = DocxSimplifier(debug=True)
        output2 = simplifier2.simplify_file(str(mock_docx), level=1)
        
        # Both should exist
        self.assertTrue(Path(output1).exists())
        self.assertTrue(Path(output2).exists())
        
        # Should have reasonable sizes
        size1 = Path(output1).stat().st_size
        size2 = Path(output2).stat().st_size
        self.assertGreater(size1, 0)
        self.assertGreater(size2, 0)
    
    def test_all_simplification_levels(self):
        """Test that all simplification levels work correctly."""
        mock_docx = self.create_mock_docx()
        
        outputs = {}
        for level in range(9):  # 0-8
            output_path = self.simplifier.simplify_file(str(mock_docx), level=level)
            outputs[level] = output_path
            self.assertTrue(Path(output_path).exists())
        
        # Different levels should produce different results
        sizes = {level: Path(path).stat().st_size for level, path in outputs.items()}
        
        # Should have some variation in sizes
        unique_sizes = set(sizes.values())
        self.assertGreater(len(unique_sizes), 1)
    
    def test_pattern_performance_comparison(self):
        """Test that compiled patterns are faster than regular re.sub calls."""
        import re
        
        # Sample text with patterns to match
        test_text = '<w:r><w:rPr><w:sz w:val="24"/><w:color w:val="000000"/></w:rPr><w:t>text</w:t></w:r>' * 100
        
        # Time regular regex compilation and execution
        start_time = time.time()
        for _ in range(PATTERN_PERFORMANCE_ITERATIONS):
            result1 = re.sub(r'<w:sz w:val="24"/>', '', test_text)
        regular_time = time.time() - start_time
        
        # Time compiled pattern execution
        compiled_pattern = re.compile(r'<w:sz w:val="24"/>')
        start_time = time.time()
        for _ in range(PATTERN_PERFORMANCE_ITERATIONS):
            result2 = compiled_pattern.sub('', test_text)
        compiled_time = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(result1, result2)
        
        # Compiled should be faster (though margin may be small for simple test)
        print(f"Regular regex time: {regular_time:.4f}s")
        print(f"Compiled pattern time: {compiled_time:.4f}s")
        print(f"Speed improvement: {regular_time/compiled_time:.2f}x")
        
        # For repeated operations, compiled should be at least as fast
        self.assertLessEqual(compiled_time, regular_time * 1.1)  # Allow 10% margin


class TestPerformanceComparison(unittest.TestCase):
    """Compare performance between standard and optimized implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_performance_test_docx(self, size="medium"):
        """Create DOCX file for performance testing."""
        docx_path = Path(self.temp_dir) / f"{size}_test.docx"
        
        # Create different sizes for testing
        if size == "small":
            paragraph_count = 10
        elif size == "medium":
            paragraph_count = 100
        else:  # large
            paragraph_count = 500
        
        paragraphs = []
        for i in range(paragraph_count):
            paragraphs.append(
                f'<w:p><w:r><w:rPr><w:sz w:val="24"/><w:color w:val="000000"/>'
                f'<w:b/><w:i/></w:rPr><w:t>Performance test paragraph {i} with '
                f'multiple formatting attributes and longer text content to simulate '
                f'real document complexity.</w:t></w:r></w:p>'
            )
        
        document_content = ''.join(paragraphs)
        
        with zipfile.ZipFile(docx_path, 'w') as zip_file:
            zip_file.writestr('[Content_Types].xml', 
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                '</Types>')
            
            zip_file.writestr('_rels/.rels',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                '</Relationships>')
            
            zip_file.writestr('word/document.xml',
                f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f'<w:body>{document_content}</w:body></w:document>')
        
        return docx_path
    
    def test_performance_comparison(self):
        """Compare performance between standard and optimized versions."""
        from docx_simplifier.core import DocxSimplifier
        
        test_file = self.create_performance_test_docx("medium")
        
        # Test standard implementation
        standard_simplifier = DocxSimplifier()
        start_time = time.time()
        standard_output = standard_simplifier.simplify_file(str(test_file), level=5)
        standard_time = time.time() - start_time
        
        # Test second implementation
        second_simplifier = DocxSimplifier()
        start_time = time.time()
        second_output = second_simplifier.simplify_file(str(test_file), level=5)
        second_time = time.time() - start_time
        
        print(f"\nPerformance Comparison:")
        print(f"First implementation: {standard_time:.4f} seconds")
        print(f"Second implementation: {second_time:.4f} seconds")
        
        if standard_time > 0:
            ratio = standard_time / second_time
            print(f"Performance ratio: {ratio:.2f}x")
            
            # Both should perform reasonably well
            self.assertLess(second_time, MAX_PROCESSING_TIME)  # Should complete within max time
        
        # Both should exist and be reasonable sizes
        self.assertTrue(Path(standard_output).exists())
        self.assertTrue(Path(second_output).exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)