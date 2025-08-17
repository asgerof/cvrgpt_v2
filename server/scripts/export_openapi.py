#!/usr/bin/env python3
"""Export OpenAPI schema to JSON file."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cvrgpt_api.api import app

def main():
    """Export OpenAPI schema to openapi.json."""
    schema = app.openapi()
    
    # Write to server/openapi.json
    output_file = Path(__file__).parent.parent / "openapi.json"
    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"OpenAPI schema exported to {output_file}")

if __name__ == "__main__":
    main()