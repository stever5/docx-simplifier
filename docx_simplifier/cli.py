"""
Command-line interface for docx-simplifier with progress reporting.

This module provides the CLI entry point for the docx-simplifier application.
"""

import argparse
import sys
import time
from pathlib import Path

from .core import DocxSimplifier
from .levels import get_all_descriptions, get_level_description
from .utils import format_file_size
from .constants import LARGE_FILE_THRESHOLD, PROGRESS_BAR_LENGTH


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='docx-simplifier',
        description='Simplify DOCX file structure to make them easier to translate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Simplification Levels:
{get_all_descriptions()}

Examples:
  docx-simplifier document.docx                    # Simplify at level 1
  docx-simplifier document.docx -l 3              # Simplify at level 3
  docx-simplifier document.docx -o clean.docx     # Specify output file
  docx-simplifier document.docx -l 5 --progress   # Level 5 with progress bar
  docx-simplifier document.docx --stats           # Show performance statistics
"""
    )
    
    parser.add_argument(
        'input_file',
        help='Input DOCX file to simplify'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: input_simplified_level{N}.docx)'
    )
    
    parser.add_argument(
        '-l', '--level',
        type=int,
        choices=range(0, 9),
        default=1,
        help='Simplification level (0-8, default: 1)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Print debug information during processing'
    )
    
    parser.add_argument(
        '--progress',
        action='store_true',
        help='Show progress bar for large files'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show performance statistics after processing'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser


def progress_callback(message: str, percentage: float):
    """Simple progress callback for console output."""
    # Create a simple progress bar
    filled_length = int(PROGRESS_BAR_LENGTH * percentage / 100)
    bar = '█' * filled_length + '░' * (PROGRESS_BAR_LENGTH - filled_length)
    
    print(f'\r{message}: [{bar}] {percentage:.1f}%', end='', flush=True)
    
    if percentage >= 100:
        print()  # New line when complete


def validate_input_file(filepath):
    """Validate that the input file exists and is a DOCX file."""
    path = Path(filepath)
    
    if not path.exists():
        print(f"Error: Input file '{filepath}' not found.", file=sys.stderr)
        return False
    
    if not path.is_file():
        print(f"Error: '{filepath}' is not a file.", file=sys.stderr)
        return False
    
    if path.suffix.lower() != '.docx':
        print(f"Warning: '{filepath}' does not have a .docx extension.", file=sys.stderr)
    
    return True


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate input file
    if not validate_input_file(args.input_file):
        sys.exit(1)
    
    # Get file size for performance info
    input_path = Path(args.input_file)
    file_size = input_path.stat().st_size
    
    if args.progress or file_size > LARGE_FILE_THRESHOLD:  # Show info for large files
        print(f"Processing: {args.input_file} ({format_file_size(file_size)})")
        print(f"Simplification level: {args.level} - {get_level_description(args.level)}")
    
    # Set up progress callback if requested or for large files
    progress_cb = progress_callback if (args.progress or file_size > LARGE_FILE_THRESHOLD) else None
    
    # Create simplifier instance
    simplifier = DocxSimplifier(
        debug=args.debug,
        progress_callback=progress_cb
    )
    
    try:
        # Record start time for performance measurement
        start_time = time.time()
        
        # Process the file
        output_path = simplifier.simplify_file(
            input_path=args.input_file,
            output_path=args.output,
            level=args.level
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Get file sizes and processing statistics
        output_size = Path(output_path).stat().st_size
        file_size_reduction = ((file_size - output_size) / file_size) * 100 if file_size > 0 else 0
        
        # Get processing stats including XML content reduction
        stats = simplifier.get_performance_stats()
        xml_reduction = stats.get('xml_reduction_percent', 0)
        xml_before = stats.get('xml_size_before', 0)
        xml_after = stats.get('xml_size_after', 0)
        
        if args.progress or file_size > LARGE_FILE_THRESHOLD:
            print(f"\n✅ Successfully simplified '{args.input_file}' to '{output_path}'")
            print(f"⏱️  Processing time: {processing_time:.2f} seconds")
            print(f"📁 File Size: {format_file_size(file_size)} → {format_file_size(output_size)} ({file_size_reduction:.1f}% reduction)")
            if xml_before > 0:
                print(f"📄 XML Content: {format_file_size(xml_before)} → {format_file_size(xml_after)} ({xml_reduction:.1f}% reduction)")
        else:
            print(f"Successfully simplified '{args.input_file}' to '{output_path}'")
            print(f"Applied simplification level {args.level}: {get_level_description(args.level)}")
            if xml_before > 0:
                print(f"XML content reduced by {xml_reduction:.1f}%")
        
        # Show performance statistics if requested
        if args.stats:
            print(f"\n📊 Performance Statistics:")
            print(f"   • Processing approach: {stats.get('approach', 'structured XML manipulation')}")
            print(f"   • Total time: {stats.get('total_time', f'{processing_time:.4f}s')}")
            if 'elements_removed' in stats:
                print(f"   • Elements removed: {stats['elements_removed']:,}")
            if 'elements_modified' in stats:
                print(f"   • Elements modified: {stats['elements_modified']:,}")
            print(f"   • Processing rate: {format_file_size(file_size / processing_time)}/second")
            
            print(f"\n🚀 Optimizations applied:")
            for opt in stats.get('optimizations', []):
                print(f"   • {opt}")
        
    except Exception as e:
        print(f"\n❌ Error processing file: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
