#!/usr/bin/env python3
"""
Generate combined Native Config model OpenAPI specification.
Merges all 10 category specifications into a single unified spec.
"""

import json
from pathlib import Path

script_dir = Path(__file__).parent

def generate_combined_native():
    """Generate all-native.json combining all category specs."""

    base_path = script_dir.parent / 'swagger-native-config-model' / 'api'

    categories = [
        "native-interfaces",
        "native-routing",
        "native-security",
        "native-switching",
        "native-services",
        "native-qos",
        "native-mpls",
        "native-vpn",
        "native-wireless",
        "native-system"
    ]

    # Base combined spec
    combined = {
        "openapi": "3.0.0",
        "info": {
            "title": "Cisco IOS-XE Native Configuration Model - All Categories",
            "description": """Complete Native Configuration Model combining all 10 feature categories.

This unified specification provides access to the entire Cisco-IOS-XE-native YANG model organized by functional areas:

**Categories:**
- **Interfaces**: Physical and logical interface configuration
- **Routing**: Static routes, routing protocols (OSPF, BGP, EIGRP, RIP)
- **Security**: ACLs, AAA, crypto, zone-based firewall, trustsec
- **Switching**: VLANs, STP, port-channel, QinQ, private VLANs
- **Services**: DHCP, DNS, NTP, logging, SNMP, NetFlow
- **QoS**: Classification, policing, shaping, queuing, WRED
- **MPLS**: LDP, RSVP, VPN, traffic engineering
- **VPN**: L2VPN, L3VPN, VPLS, pseudowire, EVPN
- **Wireless**: WLAN, mobility, radio, AP configuration
- **System**: Global settings, banners, users, hostname, boot

**Base Model:** Cisco-IOS-XE-native.yang (IOS-XE 17.18.1)
**Total Operations:** ~50+ configuration endpoints
**Device Support:** Catalyst, ASR, CSR, ISR platforms

**RESTCONF Base URL:** https://10.85.134.65/restconf/data/Cisco-IOS-XE-native:native
**Authentication:** Basic Auth (admin/EN-TME-Cisco123)
""",
            "version": "17.18.1",
            "contact": {
                "name": "Cisco IOS-XE YANG Model Documentation",
                "url": "https://github.com/YangModels/yang/tree/main/vendor/cisco/xe"
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
        "categories_merged": 0
    }

    # Merge each category
    for category in categories:
        spec_file = base_path / f"{category}.json"

        if not spec_file.exists():
            print(f"⚠️  Warning: {category}.json not found, skipping")
            continue

        with open(spec_file, 'r') as f:
            spec = json.load(f)

        # Merge paths
        if "paths" in spec:
            for path, methods in spec["paths"].items():
                combined["paths"][path] = methods
                stats["total_paths"] += 1

        # Merge schemas
        if "components" in spec and "schemas" in spec["components"]:
            for schema_name, schema_def in spec["components"]["schemas"].items():
                combined["components"]["schemas"][schema_name] = schema_def
                stats["total_schemas"] += 1

        # Add tag
        category_name = category.replace("native-", "").replace("-", " ").title()
        combined["tags"].append({
            "name": category_name,
            "description": f"Native {category_name} configuration"
        })

        stats["categories_merged"] += 1
        print(f"✅ Merged {category}: {len(spec.get('paths', {}))} paths, {len(spec.get('components', {}).get('schemas', {}))} schemas")

    # Write combined spec
    output_file = base_path / "all-native.json"
    with open(output_file, 'w') as f:
        json.dump(combined, f, indent=2)

    print(f"\n📊 Combined Native Model Statistics:")
    print(f"   Categories Merged: {stats['categories_merged']}/10")
    print(f"   Total Paths: {stats['total_paths']}")
    print(f"   Total Schemas: {stats['total_schemas']}")
    print(f"   Output: {output_file}")

    return output_file

def generate_html_page():
    """Generate all-native.html Swagger UI page."""

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IOS-XE Native Config - All Categories</title>
    <link rel="stylesheet" type="text/css" href="../swagger-ui-5.11.0/dist/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .header {
            background: linear-gradient(135deg, #1e88e5 0%, #1565c0 100%);
            color: white;
            padding: 30px 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 300;
        }

        .header p {
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }

        .stats {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .stat-box {
            background: rgba(255,255,255,0.2);
            padding: 15px 25px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }

        .stat-number {
            font-size: 2em;
            font-weight: bold;
            display: block;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        #swagger-ui {
            max-width: 1400px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }

        .swagger-ui .topbar {
            display: none;
        }

        .swagger-ui .info .title {
            color: #1e88e5;
        }

        .back-link {
            display: inline-block;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            margin-top: 15px;
            transition: background 0.3s;
        }

        .back-link:hover {
            background: rgba(255,255,255,0.3);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 IOS-XE Native Configuration Model</h1>
        <p>Complete unified specification - All 10 feature categories</p>
        <div class="stats">
            <div class="stat-box">
                <span class="stat-number">10</span>
                <span class="stat-label">Categories</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">~50+</span>
                <span class="stat-label">Configuration Endpoints</span>
            </div>
            <div class="stat-box">
                <span class="stat-number">17.18.1</span>
                <span class="stat-label">IOS-XE Version</span>
            </div>
        </div>
        <a href="index.html" class="back-link">← Back to Native Model Index</a>
    </div>

    <div id="swagger-ui"></div>

    <script src="../swagger-ui-5.11.0/dist/swagger-ui-bundle.js"></script>
    <script src="../swagger-ui-5.11.0/dist/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "api/all-native.json",
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
            });

            window.ui = ui;
        }
    </script>
</body>
</html>
"""

    output_path = script_dir.parent / 'swagger-native-config-model' / 'all-native.html'
    with open(output_path, 'w') as f:
        f.write(html_content)

    print(f"✅ Generated HTML: {output_path}")
    return output_path

if __name__ == "__main__":
    print("=" * 60)
    print("Generating Combined Native Configuration Model")
    print("=" * 60)

    # Generate combined JSON
    json_file = generate_combined_native()

    # Generate HTML page
    html_file = generate_html_page()

    print("\n✅ Native combined view generation complete!")
    print(f"   View at: http://localhost:3004/swagger-native-config-model/all-native.html")
