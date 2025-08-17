"""
Unit tests for the core DocxSimplifier functionality.
"""

import os
import tempfile
import unittest
from pathlib import Path
import zipfile

from docx_simplifier.core import DocxSimplifier
from docx_simplifier.levels import get_level_description


class TestDocxSimplifier(unittest.TestCase):
    """Test cases for DocxSimplifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.simplifier = DocxSimplifier()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_docx(self, filename="test.docx"):
        """Create a minimal mock DOCX file for testing."""
        docx_path = Path(self.temp_dir) / filename
        
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
            
            # Document with some test content
            zip_file.writestr('word/document.xml',
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body>'
                '<w:p>'
                '<w:r><w:rPr><w:sz w:val="24"/><w:color w:val="000000"/></w:rPr><w:t>Test document</w:t></w:r>'
                '</w:p>'
                '<w:p>'
                '<w:r><w:rPr><w:b/><w:sz w:val="28"/></w:rPr><w:t>Bold text</w:t></w:r>'
                '</w:p>'
                '</w:body>'
                '</w:document>')
        
        return docx_path
    
    def test_level_validation(self):
        """Test that invalid levels raise ValueError."""
        mock_docx = self.create_mock_docx()
        
        with self.assertRaises(ValueError):
            self.simplifier.simplify_file(str(mock_docx), level=-1)
        
        with self.assertRaises(ValueError):
            self.simplifier.simplify_file(str(mock_docx), level=9)
    
    def test_file_not_found(self):
        """Test that missing files raise FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            self.simplifier.simplify_file("nonexistent.docx")
    
    def test_output_filename_generation(self):
        """Test automatic output filename generation."""
        mock_docx = self.create_mock_docx()
        
        output_path = self.simplifier.simplify_file(str(mock_docx), level=3)
        expected_name = "test_simplified_level3.docx"
        
        self.assertTrue(output_path.endswith(expected_name))
        self.assertTrue(Path(output_path).exists())
    
    def test_custom_output_path(self):
        """Test using custom output path."""
        mock_docx = self.create_mock_docx()
        custom_output = Path(self.temp_dir) / "custom_output.docx"
        
        output_path = self.simplifier.simplify_file(
            str(mock_docx), 
            str(custom_output), 
            level=1
        )
        
        self.assertEqual(output_path, str(custom_output))
        self.assertTrue(custom_output.exists())
    
    def test_simplification_levels(self):
        """Test that different levels produce different results."""
        mock_docx = self.create_mock_docx()
        
        # Test multiple levels
        outputs = {}
        for level in [0, 1, 5, 8]:
            output_path = self.simplifier.simplify_file(str(mock_docx), level=level)
            outputs[level] = output_path
            self.assertTrue(Path(output_path).exists())
        
        # Verify different levels produce different file sizes
        sizes = {}
        for level, path in outputs.items():
            sizes[level] = Path(path).stat().st_size
        
        # Higher levels should generally produce smaller files
        # (though this isn't guaranteed for all content)
        self.assertGreater(len(set(sizes.values())), 1)  # At least some variation
    
    def test_should_clean_entry(self):
        """Test file entry cleaning logic."""
        test_cases = [
            ("word/document.xml", True),
            ("word/endnotes.xml", True), 
            ("word/footer1.xml", True),
            ("word/footer.xml", True),
            ("word/styles.xml", False),
            ("[Content_Types].xml", False),
            ("_rels/.rels", False)
        ]
        
        for filename, should_clean in test_cases:
            with self.subTest(filename=filename):
                result = self.simplifier._should_clean_entry(filename)
                self.assertEqual(result, should_clean)
    
    def test_invalid_docx_structure(self):
        """Test handling of invalid DOCX files."""
        # Create invalid ZIP file
        invalid_path = Path(self.temp_dir) / "invalid.docx"
        with open(invalid_path, 'w') as f:
            f.write("This is not a ZIP file")
        
        with self.assertRaises(ValueError):
            self.simplifier.simplify_file(str(invalid_path))
    
    def test_debug_option(self):
        """Test debug option doesn't break processing."""
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


class TestLevelDescriptions(unittest.TestCase):
    """Test level description functionality."""
    
    def test_get_level_description(self):
        """Test getting individual level descriptions."""
        for level in range(9):
            desc = get_level_description(level)
            self.assertIsInstance(desc, str)
            self.assertGreater(len(desc), 10)  # Should be meaningful description
    
    def test_invalid_level_description(self):
        """Test that invalid levels raise ValueError."""
        with self.assertRaises(ValueError):
            get_level_description(-1)
        
        with self.assertRaises(ValueError):
            get_level_description(9)


if __name__ == '__main__':
    unittest.main()