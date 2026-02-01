#!/usr/bin/env python3
"""Generate OpenAPI specs for Cisco IOS-XE Events YANG modules"""

import json
import re
from pathlib import Path

script_dir = Path(__file__).parent
yang_dir = script_dir.parent / 'references' / '17181-YANG-modules'
output_dir = script_dir.parent / 'swagger-events-model' / 'api'
output_dir.mkdir(parents=True, exist_ok=True)

print("\n🔧 IOS-XE Events YANG to OpenAPI Generator")
print("=" * 60)

# Include both *-events.yang and *-events-oper.yang patterns
events_files = []
events_files.extend(yang_dir.glob("Cisco-IOS-XE-*-events.yang"))
events_files.extend(yang_dir.glob("Cisco-IOS-XE-*-events-oper.yang"))
events_files = sorted(set(events_files))  # Remove duplicates and sort
print(f"Found {len(events_files)} Events modules")
print()

specs_created = []

for yang_file in events_files:
    module_name = yang_file.stem
    print(f"  ✓ Processing: {module_name}")
    
    # Read YANG content
    with open(yang_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract description
    desc_match = re.search(r'description\s+"([^"]+)"', content)
    description = desc_match.group(1).strip() if desc_match else f"Event notifications for {module_name}"
    
    # Remove copyright if present
    if 'Copyright' in description:
        description = description.split('Copyright')[0].strip()
    
    # Generate OpenAPI spec for telemetry events
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": f"Events - {module_name.replace('Cisco-IOS-XE-', '').replace('-events', '')}",
            "version": "17.18.1",
            "description": f"{description}\n\n"
                          "**Event Notifications Module** - Used for model-driven telemetry and streaming subscriptions.\n\n"
                          "**Usage**: Subscribe to events via NETCONF/RESTCONF subscriptions\n\n"
                          "**Protocol**: RFC 8639 (Subscription to YANG Notifications)\n\n"
                          "**Authentication**: HTTP Basic Authentication"
        },
        "servers": [{
            "url": "https://{device}/restconf",
            "variables": {"device": {"default": "sandbox-iosxe-latest-1.cisco.com"}}
        }],
        "paths": {
            f"/data/{module_name}:events": {
                "get": {
                    "summary": f"Get {module_name} event subscriptions",
                    "description": f"Retrieve active event subscriptions for {module_name}",
                    "tags": ["events"],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/yang-data+json": {
                                    "example": {
                                        f"{module_name}:events": {
                                            "description": "Event notification stream"
                                        }
                                    }
                                }
                            }
                        },
                        "401": {"description": "Unauthorized"}
                    }
                }
            },
            "/operations/ietf-subscribed-notifications:establish-subscription": {
                "post": {
                    "summary": "Create event subscription",
                    "description": f"Establish a subscription to {module_name} events",
                    "tags": ["events"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/yang-data+json": {
                                "example": {
                                    "input": {
                                        "stream": f"{module_name}:events",
                                        "encoding": "encode-json",
                                        "update-trigger": "periodic",
                                        "period": 6000
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Subscription created",
                            "content": {
                                "application/yang-data+json": {
                                    "example": {
                                        "output": {
                                            "subscription-id": 12345
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "basicAuth": {"type": "http", "scheme": "basic"}
            }
        },
        "security": [{"basicAuth": []}],
        "tags": [
            {
                "name": "events",
                "description": "Model-driven telemetry event subscriptions"
            }
        ]
    }
    
    # Save spec
    output_file = output_dir / f"{module_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    specs_created.append({"name": module_name, "file": f"{module_name}.json"})

# Create manifest
manifest = {
    "title": "Cisco IOS-XE Event Notifications",
    "description": "Event notification modules for model-driven telemetry",
    "total_modules": len(specs_created),
    "modules": specs_created
}

with open(output_dir / "manifest.json", 'w') as f:
    json.dump(manifest, f, indent=2)

print(f"\n✅ Generated {len(specs_created)} Events module specifications")
print(f"📂 Output: {output_dir}")
print("=" * 60)
