"""
Simplification level descriptions for docx-simplifier.

This module contains human-readable descriptions of what each simplification
level does to DOCX files.
"""

LEVEL_DESCRIPTIONS = {
    0: "Remove only page breaks - minimal changes to preserve most formatting",
    1: "Remove basic formatting defaults (font size 24pt, black color, spacing, language tags, proofing errors)",
    2: "Remove font attributes, convert special hyphens, remove smart tags and complex script formatting",
    3: "Remove comments and comment references - cleaner document structure",
    4: "Remove hyperlinks (convert to plain text) - pure text content",
    5: "Remove hidden text, shadows, text colors, and highlighting - visible content only",
    6: "Remove all font specifications and sizes - uniform text appearance",
    7: "Remove all run properties except character styles - preserve only essential styling",
    8: "Remove all formatting attributes completely - plain text with document structure only"
}

def get_level_description(level):
    """Get the description for a specific simplification level."""
    if level not in LEVEL_DESCRIPTIONS:
        raise ValueError(f"Invalid level: {level}. Must be 0-8.")
    return LEVEL_DESCRIPTIONS[level]

def get_all_descriptions():
    """Get all level descriptions as a formatted string."""
    descriptions = []
    for level in sorted(LEVEL_DESCRIPTIONS.keys()):
        descriptions.append(f"Level {level}: {LEVEL_DESCRIPTIONS[level]}")
    return "\n".join(descriptions)