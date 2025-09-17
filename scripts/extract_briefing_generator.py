#!/usr/bin/env python3
"""
Script to extract the BriefingGenerator class from the monolithic file.
"""

def extract_briefing_generator(source_file, output_file):
    """Extract BriefingGenerator class and main function."""
    with open(source_file, 'r') as f:
        lines = f.readlines()

    # Find the BriefingGenerator class (starts at line 3495)
    class_start = 3494  # 0-indexed
    main_start = 5532   # 0-indexed, where main() starts

    # Extract the class and main function
    extracted_lines = []

    # Add module header
    extracted_lines.extend([
        '#!/usr/bin/env python3\n',
        '"""\n',
        'Briefing Generator - Main Application Orchestrator\n',
        '\n',
        'This is the primary class that coordinates all briefing generation activities.\n',
        'It provides a workflow-based interface for comprehensive flight preparation.\n',
        '"""\n',
        '\n',
        'import math\n',
        'from datetime import datetime\n',
        '\n',
        '# Import all required modules\n',
        'from ..config import Config\n',
        'from ..performance import PerformanceCalculator\n',
        'from ..weather import WeatherManager\n',
        'from ..airports import AirportManager\n',
        'from ..garmin import GarminPilotBriefingManager\n',
        'from .sid import SIDManager\n',
        'from .caps import CAPSManager\n',
        'from .flavortext import FlavorTextManager\n',
        'from .chatgpt import ChatGPTAnalysisManager\n',
        '\n',
        '\n'
    ])

    # Extract BriefingGenerator class
    extracted_lines.extend(lines[class_start:main_start])

    # Extract main function
    extracted_lines.extend(lines[main_start:])

    # Write to output file
    with open(output_file, 'w') as f:
        f.writelines(extracted_lines)

    print(f"✅ Extracted BriefingGenerator class to {output_file}")
    print(f"   Lines extracted: {len(extracted_lines)}")

if __name__ == "__main__":
    extract_briefing_generator(
        "sr22t_briefing_v31.py",
        "src/passbrief/briefing/generator.py"
    )