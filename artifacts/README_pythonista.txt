# PassBrief for Pythonista iOS

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
