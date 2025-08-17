# DOCX Simplifier

A Python application that simplifies the underlying structure of .docx files to remove unnecessary tags, making them easier to translate in computer-assisted translation tools. Based on the Groovy Tagwipe script for OmegaT.

## Features

- **9 Simplification Levels** (0-8): From minimal changes to complete formatting removal
- **Command Line Interface**: Process files from the terminal with progress reporting
- **Graphical Interface**: wxPython GUI with progress bars and performance statistics
- **High-Performance Processing**: LXML-based structured XML manipulation for guaranteed XML validity
- **Progress Reporting**: Real-time feedback for large file processing
- **Automatic Output Naming**: Generates `filename_simplified_level{N}.docx` by default

## Installation

### From Source

```bash
git clone <repository-url>
cd docx-simplifier
pip install -e .
```

### Dependencies

- Python 3.8+
- lxml 4.0+ (for XML processing)
- wxPython 4.0+ (for GUI)

## Usage

### Command Line

```bash
# Basic usage with default level 1
docx-simplifier document.docx

# Specify simplification level
docx-simplifier document.docx -l 5

# Custom output filename
docx-simplifier document.docx -o cleaned_document.docx

# With progress reporting (automatic for large files)
docx-simplifier document.docx --progress

# Show performance statistics
docx-simplifier document.docx -l 5 --stats

# With debug output
docx-simplifier document.docx --debug

# Show help and level descriptions
docx-simplifier --help
```

### GUI Application

```bash
docx-simplifier-gui
```

The GUI provides:
- File browser for selecting input documents
- Slider for choosing simplification level (0-8)
- Level descriptions
- Process button to execute simplification
- Info dialog with detailed level explanations
- Progress bars for long operations
- Performance statistics display
- Large file detection and warnings
- Processing time and size reduction reporting

### Python API

```python
from docx_simplifier import DocxSimplifier

# Progress callback function
def progress_callback(message, percentage):
    print(f"{message}: {percentage:.1f}%")

# Create simplifier with progress reporting
simplifier = DocxSimplifier(
    debug=False,
    progress_callback=progress_callback
)

# Process a file
output_path = simplifier.simplify_file(
    input_path="document.docx",
    level=5
)

# Get performance statistics
stats = simplifier.get_performance_stats()
print(f"Used {stats['compiled_patterns']} compiled patterns")
print(f"Optimizations: {', '.join(stats['optimizations'])}")

print(f"Simplified document saved to: {output_path}")
```

## Simplification Levels

- **Level 0**: Remove only page breaks - minimal changes
- **Level 1**: Remove basic formatting defaults (font size 24pt, black color, spacing, language tags)
- **Level 2**: Remove font attributes, convert special hyphens, remove smart tags
- **Level 3**: Remove comments and comment references
- **Level 4**: Remove hyperlinks (convert to plain text)
- **Level 5**: Remove hidden text, shadows, text colors, and highlighting
- **Level 6**: Remove all font specifications and sizes
- **Level 7**: Remove all run properties except character styles
- **Level 8**: Remove all formatting attributes completely

## How It Works

The application:

1. **Opens DOCX files** as ZIP archives
2. **Identifies XML files** that contain document content (document.xml, endnotes.xml, footer*.xml)
3. **Applies lxml-based cleaning** rules based on the selected level
4. **Preserves document structure** while removing formatting complexity
5. **Saves the result** as a new DOCX file

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage report
python -m pytest tests/ --cov=docx_simplifier --cov-report=html

# Run tests without coverage (faster)
python -m pytest tests/ -o addopts=""

# Run specific test modules
python -m pytest tests/test_core.py -v
python -m pytest tests/test_performance.py -v
```

### Test Coverage

The project maintains test coverage:
- **Core functionality**: 91% coverage with unit tests
- **Utility functions**: 100% coverage 
- **Constants and configuration**: 100% coverage
- **Performance features**: Benchmarking and optimization tests
- **Overall project**: 45%+ coverage (CLI/GUI excluded as they're interactive)

Coverage reports are generated in `htmlcov/` directory.

### Code Quality

The codebase follows quality standards:

```bash
# Code formatting
black docx_simplifier/

# Linting
flake8 docx_simplifier/

# Run development install with all tools
pip install -e ".[dev]"
```

**Quality features:**
- Type hints throughout
- Modular architecture with separated concerns
- Pre-compiled regex patterns for performance
- Error handling and validation
- Centralized configuration and constants
- Shared utility functions eliminate code duplication

## Original Credits

Based on the Groovy Tagwipe script for OmegaT:
- **Original Perl Version**: Thomas Cordonnier  
- **Groovy Port**: Briac Pilpré
- **Enhancements**: Kos Ivantsov

## Troubleshooting

### Common Issues

**"Invalid DOCX file" Error**
- Ensure the file is a valid .docx document
- Try opening the file in Microsoft Word first

**Permission Errors**
- Check that you have write permissions to the output directory
- Try specifying a different output location

**GUI Not Starting**
- Ensure wxPython is installed: `pip install wxpython`
- On Linux, you may need additional packages: `sudo apt-get install python3-wxgtk4.0-dev`

### Debug Mode

Use the `--debug` flag for detailed processing information:

```bash
docx-simplifier document.docx --debug
```

## File Format Support

- **Input**: .docx files (Office Open XML format)
- **Output**: .docx files with simplified structure

## Limitations

- Only processes .docx files (not .doc, .rtf, etc.)

## Version History

- **1.0.0**: Initial Python implementation based on Groovy Tagwipe
  - Feature parity with original script
  - Added GUI interface and improved CLI
  - Enhanced error handling and validation
