"""
Unit tests for levels functionality.
"""

import unittest
from docx_simplifier.levels import (
    LEVEL_DESCRIPTIONS,
    get_level_description,
    get_all_descriptions
)


class TestLevels(unittest.TestCase):
    """Test level description functionality."""
    
    def test_level_descriptions_completeness(self):
        """Test that all levels 0-8 have descriptions."""
        for level in range(9):  # 0-8
            self.assertIn(level, LEVEL_DESCRIPTIONS)
            self.assertIsInstance(LEVEL_DESCRIPTIONS[level], str)
            self.assertGreater(len(LEVEL_DESCRIPTIONS[level]), 0)
    
    def test_get_level_description_valid_levels(self):
        """Test getting descriptions for valid levels."""
        for level in range(9):  # 0-8
            description = get_level_description(level)
            self.assertEqual(description, LEVEL_DESCRIPTIONS[level])
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 10)  # Should be meaningful description
    
    def test_get_level_description_invalid_levels(self):
        """Test getting descriptions for invalid levels."""
        # Test negative levels
        with self.assertRaises(ValueError):
            get_level_description(-1)
        with self.assertRaises(ValueError):
            get_level_description(-5)
        
        # Test levels too high
        with self.assertRaises(ValueError):
            get_level_description(9)
        with self.assertRaises(ValueError):
            get_level_description(10)
        with self.assertRaises(ValueError):
            get_level_description(100)
    
    def test_get_level_description_edge_cases(self):
        """Test edge cases for level descriptions."""
        # Test string input (should raise exception)
        with self.assertRaises(ValueError):
            get_level_description("1")
        with self.assertRaises(ValueError):
            get_level_description("invalid")
        
        # Test None input
        with self.assertRaises(ValueError):
            get_level_description(None)
    
    def test_get_all_descriptions(self):
        """Test getting all descriptions formatted."""
        all_descriptions = get_all_descriptions()
        self.assertIsInstance(all_descriptions, str)
        self.assertGreater(len(all_descriptions), 100)  # Should be substantial
        
        # Should contain all levels
        for level in range(9):
            self.assertIn(f"Level {level}:", all_descriptions)
            self.assertIn(LEVEL_DESCRIPTIONS[level], all_descriptions)
        
        # Should be properly formatted with newlines
        lines = all_descriptions.split('\n')
        self.assertGreaterEqual(len(lines), 9)  # At least one line per level
    
    def test_level_descriptions_content_quality(self):
        """Test that level descriptions are meaningful."""
        for level, description in LEVEL_DESCRIPTIONS.items():
            # Should not be empty or just whitespace
            self.assertTrue(description.strip())
            
            # Should be at least somewhat descriptive
            self.assertGreater(len(description), 15)
            
            # Should start with appropriate language
            first_word = description.split()[0].lower()
            self.assertIn(first_word, ['remove', 'minimal', 'convert'])
    
    def test_level_progression(self):
        """Test that levels progress logically."""
        # Level 0 should be minimal
        level_0 = LEVEL_DESCRIPTIONS[0].lower()
        self.assertIn('minimal', level_0)
        
        # Higher levels should be more aggressive
        level_8 = LEVEL_DESCRIPTIONS[8].lower()
        self.assertIn('all', level_8)
        
        # Each level should be different
        descriptions = [LEVEL_DESCRIPTIONS[i] for i in range(9)]
        unique_descriptions = set(descriptions)
        self.assertEqual(len(unique_descriptions), 9)


if __name__ == '__main__':
    unittest.main()