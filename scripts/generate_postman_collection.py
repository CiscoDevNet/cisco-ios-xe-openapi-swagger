"""
Generate a complete Postman v2.1 collection from all OpenAPI 3.0 specs.

Reads all 681 specs across 9 model folders and generates a single Postman
collection with every path/operation, organized into folders by model category
and YANG module. Uses the Postman environment variables for device/auth.

Output: tools/IOS-XE-RESTCONF-Complete.postman_collection.json
"""
import json
import glob
import os
import re
import uuid
import sys
from collections import OrderedDict

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WORKSPACE)

# Model folder display names and sort order
MODEL_DISPLAY = OrderedDict([
    ("swagger-cfg-model",            "1 - Configuration (cfg)"),
    ("swagger-native-config-model",  "2 - Native Configuration"),
    ("swagger-oper-model",           "3 - Operational (oper)"),
    ("swagger-ietf-model",           "4 - IETF Standards"),
    ("swagger-openconfig-model",     "5 - OpenConfig"),
    ("swagger-mib-model",            "6 - MIB (SNMP)"),
    ("swagger-rpc-model",            "7 - RPC Operations"),
    ("swagger-events-model",         "8 - Event Streams"),
    ("swagger-other-model",          "9 - Other"),
])

# HTTP method sort order
METHOD_ORDER = {"get": 0, "put": 1, "post": 2, "patch": 3, "delete": 4}


def make_id():
    """Generate a Postman-style UUID."""
    return str(uuid.uuid4())


def resolve_schema_example(schema, components, depth=0):
    """Generate a minimal example body from a schema reference."""
    if depth > 3:
        return {}

    if "$ref" in schema:
        ref = schema["$ref"]
        # e.g. "#/components/schemas/SomeName"
        parts = ref.split("/")
        if len(parts) >= 4 and parts[1] == "components" and parts[2] == "schemas":
            schema_name = parts[3]
            resolved = components.get("schemas", {}).get(schema_name, {})
            return resolve_schema_example(resolved, components, depth + 1)
        return {}

    schema_type = schema.get("type", "object")

    if schema_type == "object":
        props = schema.get("properties", {})
        example = {}
        for prop_name, prop_schema in list(props.items())[:10]:  # Limit to 10 props
            example[prop_name] = resolve_schema_example(prop_schema, components, depth + 1)
        return example
    elif schema_type == "array":
        items = schema.get("items", {})
        return [resolve_schema_example(items, components, depth + 1)]
    elif schema_type == "string":
        return schema.get("example", schema.get("default", "string"))
    elif schema_type == "integer":
        return schema.get("example", schema.get("default", 0))
    elif schema_type == "number":
        return schema.get("example", schema.get("default", 0.0))
    elif schema_type == "boolean":
        return schema.get("example", schema.get("default", True))
    else:
        return {}


def build_postman_request(method, path, operation, spec_data):
    """Convert an OpenAPI operation to a Postman request item."""
    method_upper = method.upper()
    summary = operation.get("summary", f"{method_upper} {path}")
    description = operation.get("description", summary)

    # Build URL from path
    # Replace {param} with :param for Postman path variables
    postman_path = re.sub(r'\{([^}]+)\}', r':\1', path)
    path_segments = [s for s in postman_path.split("/") if s]

    # Build path variables
    path_vars = []
    for match in re.finditer(r'\{([^}]+)\}', path):
        param_name = match.group(1)
        path_vars.append({
            "key": param_name,
            "value": "",
            "description": f"Path parameter: {param_name}"
        })

    # Build query parameters
    query_params = []
    for param in operation.get("parameters", []):
        if param.get("in") == "query":
            query_params.append({
                "key": param.get("name", ""),
                "value": "",
                "description": param.get("description", ""),
                "disabled": True
            })

    # Build headers (skip Accept/Content-Type, those come from collection defaults)
    headers = [
        {"key": "Accept", "value": "application/yang-data+json"},
    ]
    if method_upper in ("PUT", "POST", "PATCH"):
        headers.append({"key": "Content-Type", "value": "application/yang-data+json"})

    # Build request body for PUT/POST/PATCH
    body = None
    if method_upper in ("PUT", "POST", "PATCH"):
        rb = operation.get("requestBody", {})
        content = rb.get("content", {})
        yang_content = content.get("application/yang-data+json", {})
        schema = yang_content.get("schema", {})

        # Try to generate example body
        components = spec_data.get("components", {})
        example_body = resolve_schema_example(schema, components)

        body = {
            "mode": "raw",
            "raw": json.dumps(example_body, indent=2) if example_body else "{\n  \n}",
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }

    # Build the Postman request
    request = {
        "method": method_upper,
        "header": headers,
        "url": {
            "raw": "{{baseUrl}}" + path,
            "host": ["{{baseUrl}}"],
            "path": path_segments,
        },
        "description": description
    }

    if query_params:
        request["url"]["query"] = query_params

    if path_vars:
        request["url"]["variable"] = path_vars

    if body:
        request["body"] = body

    # Response examples
    responses = []
    for status_code, resp_detail in operation.get("responses", {}).items():
        resp_desc = resp_detail.get("description", "")
        responses.append({
            "name": f"{status_code} {resp_desc}",
            "status": resp_desc,
            "code": int(status_code) if status_code.isdigit() else 200,
            "_postman_previewlanguage": "json",
            "header": [],
            "body": ""
        })

    item = {
        "name": f"{method_upper} {summary}",
        "request": request,
    }

    if responses:
        item["response"] = responses

    return item


def process_spec(spec_path, spec_data):
    """Process a single OpenAPI spec into Postman folder items."""
    items = []
    paths = spec_data.get("paths", {})

    for path, methods in paths.items():
        # Sort methods: GET, PUT, POST, PATCH, DELETE
        sorted_methods = sorted(
            [(m, d) for m, d in methods.items() if m.lower() in METHOD_ORDER],
            key=lambda x: METHOD_ORDER.get(x[0].lower(), 99)
        )

        for method, operation in sorted_methods:
            item = build_postman_request(method, path, operation, spec_data)
            items.append(item)

    return items


def main():
    print("=" * 60)
    print("Postman Collection Generator")
    print("Cisco IOS-XE 17.18.1 RESTCONF - Complete")
    print("=" * 60)

    # Top-level collection structure
    collection = {
        "info": {
            "_postman_id": make_id(),
            "name": "Cisco IOS-XE 17.18.1 RESTCONF - Complete Collection",
            "description": (
                "Complete Postman collection for Cisco IOS-XE 17.18.1 RESTCONF APIs.\n\n"
                "**Auto-generated** from 681 OpenAPI 3.0 specs covering:\n"
                "- 13,840 RESTCONF endpoints\n"
                "- 24,734 operations (GET/PUT/POST/PATCH/DELETE)\n"
                "- 848 YANG modules across 9 categories\n\n"
                "**Setup:**\n"
                "1. Import the companion environment: `IOS-XE-RESTCONF.postman_environment.json`\n"
                "2. Set your device IP, username, and password in the environment\n"
                "3. Disable SSL certificate verification (Settings → General → SSL)\n\n"
                "**Authentication:** Uses Basic Auth from environment variables.\n\n"
                "**Source:** https://github.com/jeremycohoe/cisco-ios-xe-openapi-swagger"
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "basic",
            "basic": [
                {"key": "username", "value": "{{username}}", "type": "string"},
                {"key": "password", "value": "{{password}}", "type": "string"}
            ]
        },
        "event": [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": [
                        "// Disable SSL verification for self-signed certs",
                        "pm.request.headers.add({key: 'Accept', value: 'application/yang-data+json'});"
                    ]
                }
            }
        ],
        "variable": [
            {"key": "baseUrl", "value": "https://{{device}}:{{port}}/restconf", "type": "string"}
        ],
        "item": []
    }

    total_specs = 0
    total_paths = 0
    total_ops = 0

    for folder, display_name in MODEL_DISPLAY.items():
        spec_files = sorted(glob.glob(os.path.join(folder, "api", "*.json")))
        if not spec_files:
            continue

        folder_items = []
        folder_paths = 0
        folder_ops = 0

        for spec_path in spec_files:
            try:
                spec_data = json.load(open(spec_path, "r", encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"  WARN: Skipping {spec_path}: {e}")
                continue

            info = spec_data.get("info", {})
            yang_module = info.get("x-yang-module", os.path.splitext(os.path.basename(spec_path))[0])
            title = info.get("title", yang_module)
            spec_desc = info.get("description", "")

            paths = spec_data.get("paths", {})
            if not paths:
                continue

            # Build items for this spec
            items = process_spec(spec_path, spec_data)

            if not items:
                continue

            path_count = len(paths)
            op_count = len(items)
            folder_paths += path_count
            folder_ops += op_count
            total_specs += 1

            # Create a sub-folder for this YANG module
            module_folder = {
                "name": yang_module,
                "description": f"{title}\n\n{spec_desc[:500] if spec_desc else ''}\n\nEndpoints: {path_count} | Operations: {op_count}",
                "item": items
            }
            folder_items.append(module_folder)

        if folder_items:
            # Create top-level model category folder
            category_folder = {
                "name": display_name,
                "description": f"{len(folder_items)} YANG modules | {folder_paths} endpoints | {folder_ops} operations",
                "item": folder_items
            }
            collection["item"].append(category_folder)

            total_paths += folder_paths
            total_ops += folder_ops
            print(f"  {display_name}: {len(folder_items)} modules, {folder_paths} paths, {folder_ops} ops")

    # Write collection
    output_path = os.path.join("tools", "IOS-XE-RESTCONF-Complete.postman_collection.json")
    os.makedirs("tools", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path)
    print(f"\n{'=' * 60}")
    print(f"Collection written: {output_path}")
    print(f"  Specs processed: {total_specs}")
    print(f"  Total paths:     {total_paths}")
    print(f"  Total operations:{total_ops}")
    print(f"  File size:       {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    print(f"  Model folders:   {len(collection['item'])}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
