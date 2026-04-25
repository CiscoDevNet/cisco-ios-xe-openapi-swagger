#!/usr/bin/env python3
"""
Enrich v2 deep-path OpenAPI specs with production-realistic examples,
operation descriptions, and property descriptions.

Targets all 9 api-v2/ directories. Replaces placeholder "example" string
values and generic integers with field-name-matched realistic values.
"""

import json
import os
import re
from pathlib import Path


# ── Field-name to example value mapping ──────────────────────────────────────

def get_example_for_field(field_name, module_name=""):
    """Return a realistic example value based on field/property name."""
    fl = field_name.lower().replace("_", "-")
    ml = module_name.lower()

    # ── IP / Network ─────────────────────────────────────────────────────
    if fl in ("ip", "ip-address", "ipaddress", "address", "source-address",
              "destination-address", "src-addr", "dst-addr", "peer-address",
              "remote-address", "local-address", "host", "server",
              "neighbor-address", "next-hop", "gateway", "router-id",
              "neighbor-id", "source-ip", "destination-ip"):
        return "10.1.1.1"
    if "ipv6" in fl or fl == "ipv6-address":
        return "2001:db8::1"
    if fl in ("mac", "mac-address", "bssid", "wtp-mac", "source-mac",
              "destination-mac", "hw-addr", "hardware-address"):
        return "00:1a:2b:3c:4d:5e"
    if fl in ("prefix", "ip-prefix", "network", "route-filter", "aggregate"):
        return "10.0.0.0/24"
    if fl in ("netmask", "subnet-mask", "mask"):
        return "255.255.255.0"
    if fl in ("prefix-length", "prefix-len", "mask-length"):
        return 24

    # ── Interface ────────────────────────────────────────────────────────
    if fl in ("interface", "interface-name", "if-name", "port-name"):
        return "GigabitEthernet1/0/1"
    if fl in ("intf", "ifname"):
        return "Gi1/0/1"
    if fl in ("mtu", "ip-mtu"):
        return 1500
    if fl in ("speed",):
        return 1000
    if fl in ("duplex",):
        return "full"
    if fl in ("bandwidth",):
        return 1000000000

    # ── VLAN / VRF ───────────────────────────────────────────────────────
    if fl in ("vlan-id", "vlan", "dot1q-id"):
        return 100
    if fl in ("vlan-name",):
        return "DATA_VLAN"
    if fl in ("vrf", "vrf-name", "rd"):
        return "default"

    # ── Routing / BGP / OSPF ─────────────────────────────────────────────
    if fl in ("as-number", "asn", "local-as", "remote-as", "peer-as"):
        return 65001
    if fl in ("area", "area-id", "ospf-area"):
        return "0.0.0.0"
    if "bgp" in fl and "state" in fl:
        return "Established"
    if "ospf" in fl and "state" in fl:
        return "Full"
    if fl in ("route-distinguisher", "rd"):
        return "65000:1"
    if fl in ("route-target", "rt"):
        return "65000:100"
    if fl in ("community",):
        return "65000:200"
    if fl in ("metric", "cost"):
        return 10
    if fl in ("preference", "admin-distance", "distance"):
        return 110
    if fl in ("weight",):
        return 32768
    if fl in ("local-preference", "local-pref"):
        return 100
    if fl in ("med", "multi-exit-disc"):
        return 0
    if fl in ("origin",):
        return "igp"
    if fl in ("next-hop-self",):
        return True
    if fl in ("afi", "afi-safi", "address-family"):
        return "ipv4-unicast"

    # ── AAA / Authentication ─────────────────────────────────────────────
    if fl in ("username", "user", "user-name", "login"):
        return "admin"
    if fl in ("password", "secret", "passwd"):
        return "***"
    if fl in ("group-name", "server-group"):
        return "RADIUS-GROUP"
    if fl in ("auth-type", "authentication-type"):
        return "local"
    if fl in ("auth-result",):
        return "Success"
    if fl in ("method",):
        return "local"
    if fl in ("role", "privilege-level"):
        return 15
    if fl in ("access-level",):
        return "read-write"

    # ── ACL / Security ───────────────────────────────────────────────────
    if fl in ("acl-name", "access-list", "acl"):
        return "ACL-PERMIT-ALL"
    if fl in ("rule", "sequence", "sequence-number", "seq"):
        return 10
    if fl in ("action",) and "acl" in ml:
        return "permit"
    if fl in ("protocol",):
        return "tcp"
    if fl in ("port", "port-number", "src-port", "dst-port"):
        return 443
    if fl in ("direction",):
        return "inbound"

    # ── Counters / Statistics ────────────────────────────────────────────
    if "packet" in fl and any(w in fl for w in ("in", "rx", "receive", "input")):
        return 12845632
    if "packet" in fl and any(w in fl for w in ("out", "tx", "transmit", "output")):
        return 10234567
    if "byte" in fl and any(w in fl for w in ("in", "rx", "receive", "input")):
        return 1284563200
    if "byte" in fl and any(w in fl for w in ("out", "tx", "transmit", "output")):
        return 1023456700
    if "error" in fl or "crc" in fl or "collision" in fl:
        return 0
    if "drop" in fl or "discard" in fl:
        return 0

    # ── Hardware / Platform ──────────────────────────────────────────────
    if fl in ("serial-number", "serial", "sn"):
        return "FOC2145L0QS"
    if fl in ("pid", "product-id", "model"):
        return "C9300-48P"
    if fl in ("version", "sw-version", "software-version", "ios-version"):
        return "17.18.1"
    if fl in ("hostname", "sysname", "device-name"):
        return "Router1"
    if fl in ("location", "sysLocation", "physical-location"):
        return "San Jose, CA"
    if fl in ("contact", "sysContact"):
        return "noc@example.com"
    if fl in ("sys-descr", "system-description", "sysDescr"):
        return "Cisco IOS-XE Software, Catalyst 9300"

    # ── Uptime / Timestamps ──────────────────────────────────────────────
    if "uptime" in fl or "up-time" in fl:
        return 651780
    if "timestamp" in fl or "last-updated" in fl or "last-change" in fl:
        return "2025-03-15T10:30:45Z"
    if "date" in fl and "time" not in fl:
        return "2025-03-15"
    if "time" in fl and "stamp" not in fl and "date" not in fl:
        return "10:30:45"

    # ── Environment ──────────────────────────────────────────────────────
    if "temperature" in fl or "temp" in fl:
        return 45
    if "fan" in fl and ("speed" in fl or "rpm" in fl):
        return 3200
    if "power" in fl and ("watt" in fl or "consumption" in fl):
        return 125.5
    if "voltage" in fl:
        return 12.1
    if "current" in fl and "amp" in fl:
        return 10.4

    # ── CPU / Memory ─────────────────────────────────────────────────────
    if "cpu" in fl and ("usage" in fl or "util" in fl or "percent" in fl):
        return 5
    if "cpu" in fl and "load" in fl:
        return 0.05
    if "memory" in fl:
        if "total" in fl or "size" in fl:
            return 2048000000
        if "used" in fl:
            return 921600000
        if "free" in fl:
            return 1126400000
        if "percent" in fl or "usage" in fl:
            return 45

    # ── Wireless ─────────────────────────────────────────────────────────
    if fl in ("ssid",):
        return "Corporate-WiFi"
    if fl in ("channel", "channel-number"):
        return 36
    if fl in ("rssi",):
        return -55
    if fl in ("snr", "signal-to-noise"):
        return 35
    if "client" in fl and "count" in fl:
        return 45

    # ── QoS ──────────────────────────────────────────────────────────────
    if fl in ("class-name", "policy-name", "class-map"):
        return "CLASS-VOICE"
    if fl in ("policy-map", "service-policy"):
        return "PM-WAN-EDGE"
    if fl in ("queue-depth", "queue-size"):
        return 64
    if fl in ("rate", "bit-rate", "cir", "pir"):
        return 1000000
    if fl in ("burst", "bc", "be"):
        return 8000
    if fl in ("dscp",):
        return 46

    # ── SNMP / MIB ───────────────────────────────────────────────────────
    if fl in ("community-string", "community"):
        return "public"
    if fl in ("oid", "object-identifier"):
        return "1.3.6.1.2.1.1.1"
    if fl in ("trap-host", "trap-destination"):
        return "10.0.0.100"

    # ── Crypto / Certificates ────────────────────────────────────────────
    if fl in ("key-name", "keychain", "key-chain"):
        return "MY-KEY-CHAIN"
    if fl in ("algorithm",):
        return "hmac-sha-256"
    if fl in ("key-string", "keystring", "key"):
        return "***"
    if fl in ("lifetime",):
        return 3600
    if fl in ("key-id",):
        return 1

    # ── Logging / Monitoring ─────────────────────────────────────────────
    if fl in ("severity", "level"):
        return "informational"
    if fl in ("facility",):
        return "local7"
    if fl in ("message", "log-message"):
        return "Interface GigabitEthernet1/0/1 changed state to up"
    if fl in ("event-type",):
        return "interface-state-change"

    # ── Generic status/state ─────────────────────────────────────────────
    if fl in ("oper-status", "oper-state", "link-status"):
        return "up"
    if fl in ("admin-status", "admin-state"):
        return "up"
    if "status" in fl or "state" in fl:
        return "active"
    if fl in ("enabled", "enable", "active", "is-enabled"):
        return True
    if fl in ("disabled", "disable", "shutdown"):
        return False
    if fl in ("mode",):
        return "normal"
    if fl in ("type",):
        return "default"

    # ── Generic identifiers ──────────────────────────────────────────────
    if fl in ("name",):
        return "example-1"
    if fl in ("description", "desc", "remark"):
        return "Configured via RESTCONF"
    if fl in ("id",):
        return 1
    if fl in ("index",):
        return 0
    if fl in ("tag", "label"):
        return "production"
    if fl in ("priority",):
        return 100
    if fl in ("timeout",):
        return 30
    if fl in ("interval",):
        return 60
    if fl in ("retries", "retry-count"):
        return 3
    if fl in ("threshold",):
        return 80
    if fl in ("maximum", "max", "limit"):
        return 1000
    if fl in ("minimum", "min"):
        return 1
    if fl in ("size", "length"):
        return 256
    if fl in ("count", "num", "number"):
        return 10
    if fl in ("duration",):
        return 300
    if fl in ("value",):
        return "configured-value"
    if fl in ("reason",):
        return "administrative"
    if fl in ("result",):
        return "success"
    if fl in ("country",):
        return "US"
    if fl in ("day",):
        return "monday"

    # ── Fallback based on name patterns ──────────────────────────────────
    if "name" in fl:
        return "example-1"
    if "address" in fl:
        return "10.1.1.1"
    if "count" in fl or "num" in fl:
        return 10
    if "id" in fl:
        return 1
    if "percent" in fl or "ratio" in fl:
        return 50
    if "flag" in fl or "is-" in fl or "has-" in fl:
        return True
    if "list" in fl:
        return "item-1"
    if "path" in fl:
        return "/data/example"
    if "url" in fl or "uri" in fl:
        return "https://10.1.1.1/restconf"

    return "configured-value"


def build_example_from_schema(schema, module_name="", depth=0, max_depth=6):
    """Build a realistic example object by walking schema properties.

    Used when the top-level example is empty ({}) but the schema has
    properties defined. Recursively descends into nested objects and
    arrays, generating field-appropriate values via get_example_for_field().
    """
    if not isinstance(schema, dict) or depth > max_depth:
        return None

    schema_type = schema.get("type", "object")

    # Leaf types — return a single value
    if schema_type == "string":
        return schema.get("example") or "configured-value"
    if schema_type == "integer":
        ex = schema.get("example")
        return ex if isinstance(ex, int) and not isinstance(ex, bool) else 1
    if schema_type == "number":
        ex = schema.get("example")
        return ex if isinstance(ex, (int, float)) and not isinstance(ex, bool) else 1.0
    if schema_type == "boolean":
        return schema.get("example", True)

    # Array — build one example item
    if schema_type == "array":
        items_schema = schema.get("items", {})
        item = build_example_from_schema(items_schema, module_name, depth + 1, max_depth)
        return [item] if item is not None else []

    # Object — walk properties
    if schema_type == "object":
        props = schema.get("properties", {})
        if not props:
            return None  # can't derive structure without properties
        result = {}
        for prop_name, prop_schema in props.items():
            if not isinstance(prop_schema, dict):
                continue
            prop_type = prop_schema.get("type", "object")
            if prop_type in ("object", "array"):
                child = build_example_from_schema(prop_schema, module_name, depth + 1, max_depth)
                if child is not None:
                    result[prop_name] = child
                else:
                    # Empty object for nested objects without properties
                    result[prop_name] = {} if prop_type == "object" else []
            else:
                val = get_example_for_field(prop_name, module_name)
                result[prop_name] = convert_example(val, prop_type)
        return result if result else None

    return None


def convert_example(example, schema_type):
    """Convert example value to match the schema type."""
    if schema_type == "string":
        return str(example)
    if schema_type == "integer":
        if isinstance(example, bool):
            return 1
        if isinstance(example, (int, float)):
            return int(example)
        s = str(example).replace("-", "", 1)
        return int(example) if s.isdigit() else 1
    if schema_type == "number":
        if isinstance(example, (int, float)) and not isinstance(example, bool):
            return float(example)
        return 1.0
    if schema_type == "boolean":
        return bool(example)
    return example


# ── Operation description templates ──────────────────────────────────────────

METHOD_DESC = {
    "get":    "Retrieve {resource} from the device via RESTCONF.\n\nReturns the current operational or configuration state of this resource.",
    "put":    "Create or replace {resource} on the device.\n\nThis replaces the entire resource — any fields not included will be removed.",
    "post":   "Create {resource} on the device.\n\nAdds a new instance of this resource to the configuration.",
    "patch":  "Partially update {resource} on the device.\n\nOnly the fields included in the request body are modified; other fields remain unchanged.",
    "delete": "Remove {resource} from the device configuration.\n\nThis deletes the resource and all descendant data.",
}

RPC_DESC = "Execute the **{rpc_name}** RPC operation.\n\nSends a POST request to invoke this action on the device. " \
           "The request body contains input parameters; the response contains any output values."

NOTIFICATION_DESC = "Subscribe to **{name}** notifications.\n\n" \
                    "This event is delivered via YANG-Push or NETCONF notification subscription. " \
                    "In RESTCONF, use SSE (Server-Sent Events) to receive real-time updates."


# ── Property description templates ───────────────────────────────────────────

PROP_DESCRIPTIONS = {
    # Network
    "ip-address": "IPv4 address in dotted decimal notation",
    "ipv6-address": "IPv6 address",
    "mac-address": "MAC address in colon-separated hex notation",
    "prefix-length": "Subnet prefix length (0-128)",
    "netmask": "IPv4 subnet mask in dotted decimal",
    "interface": "Interface name (e.g., GigabitEthernet1/0/1)",
    "interface-name": "Interface name (e.g., GigabitEthernet1/0/1)",
    "mtu": "Maximum transmission unit in bytes",
    "bandwidth": "Interface bandwidth in bits per second",
    "speed": "Interface speed in Mbps",
    "duplex": "Interface duplex mode (full/half/auto)",
    "vlan-id": "VLAN identifier (1-4094)",
    "vrf": "VRF instance name",
    "vrf-name": "VRF instance name",
    # Routing
    "as-number": "BGP autonomous system number",
    "area-id": "OSPF area identifier",
    "metric": "Routing metric/cost value",
    "next-hop": "Next-hop IP address for this route",
    "route-distinguisher": "VPN route distinguisher (ASN:NN format)",
    "community": "BGP community string",
    # Device
    "hostname": "Device hostname",
    "serial-number": "Device serial number",
    "version": "Software version string",
    "uptime": "System uptime in seconds",
    "description": "User-configured description string",
    "name": "Unique identifier name",
    # Status
    "oper-status": "Current operational status (up/down)",
    "admin-status": "Administrative status (up/down)",
    "enabled": "Whether this feature is enabled",
    "status": "Current status",
    "state": "Current operational state",
    # Security
    "username": "Authentication username",
    "password": "Authentication password (encrypted)",
    "key-string": "Cryptographic key string",
    "acl-name": "Access control list name",
    "community-string": "SNMP community string",
    # Counters
    "id": "Unique numeric identifier",
    "index": "Numeric index value",
    "count": "Count value",
    "sequence": "Sequence number",
    "priority": "Priority value (higher = preferred)",
    "timeout": "Timeout duration in seconds",
    "interval": "Polling or update interval in seconds",
    "threshold": "Threshold trigger value",
    "severity": "Log severity level",
    "timestamp": "Event timestamp (ISO 8601)",
}


# ── Core enrichment functions ────────────────────────────────────────────────

def enrich_schema_examples(schema, module_name, path=""):
    """Recursively replace placeholder examples in schema properties."""
    if not isinstance(schema, dict):
        return 0
    changes = 0

    # Replace or add example on leaf properties
    if "type" in schema:
        field_name = path.rsplit("/", 1)[-1] if path else ""
        if field_name:
            new_val = get_example_for_field(field_name, module_name)
            typed_val = convert_example(new_val, schema["type"])
            cur = schema.get("example")
            # Replace placeholder "example" or missing examples
            if cur in (None, "example", "example-value", "string"):
                schema["example"] = typed_val
                changes += 1
            elif schema["type"] == "integer" and cur == 1 and typed_val != 1:
                schema["example"] = typed_val
                changes += 1
            elif schema["type"] == "boolean" and cur is True and isinstance(typed_val, bool):
                schema["example"] = typed_val
                changes += 1

    # Add property description if missing
    if "type" in schema and "description" not in schema:
        field_name = path.rsplit("/", 1)[-1] if path else ""
        desc = PROP_DESCRIPTIONS.get(field_name)
        if desc:
            schema["description"] = desc
            changes += 1

    # Recurse into properties
    for prop_name, prop_schema in schema.get("properties", {}).items():
        changes += enrich_schema_examples(prop_schema, module_name, f"{path}/{prop_name}")

    # Recurse into items (arrays)
    if "items" in schema:
        changes += enrich_schema_examples(schema["items"], module_name, f"{path}/items")

    # Recurse into composition
    for key in ("allOf", "anyOf", "oneOf"):
        for sub in schema.get(key, []):
            changes += enrich_schema_examples(sub, module_name, path)

    return changes


# ── Nested empty container fill mapping ──────────────────────────────────────
# Templates for common YANG containers that appear empty in generated examples.
# Keys match the JSON property name; values are the filled example content.

CONTAINER_FILL = {
    # OpenConfig state/config
    "state": {"enabled": True, "admin-status": "UP", "oper-status": "UP"},
    "config": {"enabled": True, "description": "Configured via RESTCONF"},

    # Interface features
    "switchport": {"mode": "access", "access": {"vlan": 100}},
    "switchport-conf": {"switchport": True},
    "switchport-config": {"switchport": True},
    "ip": {"address": {"primary": {"address": "10.1.1.1", "mask": "255.255.255.0"}}},
    "ipv6": {"address": {"prefix-list": [{"prefix": "2001:db8::1/64"}]}},
    "bfd": {"interval": 300, "min-rx": 300, "multiplier": 3},
    "standby": {"standby-list": [{"group-number": 1, "ip": {"address": "10.1.1.254"}}]},
    "trust": {"device": "cisco-phone"},
    "storm-control": {"broadcast": {"level": {"threshold": 80.0}}},
    "bandwidth": {"kilobits": 1000000},
    "backup": {"interface": {"GigabitEthernet": "1/0/2"}},
    "arp": {"timeout": 14400},
    "encapsulation": {"dot1Q": {"vlan-id": 100}},
    "flowcontrol": {"receive": "on", "send": "on"},
    "dampening": {"half-life-time": 15},
    "fair-queue": {"queue-limit": 64},
    "fair-queue-conf": {"fair-queue": True},
    "priority-queue": {"out": True},
    "keepalive-config": {"keepalive": True},
    "logging": {"event": {"link-status": True}},
    "mop": {"enabled": False},
    "mdix": {"auto": True},
    "domain": {"name": "example.com"},
    "source": {"address": "10.1.1.1"},

    # Routing protocols
    "mpls": {"ip": True},
    "isis": {"tag": "AREA-1"},
    "ospf": {"id": 1},
    "bgp": {"asn": 65001},

    # QoS / policy
    "interface_qos": {"output": {"policy-name": "QOS-POLICY"}},
    "rcv-queue": {"queue-limit": 40},

    # Redundancy / HA
    "redundancy": {"mode": "sso"},
    "uplink": {"name": "GigabitEthernet1/0/1"},

    # L2 protocols
    "l2protocol-tunnel": {"shutdown-threshold": 1000},
    "l2protocol": {"peer": {"cdp": True}},
    "cws-tunnel": {"in": True},
    "cemoudp": {"reserve": 64},
    "clns": {"mtu": 1500},

    # Misc interface
    "subscriber": {"activate": True},
    "access-session": {"port-control": "auto"},
    "peer": {"default": {"ip": {"address": "10.1.1.2"}}},
    "pm-path": {"name": "PM-1"},
    "stackwise-virtual": {"link": 1},
    "punt-control": {"punt-enable": True},
    "srlg": {"value": [100]},
    "history": {"size": 100},

    # Counters and thresholds
    "counters": {"in-octets": 0, "out-octets": 0, "in-errors": 0},
    "threshold": {"value": 80},
    "include": {"connected": True},
    "level": {"level-1": True},

    # Crypto / security
    "authentication": {"type": "md5", "key-chain": "KEY-1"},
    "authorization": {"exec": {"default": {"group": "tacacs+"}}},

    # Common presence containers
    "enable": True,
    "enabled": True,

    # ── High-frequency containers previously mapped to null ──────────
    # Multicast / routing
    "multicast": {"routing": True},
    "global": {"mode": "enable"},
    "shutdown": False,
    "permanent": True,
    "all": True,
    "ip-vrf": {"forwarding": "MGMT-VRF"},
    "dhcp": {"snooping": True},
    "default": {"enabled": True},
    "default-port": {"enabled": True},
    "msec": True,
    "year": True,
    "localtime": True,
    "show-timezone": True,
    "unassociate": True,
    "stitching": True,
    "vrf-also": True,
    "abort-character": True,
    "discovery": {"enabled": True},
    "unicast": {"enabled": True},
    "disable": False,
    "tcp": {"mss": 1460},
    "none": True,
    "log": {"enabled": True},
    "multitopology": True,
    "interface-ref": {"config": {"interface": "GigabitEthernet1/0/1"}},
    "disabled": False,
    "preserve": True,
    "output": {"policy-name": "OUTPUT-POLICY"},
    "passive": True,
    "ipv4": {"unicast": True},
    "md5": {"key-chain": "KEY-1"},
    "local": True,
    "uptime": True,
    "autohangup": True,
    "set-to-5": True,
    "set-to-6": True,
    "set-to-7": True,
    "set-to-8": True,
}


def enrich_top_level_example(example_obj, module_name):
    """Replace placeholder values in a top-level example object."""
    if not isinstance(example_obj, dict):
        return 0
    changes = 0
    for key, val in list(example_obj.items()):
        if isinstance(val, dict) and not val:
            # ── Empty {} — fill from mapping, field heuristic, or [null] ──
            if key in CONTAINER_FILL:
                example_obj[key] = CONTAINER_FILL[key]
                changes += 1
            else:
                hint = get_example_for_field(key, module_name)
                if hint != "configured-value":
                    example_obj[key] = hint
                    changes += 1
                else:
                    # YANG empty leaf / presence container → [null] per RFC 7951
                    example_obj[key] = [None]
                    changes += 1
        elif val is None:
            # ── null values — replace with known fill or [null] ──
            if key in CONTAINER_FILL:
                example_obj[key] = CONTAINER_FILL[key]
                changes += 1
            else:
                hint = get_example_for_field(key, module_name)
                if hint != "configured-value":
                    example_obj[key] = hint
                    changes += 1
                else:
                    # YANG empty leaf / presence container → [null] per RFC 7951
                    example_obj[key] = [None]
                    changes += 1
        elif isinstance(val, dict):
            changes += enrich_top_level_example(val, module_name)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    changes += enrich_top_level_example(item, module_name)
        elif isinstance(val, str) and val in ("example", "example-value", "string"):
            new_val = get_example_for_field(key, module_name)
            example_obj[key] = str(new_val) if isinstance(new_val, (int, float, bool)) else new_val
            changes += 1
        elif isinstance(val, int) and val == 1 and not isinstance(val, bool):
            new_val = get_example_for_field(key, module_name)
            if isinstance(new_val, (int, float)) and not isinstance(new_val, bool):
                conv = int(new_val)
                if conv != 1:
                    example_obj[key] = conv
                    changes += 1
    return changes


def get_resource_label(path, summary=""):
    """Extract a human-readable resource label from a RESTCONF path."""
    if summary:
        # Strip method prefixes
        label = re.sub(r"^(Get|Retrieve|Create|Update|Replace|Delete|Remove|Execute|Notification:)\s+", "", summary).strip()
        if label:
            return label
    # fallback: last meaningful segment
    segments = [s for s in path.split("/") if s and s != "data" and "=" not in s]
    if segments:
        raw = segments[-1].split(":")[-1]
        return raw.replace("-", " ")
    return "this resource"


def _populate_empty_example(example_obj, schema, module_name, restconf_path=""):
    """Populate empty {} inner values in example objects using schema properties.

    When generators emit examples like {"Cisco-IOS-XE-native:vlan": {}},
    this function fills in the empty inner object by walking the schema's
    properties and generating realistic values. Falls back to path-based
    heuristics when the schema has no properties defined.
    """
    if not isinstance(example_obj, dict) or not isinstance(schema, dict):
        return 0
    changes = 0
    for key, val in example_obj.items():
        if isinstance(val, dict) and not val:
            # Empty inner object — try to populate from schema
            built = build_example_from_schema(schema, module_name)
            if built and isinstance(built, dict):
                example_obj[key] = built
                changes += 1
            else:
                # Fallback: path-based heuristics when schema has no properties
                fallback = _build_example_from_path(key, restconf_path, module_name)
                if fallback:
                    example_obj[key] = fallback
                    changes += 1
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict) and not item:
                    built = build_example_from_schema(schema, module_name)
                    if built and isinstance(built, dict):
                        item.update(built)
                        changes += 1
    return changes


def _build_example_from_path(wrapper_key, restconf_path, module_name):
    """Generate a minimal but syntactically valid example from the RESTCONF path.

    Extracts the resource name from the wrapper key (e.g., "vlan" from
    "Cisco-IOS-XE-native:vlan") and produces a common-structure example
    that a device would accept. This is the fallback when schemas lack
    properties.
    """
    # Extract resource name: "Cisco-IOS-XE-native:vlan" -> "vlan"
    resource = wrapper_key.split(":")[-1] if ":" in wrapper_key else wrapper_key
    rl = resource.lower().replace("_", "-")

    # Extract path segments for context
    segments = [s.split(":")[-1] for s in restconf_path.split("/")
                if s and s != "data" and "=" not in s] if restconf_path else []

    # ── Resource-specific templates ────────────────────────────────────
    # VLAN configuration  
    if rl == "vlan":
        return {
            "vlan-list": [{"id": 100, "name": "DATA_VLAN"}]
        }

    # Interface related
    if rl in ("interface", "interfaces"):
        return {
            "GigabitEthernet": [{"name": "1/0/1", "description": "UPLINK"}]
        }

    # ACL / access-list
    if "access-list" in rl or "acl" in rl:
        return {
            "extended": [{"name": "ACL-PERMIT-ALL"}]
        }

    # Routing
    if rl in ("router", "routing"):
        return {"router": {"id": 1}}
    if rl in ("route", "ip-route", "static"):
        return {
            "ip-route-interface-forwarding-list": [{
                "prefix": "10.0.0.0",
                "mask": "255.255.255.0",
                "fwd-list": [{"fwd": "10.1.1.1"}]
            }]
        }

    # BGP
    if rl == "bgp":
        return {"asn": 65001, "neighbor": [{"id": "10.1.1.2", "remote-as": 65002}]}

    # OSPF
    if rl == "ospf":
        return {"id": 1, "network": [{"ip": "10.0.0.0", "mask": "0.0.0.255", "area": 0}]}

    # AAA
    if rl == "aaa":
        return {"authentication": {"login": {}}, "authorization": {"exec": {}}}

    # Spanning tree
    if "spanning-tree" in rl:
        return {"mode": "rapid-pvst"}

    # Logging
    if rl == "logging":
        return {"buffered": {"severity": "informational"}}

    # NTP
    if rl == "ntp":
        return {"server": {"server-list": [{"ip-address": "10.1.1.100"}]}}

    # SNMP
    if rl in ("snmp", "snmp-server"):
        return {"community": [{"name": "public", "RO": {}}]}

    # Line (console/vty)
    if rl == "line":
        return {"vty": [{"first": 0, "last": 4}]}

    # Banner
    if rl == "banner":
        return {"motd": {"banner": "Authorized Access Only"}}

    # Service
    if rl == "service":
        return {"timestamps": {"debug": {"datetime": {"msec": {}}}}}

    # Hostname
    if rl == "hostname":
        return "Switch-01"

    # Crypto / SSH
    if "crypto" in rl or "ssh" in rl:
        return {"key": {"generate": {"rsa": {"general-keys": {"modulus": 2048}}}}}

    # DHCP
    if "dhcp" in rl:
        return {"pool": [{"id": "POOL-1", "network": {"number": "10.0.0.0", "mask": "255.255.255.0"}}]}

    # NAT
    if "nat" in rl:
        return {"inside": {"source": {"list": [{"id": 1, "pool": "NAT-POOL"}]}}}

    # Policy / policy-map / class-map
    if "policy" in rl or "class-map" in rl:
        return {"name": "POLICY-1"}

    # Prefix-list
    if "prefix-list" in rl:
        return {"prefixes": [{"name": "PFX-LIST-1"}]}

    # Route-map
    if "route-map" in rl:
        return {"route-map-without-order-seq": [{"name": "RMAP-1"}]}

    # Generic containers — produce a minimal but non-empty example
    # using the resource name as a child-node hint
    val = get_example_for_field(resource, module_name)
    if val != "configured-value":
        return {resource: val}

    # Last resort: minimal but tagged example so users know to fill in
    return {"_comment": f"Configure {resource} parameters here"}


def enrich_operation(method, op, path, module_name):
    """Enrich a single operation with description and improved examples."""
    changes = 0

    resource = get_resource_label(path, op.get("summary", ""))

    # ── Add description if missing ──
    if not op.get("description"):
        if method == "post" and "/operations/" in path:
            rpc_name = path.split(":")[-1] if ":" in path else path.rsplit("/", 1)[-1]
            op["description"] = RPC_DESC.format(rpc_name=rpc_name)
            changes += 1
        elif op.get("summary", "").startswith("Notification:"):
            notif_name = path.rsplit("/", 1)[-1].split(":")[-1] if ":" in path else path.rsplit("/", 1)[-1]
            op["description"] = NOTIFICATION_DESC.format(name=notif_name)
            changes += 1
        elif method in METHOD_DESC:
            op["description"] = METHOD_DESC[method].format(resource=resource)
            changes += 1

    # ── Enrich requestBody schema + example ──
    rb = op.get("requestBody", {}).get("content", {})
    for media, media_obj in rb.items():
        if "schema" in media_obj:
            changes += enrich_schema_examples(media_obj["schema"], module_name, path)
        # Populate empty example inner values from schema properties
        if "example" in media_obj and "schema" in media_obj:
            changes += _populate_empty_example(media_obj["example"],
                                               media_obj["schema"], module_name, path)
        if "example" in media_obj:
            changes += enrich_top_level_example(media_obj["example"], module_name)

    # ── Enrich response schemas + examples ──
    for code, resp in op.get("responses", {}).items():
        for media, media_obj in resp.get("content", {}).items():
            if "schema" in media_obj:
                changes += enrich_schema_examples(media_obj["schema"], module_name, path)
            # Populate empty example inner values from schema properties
            if "example" in media_obj and "schema" in media_obj:
                changes += _populate_empty_example(media_obj["example"],
                                                   media_obj["schema"], module_name, path)
            if "example" in media_obj:
                changes += enrich_top_level_example(media_obj["example"], module_name)

    return changes


def process_spec(spec_path):
    """Load, enrich, and save a single OpenAPI spec."""
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    module_name = spec.get("info", {}).get("x-yang-module", spec_path.stem)
    changes = 0

    for path, path_obj in spec.get("paths", {}).items():
        for method in ("get", "post", "put", "patch", "delete"):
            op = path_obj.get(method)
            if op:
                changes += enrich_operation(method, op, path, module_name)

    # Also enrich component schemas if present
    for schema_name, schema_def in spec.get("components", {}).get("schemas", {}).items():
        changes += enrich_schema_examples(schema_def, module_name, schema_name)

    if changes > 0:
        with open(spec_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return changes


# ── Main ─────────────────────────────────────────────────────────────────────

V2_DIRS = [
    "swagger-oper-model",
    "swagger-cfg-model",
    "swagger-native-config-model",
    "swagger-openconfig-model",
    "swagger-ietf-model",
    "swagger-mib-model",
    "swagger-rpc-model",
    "swagger-events-model",
    "swagger-other-model",
]


def main():
    root = Path(__file__).resolve().parent.parent
    print("=" * 70)
    print("Enrich v2 Deep-Path Specs — Examples + Descriptions")
    print("=" * 70)

    grand_specs = 0
    grand_changes = 0

    for model_dir in V2_DIRS:
        api_v2 = root / model_dir / "api-v2"
        if not api_v2.exists():
            print(f"\n⚠  {model_dir}/api-v2 not found — skipping")
            continue

        specs = sorted(f for f in api_v2.glob("*.json") if f.name != "manifest.json")
        dir_changes = 0
        for sp in specs:
            c = process_spec(sp)
            dir_changes += c

        label = model_dir.replace("swagger-", "").replace("-model", "")
        print(f"  {label:30s}  {len(specs):>4} specs  {dir_changes:>6} enrichments")
        grand_specs += len(specs)
        grand_changes += dir_changes

    print(f"\n{'─' * 70}")
    print(f"  Total: {grand_specs} specs, {grand_changes} enrichments applied")
    print("=" * 70)


if __name__ == "__main__":
    main()
