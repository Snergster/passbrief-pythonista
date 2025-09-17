#!/usr/bin/env python3
"""
Pythonista Deployment Builder for PassBrief

This script combines the modular PassBrief codebase into a single Python file
suitable for deployment on Pythonista iOS, while maintaining all functionality.

Key Features:
- Combines all modules into single file with proper dependency order
- Removes development-only imports and code
- Preserves all aviation safety-critical functionality
- Creates iOS-optimized file paths and configurations
- Generates comprehensive test suite for validation
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

class PythonistaBuilder:
    """Builds single-file deployment for Pythonista iOS"""

    def __init__(self, src_dir="src", output_dir="artifacts"):
        self.src_dir = Path(src_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Module dependency order (to avoid import issues)
        self.module_order = [
            "config.py",
            "performance/data.py",
            "performance/calculator.py",
            "weather/manager.py",
            "airports/manager.py",
            "garmin/pilot.py",
            "briefing/sid.py",
            "briefing/caps.py",
            "briefing/flavortext.py",
            "briefing/chatgpt.py",
            "briefing/generator.py"
        ]

        # Imports to remove in single-file deployment
        self.remove_imports = [
            "from ..config import Config",
            "from ..performance import",
            "from ..weather import",
            "from ..airports import",
            "from ..garmin import",
            "from .sid import",
            "from .caps import",
            "from .flavortext import",
            "from .chatgpt import",
            "from .data import",
            "from .calculator import",
            "from .manager import",
            "from .pilot import"
        ]

    def read_module_file(self, module_path):
        """Read a module file and clean it for single-file deployment"""
        full_path = self.src_dir / "passbrief" / module_path

        if not full_path.exists():
            print(f"⚠️ Warning: Module file not found: {full_path}")
            return ""

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove relative imports
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Skip relative imports that will be unnecessary in single file
            if any(imp in line for imp in self.remove_imports):
                continue
            # Keep all other lines including docstrings, comments, and code
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def build_single_file(self):
        """Build the complete single-file deployment"""
        print("🔨 Building PassBrief for Pythonista deployment...")

        # Start with file header
        output_content = self._generate_file_header()

        # Add standard library imports
        output_content += self._generate_imports()

        # Add configuration constants
        output_content += "\n\n" + "# " + "=" * 40 + "\n"
        output_content += "# CONFIGURATION\n"
        output_content += "# " + "=" * 40 + "\n\n"
        output_content += self.read_module_file("config.py")

        # Add performance data and calculator
        output_content += "\n\n" + "# " + "=" * 40 + "\n"
        output_content += "# PERFORMANCE SYSTEM\n"
        output_content += "# " + "=" * 40 + "\n\n"
        output_content += self.read_module_file("performance/data.py")
        output_content += "\n\n"
        output_content += self.read_module_file("performance/calculator.py")

        # Add external data managers
        output_content += "\n\n" + "# " + "=" * 40 + "\n"
        output_content += "# EXTERNAL DATA INTEGRATION\n"
        output_content += "# " + "=" * 40 + "\n\n"
        output_content += self.read_module_file("weather/manager.py")
        output_content += "\n\n"
        output_content += self.read_module_file("airports/manager.py")
        output_content += "\n\n"
        output_content += self.read_module_file("garmin/pilot.py")

        # Add briefing components
        output_content += "\n\n" + "# " + "=" * 40 + "\n"
        output_content += "# BRIEFING GENERATION COMPONENTS\n"
        output_content += "# " + "=" * 40 + "\n\n"
        for briefing_module in ["sid.py", "caps.py", "flavortext.py", "chatgpt.py"]:
            output_content += self.read_module_file(f"briefing/{briefing_module}")
            output_content += "\n\n"

        # Add main briefing generator (application orchestrator)
        output_content += "\n\n" + "# " + "=" * 40 + "\n"
        output_content += "# MAIN APPLICATION ORCHESTRATOR\n"
        output_content += "# " + "=" * 40 + "\n\n"
        output_content += self.read_module_file("briefing/generator.py")

        # Add public API and convenience functions
        output_content += self._generate_public_api()

        # Add main execution block
        output_content += self._generate_main_execution()

        # Write the output file
        output_file = self.output_dir / "passbrief_pythonista.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)

        print(f"✅ Created single-file deployment: {output_file}")
        print(f"   File size: {len(output_content):,} characters")

        return output_file

    def _generate_file_header(self):
        """Generate file header with metadata"""
        return f'''#!/usr/bin/env python3
"""
PassBrief - SR22T Flight Briefing Tool for Pythonista iOS
Single-file deployment generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

A comprehensive departure/arrival briefing tool designed for Cirrus SR22T aircraft operations.
Optimized for Pythonista iOS with all modules combined for easy deployment.

🛫 AVIATION SAFETY NOTICE 🛫
This software handles safety-critical aviation performance data. All calculations
are based on embedded Pilot's Operating Handbook (POH) tables and follow
conservative aviation practices. Users are responsible for verifying all
performance data against official sources.

Key Features:
- Safety-critical performance calculations based on POH data
- METAR weather integration with automatic unit conversion
- Garmin Pilot PDF briefing parsing and route analysis
- Magnetic variation handling for accurate wind component calculations
- CAPS (Cirrus Airframe Parachute System) altitude integration
- AI-powered flight plan analysis and passenger briefings
- Professional takeoff briefing with phased emergency procedures

Usage:
    import passbrief_pythonista as passbrief
    briefing_gen = passbrief.create_briefing_generator()

    # Interactive workflow
    while True:
        inputs = briefing_gen.get_user_inputs()
        if not inputs:
            break
        briefing = briefing_gen.generate_briefing(inputs)
        print(briefing)
        if input("Another briefing? (y/n): ").lower() != 'y':
            break

Generated from modular source at: https://github.com/user/passbrief-pythonista
"""

'''

    def _generate_imports(self):
        """Generate all necessary imports for single-file deployment"""
        return '''
# Standard library imports
import math
import os
import sys
import json
import glob
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import tempfile
import re

# Check for optional dependencies with fallbacks
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests not available - some network features disabled")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Provide basic fallbacks for numpy functions if needed
    class SimpleNumpy:
        @staticmethod
        def interpolate(x, xp, fp):
            """Simple interpolation fallback if numpy not available"""
            if x <= xp[0]:
                return fp[0]
            if x >= xp[-1]:
                return fp[-1]

            for i in range(len(xp) - 1):
                if xp[i] <= x <= xp[i + 1]:
                    ratio = (x - xp[i]) / (xp[i + 1] - xp[i])
                    return fp[i] + ratio * (fp[i + 1] - fp[i])
            return fp[0]

    np = SimpleNumpy()

# Pythonista environment detection
def is_pythonista():
    """Detect if running in Pythonista iOS environment"""
    return 'Pythonista3' in sys.executable or 'Pythonista' in sys.executable

# iOS-optimized file paths
def get_ios_file_search_paths():
    """Get iOS-appropriate file search paths for Garmin Pilot files"""
    if is_pythonista():
        return [
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Documents/Inbox'),
            '/var/mobile/Containers/Shared/AppGroup',
            '/private/var/mobile/Containers/Shared/AppGroup'
        ]
    else:
        return ['.', '~/Downloads', '~/Documents', '~/Desktop']

print(f"🍎 Pythonista environment: {is_pythonista()}")
print(f"📱 File search paths: {len(get_ios_file_search_paths())} locations")
'''

    def _generate_public_api(self):
        """Generate public API functions for easy access"""
        return '''

# ============================================
# PUBLIC API AND CONVENIENCE FUNCTIONS
# ============================================

def create_briefing_generator():
    """
    Create a new BriefingGenerator instance - the main entry point for the application.

    Returns:
        BriefingGenerator: Ready-to-use briefing generator instance
    """
    return BriefingGenerator()

def get_version():
    """Return the current version of PassBrief."""
    return "1.0.0-pythonista"

def get_build_info():
    """Return build information for diagnostics"""
    return {
        "platform": "pythonista" if is_pythonista() else "desktop",
        "requests_available": REQUESTS_AVAILABLE,
        "numpy_available": NUMPY_AVAILABLE,
        "file_search_paths": get_ios_file_search_paths(),
        "build_date": "''' + datetime.now().isoformat() + '''"
    }

# Main public API - these are the primary classes users should access
__all__ = [
    'create_briefing_generator',
    'get_version',
    'get_build_info',
    'BriefingGenerator',
    'PerformanceCalculator',
    'WeatherManager',
    'AirportManager',
    'GarminPilotBriefingManager',
    'SIDManager',
    'CAPSManager',
    'FlavorTextManager',
    'ChatGPTAnalysisManager',
    'Config',
    'EMBEDDED_SR22T_PERFORMANCE'
]
'''

    def _generate_main_execution(self):
        """Generate main execution block for direct script execution"""
        return '''

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    """
    Main execution for standalone script operation
    """
    print("=" * 60)
    print("🛫 PassBrief - SR22T Flight Briefing Tool")
    print("   Pythonista iOS Deployment")
    print("=" * 60)

    # Show build information
    build_info = get_build_info()
    print(f"Platform: {build_info['platform']}")
    print(f"Version: {get_version()}")
    print(f"Network capabilities: {'✅' if build_info['requests_available'] else '❌'}")
    print(f"File search paths: {len(build_info['file_search_paths'])}")
    print()

    # Create and run briefing generator
    try:
        briefing_gen = create_briefing_generator()
        print("🎯 Briefing generator created successfully!")
        print("📋 Ready for flight planning operations.")
        print()
        print("Usage examples:")
        print("  briefing_gen.get_user_inputs()  # Interactive workflow")
        print("  briefing_gen.generate_briefing(inputs)  # Generate briefing")
        print()

        # Optionally run interactive mode
        if input("Start interactive briefing workflow? (y/n): ").lower() == 'y':
            while True:
                inputs = briefing_gen.get_user_inputs()
                if not inputs:
                    break

                briefing = briefing_gen.generate_briefing(inputs)
                print(briefing)

                if input("\\nAnother briefing? (y/n): ").lower() != 'y':
                    break

    except Exception as e:
        print(f"❌ Error creating briefing generator: {e}")
        import traceback
        traceback.print_exc()

    print("\\n✈️ Thank you for using PassBrief!")
'''

    def build_test_file(self):
        """Build a combined test file for Pythonista validation"""
        print("🧪 Building test suite for Pythonista...")

        test_content = '''#!/usr/bin/env python3
"""
PassBrief Test Suite for Pythonista iOS
Combined test file for validating deployment
"""

def test_imports():
    """Test that all components can be imported"""
    print("Testing imports...")
    try:
        import passbrief_pythonista as passbrief
        assert hasattr(passbrief, 'create_briefing_generator')
        assert hasattr(passbrief, 'BriefingGenerator')
        assert hasattr(passbrief, 'PerformanceCalculator')
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_briefing_generator():
    """Test briefing generator creation"""
    print("Testing briefing generator...")
    try:
        import passbrief_pythonista as passbrief
        bg = passbrief.create_briefing_generator()
        assert bg is not None
        print("✅ Briefing generator created successfully")
        return True
    except Exception as e:
        print(f"❌ Briefing generator error: {e}")
        return False

def test_performance_calculations():
    """Test basic performance calculations"""
    print("Testing performance calculations...")
    try:
        import passbrief_pythonista as passbrief
        calc = passbrief.PerformanceCalculator()

        # Test pressure altitude
        pa = calc.calculate_pressure_altitude(29.92, 4500)
        assert pa == 4500  # Should be field elevation at standard pressure

        # Test density altitude
        da = calc.calculate_density_altitude(4500, 15)
        assert isinstance(da, (int, float))

        # Test wind components
        wind = calc.calculate_wind_components(270, 10, 90)
        assert 'headwind' in wind
        assert 'crosswind' in wind

        print("✅ Performance calculations working")
        return True
    except Exception as e:
        print(f"❌ Performance calculation error: {e}")
        return False

def run_all_tests():
    """Run all validation tests"""
    print("🧪 Running PassBrief Pythonista Validation Tests")
    print("=" * 50)

    tests = [
        test_imports,
        test_briefing_generator,
        test_performance_calculations
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Deployment is ready for use.")
    else:
        print("⚠️ Some tests failed. Check deployment before use.")

    return passed == total

if __name__ == "__main__":
    run_all_tests()
'''

        test_file = self.output_dir / "test_passbrief_pythonista.py"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)

        print(f"✅ Created test suite: {test_file}")
        return test_file

    def create_readme(self):
        """Create iOS-specific README"""
        readme_content = '''# PassBrief for Pythonista iOS

## Quick Start

1. Copy `passbrief_pythonista.py` to your Pythonista Documents folder
2. Run the validation test: `python test_passbrief_pythonista.py`
3. Import and use: `import passbrief_pythonista as passbrief`

## Usage

```python
import passbrief_pythonista as passbrief

# Create briefing generator
briefing_gen = passbrief.create_briefing_generator()

# Interactive workflow
while True:
    inputs = briefing_gen.get_user_inputs()
    if not inputs:
        break

    briefing = briefing_gen.generate_briefing(inputs)
    print(briefing)

    if input("Another briefing? (y/n): ").lower() != 'y':
        break
```

## Features

✅ Complete SR22T performance calculations
✅ METAR weather integration (requires internet)
✅ Garmin Pilot PDF briefing parsing
✅ CAPS altitude calculations
✅ AI-powered flight analysis (requires OpenAI API key)
✅ Phased takeoff emergency briefings

## File Requirements

- Main app: `passbrief_pythonista.py` (~150KB)
- Optional: `test_passbrief_pythonista.py` for validation
- Optional: OpenAI API key file for AI features

## Troubleshooting

- **Import errors**: Ensure file is in Pythonista Documents folder
- **Network issues**: Check iOS network permissions
- **File not found**: Use diagnostic mode to explore file system
- **API errors**: Verify internet connection and API keys

For full documentation, see: https://github.com/user/passbrief-pythonista/docs/
'''

        readme_file = self.output_dir / "README_pythonista.txt"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"✅ Created iOS README: {readme_file}")
        return readme_file

def main():
    """Main build process"""
    print("🔨 PassBrief Pythonista Builder")
    print("=" * 40)

    # Create builder instance
    builder = PythonistaBuilder()

    # Build single file deployment
    output_file = builder.build_single_file()

    # Build test suite
    test_file = builder.build_test_file()

    # Create README
    readme_file = builder.create_readme()

    # Summary
    print("\\n" + "=" * 40)
    print("🎉 Build completed successfully!")
    print("\\nDeployment artifacts:")
    print(f"  📱 Main app: {output_file}")
    print(f"  🧪 Test suite: {test_file}")
    print(f"  📖 README: {readme_file}")

    # File sizes
    if output_file.exists():
        size_kb = output_file.stat().st_size / 1024
        print(f"\\n📊 Main app size: {size_kb:.1f} KB")

    print("\\n🚀 Ready for Pythonista deployment!")
    print("   1. Copy files to iOS device")
    print("   2. Run test suite to validate")
    print("   3. Import and use passbrief_pythonista")

if __name__ == "__main__":
    main()