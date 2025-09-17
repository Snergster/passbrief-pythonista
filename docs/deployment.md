# Deployment Guide

## Overview

PassBrief supports two deployment modes:

1. **Development Mode**: Full modular structure for development and testing
2. **Production Mode**: Single-file deployment for Pythonista iOS

## Development Deployment

### Prerequisites

- Python 3.8 or higher
- Required packages: `requests`, `json`, `math`, `numpy`, `os`, `glob`, `xml.etree.ElementTree`, `datetime`

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd passbrief-pythonista
   ```

2. Install in development mode:
   ```bash
   # Add src to Python path or install in development mode
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

3. Run tests:
   ```bash
   python -m pytest tests/
   ```

4. Run the application:
   ```bash
   python -c "import passbrief; briefing_gen = passbrief.create_briefing_generator()"
   ```

## Pythonista iOS Deployment

### Background

Pythonista iOS has constraints that require a different deployment approach:

- Limited file system access
- Preference for minimal file count
- iOS-specific file paths
- Manual file transfer process

### Build Process

The project includes build scripts to create a single-file deployment suitable for Pythonista:

1. **Build Script** (`scripts/build_for_pythonista.py`):
   - Combines all modules into a single Python file
   - Preserves all functionality while meeting Pythonista constraints
   - Maintains proper imports and dependencies
   - Creates deployment-ready artifacts

2. **File Structure for Pythonista**:
   ```
   artifacts/
   ├── passbrief_pythonista.py    # Single-file application
   ├── test_passbrief.py          # Combined test suite
   └── README_pythonista.txt      # iOS-specific instructions
   ```

### Manual Deployment Steps

1. **Generate Deployment Files**:
   ```bash
   python scripts/build_for_pythonista.py
   ```

2. **Transfer to iOS Device**:
   - Use AirDrop, iCloud Drive, or iTunes File Sharing
   - Copy `passbrief_pythonista.py` to Pythonista's file directory
   - Optionally copy test files for validation

3. **Run on Pythonista**:
   ```python
   # In Pythonista console
   import passbrief_pythonista as passbrief

   # Create and run briefing generator
   briefing_gen = passbrief.create_briefing_generator()
   ```

### iOS-Specific Considerations

#### File Paths
The application automatically detects Pythonista environment and adjusts file paths:

- **Garmin Pilot Files**: Multiple search locations across iOS file system
- **Temporary Files**: Uses iOS-appropriate temporary directories
- **Cache Management**: Respects iOS storage limitations

#### Network Access
- METAR data fetching works through iOS network stack
- Airport database queries function normally
- Magnetic variation API calls supported

#### User Interface
- Terminal-based interface optimized for Pythonista console
- Clear prompts and progress indicators
- Error handling designed for touch-screen interaction

## Configuration Management

### Environment Detection

The application automatically detects the deployment environment:

```python
import sys
import os

def is_pythonista():
    """Detect if running in Pythonista iOS environment"""
    return 'Pythonista3' in sys.executable

def get_file_search_paths():
    """Get appropriate file search paths for current environment"""
    if is_pythonista():
        return [
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Documents/Inbox'),
            '/private/var/mobile/Containers/Shared/AppGroup/*/File Provider Storage/Locations'
        ]
    else:
        return ['.', '~/Downloads', '~/Documents']
```

### Version Management

For Pythonista iOS compatibility, use clear versioning:

- **Major Changes** (substantial features): Increment number (v31 → v32)
- **Minor Changes** (small fixes/tweaks): Add letters (v31 → v31A, v31B)

This makes it easy to track versions on iOS devices.

## Performance Considerations

### Pythonista Optimizations

1. **Startup Time**: Single-file deployment reduces import overhead
2. **Memory Usage**: Embedded data tables minimize file I/O
3. **Network Efficiency**: Caching strategies for API calls
4. **Battery Life**: Optimized for mobile power constraints

### File Size Management

The build process optimizes for Pythonista deployment:

- Removes development-only code (tests, debug utilities)
- Compresses embedded data where possible
- Minimizes external dependencies
- Creates platform-specific optimizations

## Troubleshooting

### Common Issues

#### Import Errors in Development
```bash
# Solution: Add src to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### File Not Found in Pythonista
- Check file permissions in iOS Settings
- Verify file is in accessible location
- Use diagnostic mode to explore file system

#### Network Issues on iOS
- Check iOS network permissions for Pythonista
- Verify internet connectivity
- Test with manual weather input as fallback

### Diagnostic Mode

The application includes comprehensive diagnostic capabilities:

```python
# Enable diagnostic mode
briefing_gen = passbrief.create_briefing_generator()
briefing_gen.garmin_manager.run_diagnostics()
```

This provides detailed information about:
- File system access and search paths
- Network connectivity and API availability
- Performance data validation
- Configuration status

## Maintenance

### Updating Pythonista Deployment

1. Make changes in development environment
2. Run full test suite
3. Rebuild for Pythonista: `python scripts/build_for_pythonista.py`
4. Transfer updated file to iOS device
5. Test critical functions on device

### Version Tracking

Keep track of deployed versions:
- Tag releases in git: `git tag v31A`
- Document changes in deployment artifacts
- Maintain backward compatibility for data files

## Security Considerations

### API Keys
- Store sensitive keys in separate files
- Use environment variables where possible
- Never commit keys to version control
- Provide clear setup instructions for API access

### Data Privacy
- No telemetry or data collection
- All calculations performed locally
- Network access only for public aviation data
- User flight data never transmitted