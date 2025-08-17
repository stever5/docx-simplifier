"""
Main entry point for docx-simplifier package.

Allows running the package with 'python -m docx_simplifier'.
"""

import sys
from .cli import main

if __name__ == '__main__':
    main()