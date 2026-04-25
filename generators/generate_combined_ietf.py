#!/usr/bin/env python3
"""
Generate combined IETF model OpenAPI specification.
Merges all 28 IETF standard module specifications into a single unified spec.
"""

import json
from pathlib import Path

script_dir = Path(__file__).parent

def generate_combined_ietf():
    """Generate all-ietf.json combining all IETF module specs."""

    base_path = script_dir.parent / 'swagger-ietf-model' / 'api'

    # Base combined spec
    combined = {
        "openapi": "3.0.0",
        "info": {
            "title": "IETF Standard YANG Models - All Modules",
            "description": """Complete IETF Standards collection for IOS-XE 17.18.1.

This unified specification combines all 28 IETF-standardized YANG modules supported by Cisco IOS-XE.

**IETF Standards Categories:**
- **Core Networking**: interfaces, IP, routing, ACLs
- **System Management**: system, YANG library, subscriptions
- **Protocols**: BFD, LLDP, syslog, event notifications
- **Data Models**: schema mount, origin, metadata

**Key Modules:**
- ietf-interfaces: Standard interface management (RFC 8343)
- ietf-ip: IPv4/IPv6 address configuration (RFC 8344)
- ietf-routing: Core routing model (RFC 8349)
- ietf-yang-library: YANG module discovery (RFC 8525)
- ietf-system: System identification and configuration (RFC 7317)
- ietf-netconf-*: NETCONF protocol operations
- ietf-restconf: RESTCONF protocol (RFC 8040)

**Standards Compliance:**
All modules implement official IETF RFCs ensuring vendor-neutral, interoperable network management.

**Total Modules:** 28 IETF standard modules
**Base URL:** https://10.85.134.65/restconf/data
**Authentication:** Basic Auth (admin/EN-TME-Cisco123)
""",
            "version": "17.18.1",
            "contact": {
                "name": "IETF YANG Models",
                "url": "https://datatracker.ietf.org/doc/search/?name=yang&activeDrafts=on&rfcs=on"
            }
        },
        "servers": [
            {
                "url": "https://10.85.134.65/restconf",
                "description": "IOS-XE Device (C9300)"
            }
        ],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {
                "BasicAuth": {
                    "type": "http",
                    "scheme": "basic"
                }
            }
        },
        "security": [{"BasicAuth": []}],
        "tags": []
    }

    # Track statistics
    stats = {
        "total_paths": 0,
        "total_schemas": 0,
        "modules_merged": 0,
        "modules": []
    }

    # Get all JSON files (exclude manifest and combined)
    spec_files = sorted([f for f in base_path.glob("*.json")
                        if f.name not in ["manifest.json", "all-ietf.json"]])

    # Merge each module
    for spec_file in spec_files:
        with open(spec_file, 'r') as f:
            spec = json.load(f)

        module_name = spec_file.stem
        stats["modules"].append(module_name)

        # Merge paths
        paths_count = 0
        if "paths" in spec:
            for path, methods in spec["paths"].items():
                combined["paths"][path] = methods
                paths_count += 1
                stats["total_paths"] += 1

        # Merge schemas
        schemas_count = 0
        if "components" in spec and "schemas" in spec["components"]:
            for schema_name, schema_def in spec["components"]["schemas"].items():
                combined["components"]["schemas"][schema_name] = schema_def
                schemas_count += 1
                stats["total_schemas"] += 1

        # Add tag
        tag_name = module_name.replace("ietf-", "").replace("-", " ").title()
        combined["tags"].append({
            "name": tag_name,
            "description": f"IETF {tag_name} Standard Model"
        })

        stats["modules_merged"] += 1
        print(f"✅ Merged {module_name}: {paths_count} paths, {schemas_count} schemas")

    # Write combined spec
    output_file = base_path / "all-ietf.json"
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n📊 Combined IETF Model Statistics:")
    print(f"   Modules Merged: {stats['modules_merged']}")
    print(f"   Total Paths: {stats['total_paths']}")
    print(f"   Total Schemas: {stats['total_schemas']}")
    print(f"   Output: {output_file}")

    return output_file, stats

def generate_html_page(stats):
    """Generate all-ietf.html Swagger UI page."""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IETF Standard Models - All Modules</title>
    <link rel="stylesheet" type="text/css" href="../swagger-ui-5.11.0/dist/swagger-ui.css">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        .header {{
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            padding: 30px 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 300;
        }}

        .header p {{
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}

        .stat-box {{
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        #swagger-ui {{
            max-width: 1400px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .swagger-ui .topbar {{
            display: none;
        }}

        .swagger-ui .info .title {{
            color: #1e88e5;
        }}

        .back-link {{
            display: inline-block;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            margin-top: 15px;
            transition: background 0.3s;
        }}

        .back-link:hover {{
            background: rgba(255,255,255,0.3);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 IETF Standard YANG Models</h1>
        <p>Complete unified specification - All {stats['modules_merged']} IETF modules</p>
        <div class="stats">
            <div class="stat-box">
                <span class="stat-number">{stats['modules_merged']}</span>
                <span class="stat-label">IETF Modules</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">{stats['total_paths']}</span>
                <span class="stat-label">API Paths</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">{stats['total_schemas']}</span>
                <span class="stat-label">Data Schemas</span>
            </div>
        </div>
        <a href="index.html" class="back-link">← Back to IETF Model Index</a>
    </div>

    <div id="swagger-ui"></div>

    <script src="../swagger-ui-5.11.0/dist/swagger-ui-bundle.js"></script>
    <script src="../swagger-ui-5.11.0/dist/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "api/all-ietf.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 3,
                docExpansion: "list",
                filter: true,
                tagsSorter: "alpha",
                operationsSorter: "alpha"
            }});

            window.ui = ui;
        }}
    </script>
</body>
</html>
"""

    output_path = script_dir.parent / 'swagger-ietf-model' / 'all-ietf.html'
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Generated HTML: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 60)
    print("Generating Combined IETF Model Specification")
    print("=" * 60)

    # Generate combined JSON
    json_file, stats = generate_combined_ietf()

    # Generate HTML page
    html_file = generate_html_page(stats)

    print("\n✅ IETF combined view generation complete!")
    print(f"   View at: http://localhost:3004/swagger-ietf-model/all-ietf.html")
