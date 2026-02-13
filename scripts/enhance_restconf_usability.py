#!/usr/bin/env python3
"""
Enhance all OpenAPI specs for Postman/Bruno RESTCONF usability.

Adds:
1. RESTCONF headers (Accept + Content-Type) on every operation
2. RESTCONF query parameters (depth, fields, content) on GET operations
3. Standard ietf-restconf:errors response schema for error codes
4. Reusable components (parameters, headers, schemas) for the above

This makes imported Postman/Bruno collections "just work" without
needing manual header/param setup.
"""

import json
import os
import sys
import glob

# ─── Reusable component definitions ───

RESTCONF_ERROR_SCHEMA = {
    "restconf-error": {
        "type": "object",
        "description": "Standard RESTCONF error response (RFC 8040 Section 7.1)",
        "properties": {
            "ietf-restconf:errors": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "error-type": {
                                    "type": "string",
                                    "enum": ["transport", "rpc", "protocol", "application"],
                                    "description": "Layer where the error occurred"
                                },
                                "error-tag": {
                                    "type": "string",
                                    "description": "Enumerated error tag (e.g. invalid-value, data-missing, access-denied)"
                                },
                                "error-severity": {
                                    "type": "string",
                                    "enum": ["error", "warning"],
                                    "description": "Error severity"
                                },
                                "error-app-tag": {
                                    "type": "string",
                                    "description": "Application-specific error tag"
                                },
                                "error-path": {
                                    "type": "string",
                                    "description": "YANG instance-identifier of the error node"
                                },
                                "error-message": {
                                    "type": "string",
                                    "description": "Human-readable error description"
                                }
                            },
                            "required": ["error-type", "error-tag"]
                        }
                    }
                }
            }
        },
        "example": {
            "ietf-restconf:errors": {
                "error": [
                    {
                        "error-type": "protocol",
                        "error-tag": "invalid-value",
                        "error-severity": "error",
                        "error-message": "Invalid input parameter"
                    }
                ]
            }
        }
    }
}

# Query parameters for GET operations
GET_QUERY_PARAMS = [
    {
        "name": "depth",
        "in": "query",
        "required": False,
        "description": "Limit the depth of returned sub-tree data (RFC 8040 Section 4.8.2). Use 'unbounded' for full depth.",
        "schema": {
            "type": "string",
            "default": "unbounded"
        }
    },
    {
        "name": "fields",
        "in": "query",
        "required": False,
        "description": "Select specific fields to return (RFC 8040 Section 4.8.3). Example: fields=name;status",
        "schema": {
            "type": "string"
        }
    },
    {
        "name": "content",
        "in": "query",
        "required": False,
        "description": "Filter by config state: 'config' (config true only), 'nonconfig' (config false only), or 'all'.",
        "schema": {
            "type": "string",
            "enum": ["config", "nonconfig", "all"],
            "default": "all"
        }
    }
]

# RESTCONF Accept header for responses
ACCEPT_HEADER_PARAM = {
    "name": "Accept",
    "in": "header",
    "required": False,
    "description": "RESTCONF response media type (RFC 8040)",
    "schema": {
        "type": "string",
        "default": "application/yang-data+json",
        "enum": [
            "application/yang-data+json",
            "application/yang-data+xml"
        ]
    }
}

# RESTCONF Content-Type header for request bodies
CONTENT_TYPE_HEADER_PARAM = {
    "name": "Content-Type",
    "in": "header",
    "required": False,
    "description": "RESTCONF request body media type (RFC 8040)",
    "schema": {
        "type": "string",
        "default": "application/yang-data+json",
        "enum": [
            "application/yang-data+json",
            "application/yang-data+xml"
        ]
    }
}


def has_param(params_list, param_name, param_in):
    """Check if a parameter already exists in the list."""
    for p in params_list:
        if p.get("name") == param_name and p.get("in") == param_in:
            return True
    return False


def enhance_spec(spec):
    """Enhance a single OpenAPI spec with RESTCONF usability improvements."""
    stats = {
        "accept_headers_added": 0,
        "content_type_headers_added": 0,
        "query_params_added": 0,
        "error_responses_added": 0,
        "error_schema_added": False
    }

    paths = spec.get("paths", {})
    if not paths:
        return stats

    needs_error_schema = False

    for path_key, path_obj in paths.items():
        for method in ["get", "post", "put", "patch", "delete"]:
            if method not in path_obj:
                continue

            op = path_obj[method]

            # Ensure parameters array exists
            if "parameters" not in op:
                op["parameters"] = []

            # 1. Add Accept header to ALL operations
            if not has_param(op["parameters"], "Accept", "header"):
                op["parameters"].append(ACCEPT_HEADER_PARAM)
                stats["accept_headers_added"] += 1

            # 2. Add Content-Type header to write operations (POST/PUT/PATCH)
            if method in ("post", "put", "patch"):
                if not has_param(op["parameters"], "Content-Type", "header"):
                    op["parameters"].append(CONTENT_TYPE_HEADER_PARAM)
                    stats["content_type_headers_added"] += 1

            # 3. Add query params to GET operations
            if method == "get":
                for qp in GET_QUERY_PARAMS:
                    if not has_param(op["parameters"], qp["name"], "query"):
                        op["parameters"].append(qp)
                        stats["query_params_added"] += 1

            # 4. Enhance error responses with RESTCONF error schema ref
            responses = op.get("responses", {})
            error_codes_to_enhance = {
                "400": "Bad request — invalid input or constraint violation",
                "401": "Unauthorized — authentication required (HTTP Basic)",
                "403": "Forbidden — insufficient access rights (NACM)",
                "404": "Resource not found — the target resource does not exist",
                "405": "Method not allowed",
                "409": "Conflict — resource already exists or lock conflict"
            }

            for code, desc in error_codes_to_enhance.items():
                if code in responses:
                    resp = responses[code]
                    # Only enhance if no content/schema yet
                    if "content" not in resp:
                        resp["description"] = desc
                        resp["content"] = {
                            "application/yang-data+json": {
                                "schema": {
                                    "$ref": "#/components/schemas/restconf-error"
                                }
                            }
                        }
                        stats["error_responses_added"] += 1
                        needs_error_schema = True

            # Add 403 (NACM) if not present on any operation
            if "403" not in responses:
                responses["403"] = {
                    "description": "Forbidden — insufficient access rights (NACM)",
                    "content": {
                        "application/yang-data+json": {
                            "schema": {
                                "$ref": "#/components/schemas/restconf-error"
                            }
                        }
                    }
                }
                stats["error_responses_added"] += 1
                needs_error_schema = True

    # 5. Add error schema to components if needed
    if needs_error_schema:
        if "components" not in spec:
            spec["components"] = {}
        if "schemas" not in spec["components"]:
            spec["components"]["schemas"] = {}
        if "restconf-error" not in spec["components"]["schemas"]:
            spec["components"]["schemas"]["restconf-error"] = RESTCONF_ERROR_SCHEMA["restconf-error"]
            stats["error_schema_added"] = True

    return stats


def process_folder(folder_path):
    """Process all JSON spec files in a folder."""
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    # Exclude manifest.json
    json_files = [f for f in json_files if os.path.basename(f) != "manifest.json"]

    folder_stats = {
        "files_processed": 0,
        "accept_headers_added": 0,
        "content_type_headers_added": 0,
        "query_params_added": 0,
        "error_responses_added": 0,
        "error_schemas_added": 0
    }

    for filepath in sorted(json_files):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"  SKIP {os.path.basename(filepath)}: {e}")
            continue

        stats = enhance_spec(spec)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write("\n")

        folder_stats["files_processed"] += 1
        folder_stats["accept_headers_added"] += stats["accept_headers_added"]
        folder_stats["content_type_headers_added"] += stats["content_type_headers_added"]
        folder_stats["query_params_added"] += stats["query_params_added"]
        folder_stats["error_responses_added"] += stats["error_responses_added"]
        if stats["error_schema_added"]:
            folder_stats["error_schemas_added"] += 1

    return folder_stats


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    model_folders = [
        "swagger-oper-model",
        "swagger-cfg-model",
        "swagger-rpc-model",
        "swagger-events-model",
        "swagger-native-config-model",
        "swagger-openconfig-model",
        "swagger-ietf-model",
        "swagger-mib-model",
        "swagger-other-model"
    ]

    totals = {
        "files_processed": 0,
        "accept_headers_added": 0,
        "content_type_headers_added": 0,
        "query_params_added": 0,
        "error_responses_added": 0,
        "error_schemas_added": 0
    }

    print("=" * 65)
    print("  RESTCONF Usability Enhancement for Postman/Bruno")
    print("=" * 65)
    print()

    for folder_name in model_folders:
        api_path = os.path.join(base_dir, folder_name, "api")
        if not os.path.isdir(api_path):
            print(f"  SKIP {folder_name}/api — not found")
            continue

        stats = process_folder(api_path)
        print(f"  {folder_name}: {stats['files_processed']} specs | "
              f"+{stats['accept_headers_added']} Accept | "
              f"+{stats['content_type_headers_added']} Content-Type | "
              f"+{stats['query_params_added']} query params | "
              f"+{stats['error_responses_added']} error responses | "
              f"+{stats['error_schemas_added']} error schemas")

        for key in totals:
            totals[key] += stats[key]

    print()
    print("-" * 65)
    print(f"  TOTAL: {totals['files_processed']} specs enhanced")
    print(f"    Accept headers added:       {totals['accept_headers_added']}")
    print(f"    Content-Type headers added:  {totals['content_type_headers_added']}")
    print(f"    GET query params added:      {totals['query_params_added']}")
    print(f"    Error responses enhanced:    {totals['error_responses_added']}")
    print(f"    Error schemas added:         {totals['error_schemas_added']}")
    print("-" * 65)


if __name__ == "__main__":
    main()
