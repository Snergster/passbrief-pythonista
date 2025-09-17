#!/usr/bin/env python3
"""
Script to extract class definitions from the monolithic sr22t_briefing_v31.py file.
This will help speed up the refactoring process.
"""

import re

def extract_classes(file_path):
    """Extract all class definitions with their line ranges."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    classes = []
    current_class = None
    class_start = None
    indent_level = None

    for i, line in enumerate(lines):
        # Check for class definition
        class_match = re.match(r'^class\s+(\w+)', line)
        if class_match:
            # Save previous class if exists
            if current_class:
                classes.append({
                    'name': current_class,
                    'start': class_start,
                    'end': i - 1,
                    'lines': lines[class_start:i]
                })

            # Start new class
            current_class = class_match.group(1)
            class_start = i
            indent_level = len(line) - len(line.lstrip())
            continue

        # Check for end of class (next top-level definition or function)
        if current_class and line.strip():
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= indent_level and (line.startswith('class ') or line.startswith('def ') or line.startswith('if __name__')):
                # End of current class
                classes.append({
                    'name': current_class,
                    'start': class_start,
                    'end': i - 1,
                    'lines': lines[class_start:i]
                })
                current_class = None

    # Handle last class
    if current_class:
        classes.append({
            'name': current_class,
            'start': class_start,
            'end': len(lines) - 1,
            'lines': lines[class_start:]
        })

    return classes

if __name__ == "__main__":
    classes = extract_classes("../sr22t_briefing_v31.py")

    print("Classes found:")
    for cls in classes:
        print(f"  {cls['name']}: lines {cls['start']+1}-{cls['end']+1} ({len(cls['lines'])} lines)")