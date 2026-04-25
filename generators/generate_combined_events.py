#!/usr/bin/env python3
"""
Generate combined Events/Telemetry model OpenAPI specification.
Merges all 32 event notification module specifications into a single unified spec.
"""

import json
from pathlib import Path

script_dir = Path(__file__).parent

def generate_combined_events():
    """Generate all-events.json combining all event module specs."""

    base_path = script_dir.parent / 'swagger-events-model' / 'api'

    # Base combined spec
    combined = {
        "openapi": "3.0.0",
        "info": {
            "title": "IOS-XE Event Notifications & Telemetry - All Modules",
            "description": """Complete Event/Telemetry model collection for IOS-XE 17.18.1.

This unified specification combines all 32 event notification and telemetry modules for real-time network monitoring.

**Event Categories:**
- **Interface Events**: Link up/down, status changes, errors
- **Routing Events**: Neighbor changes, route updates, protocol events
- **System Events**: CPU, memory, temperature, power, environment
- **Security Events**: Authentication, authorization, policy violations
- **Service Events**: DHCP, QoS, NAT, multicast
- **Protocol Events**: BGP, OSPF, EIGRP, STP notifications

**Telemetry Capabilities:**
- **Model-Driven Telemetry (MDT)**: Streaming operational data
- **Event Subscriptions**: YANG-Push, NETCONF notifications
- **On-Change Updates**: Real-time state change notifications
- **Periodic Sampling**: Configurable interval-based telemetry

**Key Event Modules:**
- Cisco-IOS-XE-process-cpu-oper: CPU utilization events
- Cisco-IOS-XE-interfaces-oper-events: Interface state changes
- Cisco-IOS-XE-environment-oper-events: Environmental monitoring
- Cisco-IOS-XE-bgp-events-oper: BGP session notifications
- Cisco-IOS-XE-memory-events-oper: Memory threshold alerts

**Subscription Methods:**
- NETCONF: &lt;establish-subscription&gt; RPC
- RESTCONF: POST to /operations/establish-subscription
- gRPC: Dial-out telemetry subscriptions

**Total Modules:** 32 event/telemetry modules
**Base URL:** https://10.85.134.65/restconf/data
**Authentication:** Basic Auth (admin/EN-TME-Cisco123)
""",
            "version": "17.18.1",
            "contact": {
                "name": "Cisco IOS-XE Telemetry Documentation",
                "url": "https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1612/b_1612_programmability_cg/model_driven_telemetry.html"
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
                        if f.name not in ["manifest.json", "all-events.json"]])

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

        # Add tag - extract meaningful name
        tag_name = module_name.replace("Cisco-IOS-XE-", "").replace("-oper", "").replace("-events", "").replace("-", " ").title()
        combined["tags"].append({
            "name": tag_name,
            "description": f"{tag_name} event notifications and telemetry"
        })

        stats["modules_merged"] += 1
        print(f"✅ Merged {module_name}: {paths_count} paths, {schemas_count} schemas")

    # Write combined spec
    output_file = base_path / "all-events.json"
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n📊 Combined Events Model Statistics:")
    print(f"   Modules Merged: {stats['modules_merged']}")
    print(f"   Total Paths: {stats['total_paths']}")
    print(f"   Total Schemas: {stats['total_schemas']}")
    print(f"   Output: {output_file}")

    return output_file, stats

def generate_html_page(stats):
    """Generate all-events.html Swagger UI page."""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IOS-XE Events & Telemetry - All Modules</title>
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
        <h1>📡 IOS-XE Event Notifications & Telemetry</h1>
        <p>Complete unified specification - All {stats['modules_merged']} event modules</p>
        <div class="stats">
            <div class="stat-box">
                <span class="stat-number">{stats['modules_merged']}</span>
                <span class="stat-label">Event Modules</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">{stats['total_paths']}</span>
                <span class="stat-label">Telemetry Paths</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">{stats['total_schemas']}</span>
                <span class="stat-label">Event Schemas</span>
            </div>
        </div>
        <a href="index.html" class="back-link">← Back to Events Model Index</a>
    </div>

    <div id="swagger-ui"></div>

    <script src="../swagger-ui-5.11.0/dist/swagger-ui-bundle.js"></script>
    <script src="../swagger-ui-5.11.0/dist/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "api/all-events.json",
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

    output_path = script_dir.parent / 'swagger-events-model' / 'all-events.html'
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Generated HTML: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 60)
    print("Generating Combined Events/Telemetry Model")
    print("=" * 60)

    # Generate combined JSON
    json_file, stats = generate_combined_events()

    # Generate HTML page
    html_file = generate_html_page(stats)

    print("\n✅ Events combined view generation complete!")
    print(f"   View at: http://localhost:3004/swagger-events-model/all-events.html")
