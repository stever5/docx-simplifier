"""
Unit tests for utility functions.
"""

import unittest
from docx_simplifier.utils import format_file_size


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_format_file_size_bytes(self):
        """Test formatting bytes."""
        self.assertEqual(format_file_size(0), "0.0 B")
        self.assertEqual(format_file_size(512), "512.0 B")
        self.assertEqual(format_file_size(1023), "1023.0 B")
    
    def test_format_file_size_kilobytes(self):
        """Test formatting kilobytes."""
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1536), "1.5 KB")
        self.assertEqual(format_file_size(1048575), "1024.0 KB")
    
    def test_format_file_size_megabytes(self):
        """Test formatting megabytes."""
        self.assertEqual(format_file_size(1048576), "1.0 MB")
        self.assertEqual(format_file_size(5242880), "5.0 MB")
        self.assertEqual(format_file_size(10485760), "10.0 MB")
    
    def test_format_file_size_gigabytes(self):
        """Test formatting gigabytes."""
        self.assertEqual(format_file_size(1073741824), "1.0 GB")
        self.assertEqual(format_file_size(2147483648), "2.0 GB")
    
    def test_format_file_size_terabytes(self):
        """Test formatting terabytes."""
        self.assertEqual(format_file_size(1099511627776), "1.0 TB")
        self.assertEqual(format_file_size(2199023255552), "2.0 TB")
    
    def test_format_file_size_petabytes(self):
        """Test formatting petabytes."""
        self.assertEqual(format_file_size(1125899906842624), "1.0 PB")
    
    def test_format_file_size_negative(self):
        """Test formatting negative sizes."""
        self.assertEqual(format_file_size(-100), "0 B")
        self.assertEqual(format_file_size(-1024), "0 B")
    
    def test_format_file_size_float(self):
        """Test formatting float sizes."""
        self.assertEqual(format_file_size(1536.5), "1.5 KB")
        self.assertEqual(format_file_size(1073741824.5), "1.0 GB")


if __name__ == '__main__':
    unittest.main()