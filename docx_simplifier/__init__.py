"""
docx-simplifier: Simplify DOCX file structure to make them easier to translate.

This package provides tools to remove formatting complexity from DOCX files
while preserving the core content, making them more suitable for translation
workflows.

Available components:
- DocxSimplifier: High-performance implementation with compiled patterns and progress reporting
"""

from .constants import VERSION
__version__ = VERSION
__author__ = "docx-simplifier contributors"
__license__ = "GPL-3.0"

from .core import DocxSimplifier
from .levels import LEVEL_DESCRIPTIONS

__all__ = ["DocxSimplifier", "LEVEL_DESCRIPTIONS"]