"""Generate OpenAPI schema for TypeScript client generation."""

import json
from pathlib import Path

from main import app


def generate_openapi_schema():
    """Generate OpenAPI schema file."""
    schema = app.openapi()
    
    # Ensure output directory exists
    output_dir = Path("../../packages/types/schemas")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Write schema to file
    schema_file = output_dir / "openapi.json"
    with open(schema_file, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"OpenAPI schema generated at {schema_file}")


if __name__ == "__main__":
    generate_openapi_schema()
