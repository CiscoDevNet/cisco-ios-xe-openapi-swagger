# 🚀 Getting Started with Cisco IOS-XE RESTCONF APIs

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication Setup](#authentication-setup)
3. [Using Quick-Start Collections](#using-quick-start-collections)
4. [Code Examples](#code-examples)
5. [Understanding the Models](#understanding-the-models)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Quick Start

### Prerequisites

- Cisco IOS-XE device running version 17.18.1 or compatible version
- RESTCONF enabled on the device
- Network access to the device (HTTPS port 443)
- Valid credentials with appropriate privileges

### Enable RESTCONF on Your Device

```cisco
configure terminal
!
restconf
!
ip http secure-server
ip http authentication local
!
username admin privilege 15 secret cisco123
!
end
```

### Test Connectivity

```bash
# Simple curl test - get device hostname
curl -k -X GET \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/hostname" \
  -H "Accept: application/yang-data+json" \
  -u "admin:cisco123"
```

---

## Authentication Setup

### Basic Authentication

All RESTCONF API calls use HTTP Basic Authentication:

```bash
# Format: username:password
-u "admin:cisco123"
```

### Python Requests

```python
import requests
from requests.auth import HTTPBasicAuth

# Disable SSL warnings (not for production)
requests.packages.urllib3.disable_warnings()

response = requests.get(
    "https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/hostname",
    headers={"Accept": "application/yang-data+json"},
    auth=HTTPBasicAuth("admin", "cisco123"),
    verify=False
)
```

### Ansible

```yaml
- name: Get device hostname
  uri:
    url: "https://{{ inventory_hostname }}/restconf/data/Cisco-IOS-XE-native:native/hostname"
    method: GET
    user: "{{ ansible_user }}"
    password: "{{ ansible_password }}"
    force_basic_auth: yes
    validate_certs: no
    headers:
      Accept: "application/yang-data+json"
```

---

## Using Quick-Start Collections

We've curated 6 quick-start collections for common workflows. Each collection contains the most frequently used endpoints.

### 1. 🔧 Operational Troubleshooting

**File:** `swagger-oper-model/api/oper-00-troubleshooting.json`

**Use Cases:**
- Check interface status and errors
- Monitor CPU and memory utilization
- Verify BGP and OSPF neighbor states
- Review routing table entries

**Example: Get Interface Status**

```bash
curl -k -X GET \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces" \
  -H "Accept: application/yang-data+json" \
  -u "admin:cisco123"
```

### 2. 📈 Performance Monitoring

**File:** `swagger-oper-model/api/oper-00-performance.json`

**Use Cases:**
- Monitor QoS statistics
- Track interface utilization
- Review buffer drops and errors
- Analyze traffic patterns

**Example: Get QoS Statistics**

```bash
curl -k -X GET \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-qos-oper:qos-oper-data" \
  -H "Accept: application/yang-data+json" \
  -u "admin:cisco123"
```

### 3. 📦 Device Inventory

**File:** `swagger-oper-model/api/oper-00-inventory.json`

**Use Cases:**
- Retrieve hardware inventory (chassis, modules, transceivers)
- Get software version and licensing info
- Collect serial numbers and part numbers
- Verify hardware capabilities

**Example: Get Platform Details**

```bash
curl -k -X GET \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-platform-oper:components" \
  -H "Accept: application/yang-data+json" \
  -u "admin:cisco123"
```

### 4. 🚀 Day-0 Configuration

**File:** `swagger-native-config-model/api/native-00-day0.json`

**Use Cases:**
- Set device hostname and domain name
- Configure management interfaces
- Set up NTP and logging
- Configure AAA and local users

**Example: Set Hostname**

```bash
curl -k -X PATCH \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native" \
  -H "Accept: application/yang-data+json" \
  -H "Content-Type: application/yang-data+json" \
  -u "admin:cisco123" \
  -d '{
    "Cisco-IOS-XE-native:native": {
      "hostname": "Router-HQ-01"
    }
  }'
```

### 5. 🔌 Interface Configuration

**File:** `swagger-native-config-model/api/native-00-interface-basics.json`

**Use Cases:**
- Configure interface IP addresses
- Set interface descriptions
- Configure VLANs and trunking
- Enable/disable interfaces

**Example: Configure GigabitEthernet Interface**

```bash
curl -k -X PATCH \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1" \
  -H "Accept: application/yang-data+json" \
  -H "Content-Type: application/yang-data+json" \
  -u "admin:cisco123" \
  -d '{
    "Cisco-IOS-XE-native:GigabitEthernet": {
      "name": "1",
      "description": "Uplink to Core Switch",
      "ip": {
        "address": {
          "primary": {
            "address": "10.1.1.1",
            "mask": "255.255.255.0"
          }
        }
      }
    }
  }'
```

### 6. 🛣️ Routing Basics

**File:** `swagger-native-config-model/api/native-00-routing-basics.json`

**Use Cases:**
- Configure BGP neighbors and settings
- Set up OSPF areas and networks
- Create static routes
- Configure route-maps and prefix-lists

**Example: Configure Static Route**

```bash
curl -k -X POST \
  "https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/ip/route" \
  -H "Accept: application/yang-data+json" \
  -H "Content-Type: application/yang-data+json" \
  -u "admin:cisco123" \
  -d '{
    "Cisco-IOS-XE-native:route": {
      "ip-route-interface-forwarding-list": [
        {
          "prefix": "192.168.100.0",
          "mask": "255.255.255.0",
          "forwarding-address": "10.1.1.254"
        }
      ]
    }
  }'
```

---

## Code Examples

### Python: Complete GET Example

```python
#!/usr/bin/env python3
"""
Get all interface operational data
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# Device details
DEVICE = {
    "host": "10.0.0.1",
    "username": "admin",
    "password": "cisco123"
}

# API endpoint
url = f"https://{DEVICE['host']}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"

# Headers
headers = {
    "Accept": "application/yang-data+json"
}

# Make request
response = requests.get(
    url,
    headers=headers,
    auth=(DEVICE['username'], DEVICE['password']),
    verify=False
)

# Process response
if response.status_code == 200:
    data = response.json()
    
    # Extract interface information
    interfaces = data['Cisco-IOS-XE-interfaces-oper:interfaces']['interface']
    
    print(f"Found {len(interfaces)} interfaces:\n")
    
    for interface in interfaces:
        name = interface.get('name', 'Unknown')
        admin_status = interface.get('admin-status', 'Unknown')
        oper_status = interface.get('oper-status', 'Unknown')
        speed = interface.get('speed', 'Unknown')
        
        print(f"Interface: {name}")
        print(f"  Admin Status: {admin_status}")
        print(f"  Oper Status: {oper_status}")
        print(f"  Speed: {speed}")
        print()
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Python: Complete PATCH Example

```python
#!/usr/bin/env python3
"""
Configure interface description
"""

import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEVICE = {
    "host": "10.0.0.1",
    "username": "admin",
    "password": "cisco123"
}

# Configure GigabitEthernet1 description
interface_name = "1"
url = f"https://{DEVICE['host']}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet={interface_name}"

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

payload = {
    "Cisco-IOS-XE-native:GigabitEthernet": {
        "name": interface_name,
        "description": "Updated via RESTCONF API"
    }
}

response = requests.patch(
    url,
    headers=headers,
    auth=(DEVICE['username'], DEVICE['password']),
    json=payload,
    verify=False
)

if response.status_code in [200, 201, 204]:
    print("Success! Interface description updated.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Ansible: Complete Playbook

```yaml
---
# File: iosxe_restconf_example.yml
# Usage: ansible-playbook iosxe_restconf_example.yml

- name: Cisco IOS-XE RESTCONF Examples
  hosts: localhost
  gather_facts: no
  
  vars:
    iosxe_host: "10.0.0.1"
    iosxe_user: "admin"
    iosxe_pass: "cisco123"
  
  tasks:
    # Task 1: Get interface operational status
    - name: Get interface operational data
      uri:
        url: "https://{{ iosxe_host }}/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces"
        method: GET
        user: "{{ iosxe_user }}"
        password: "{{ iosxe_pass }}"
        force_basic_auth: yes
        validate_certs: no
        headers:
          Accept: "application/yang-data+json"
        status_code: 200
      register: interfaces_response
    
    - name: Display interface count
      debug:
        msg: "Found {{ interfaces_response.json['Cisco-IOS-XE-interfaces-oper:interfaces']['interface'] | length }} interfaces"
    
    # Task 2: Update interface description
    - name: Update GigabitEthernet1 description
      uri:
        url: "https://{{ iosxe_host }}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1"
        method: PATCH
        user: "{{ iosxe_user }}"
        password: "{{ iosxe_pass }}"
        force_basic_auth: yes
        validate_certs: no
        headers:
          Accept: "application/yang-data+json"
          Content-Type: "application/yang-data+json"
        body: |
          {
            "Cisco-IOS-XE-native:GigabitEthernet": {
              "name": "1",
              "description": "Configured via Ansible RESTCONF"
            }
          }
        body_format: json
        status_code:
          - 200
          - 201
          - 204
      register: config_response
    
    - name: Confirm configuration change
      debug:
        msg: "Interface description updated successfully"
      when: config_response.status in [200, 201, 204]
```

---

## Understanding the Models

### 1. **Native Configuration Model** (28 files, 18 categories)

**Purpose:** Full CLI-equivalent configuration

**Categories:** interfaces, routing, security, system, qos, vpn, wireless, switching, multicast, mpls, sdwan, services, platform, nat, voice, aaa, other, plus 3 quick-starts

**When to use:** For comprehensive device configuration tasks

### 2. **Operational Data Model** (20 files, 16 categories)

**Purpose:** Read-only real-time device state

**Categories:** interfaces, routing, platform, memory, qos, wireless, vpn, security, switching, environment, processes, sdwan, mpls, services, other, plus 3 quick-starts

**When to use:** Monitoring, troubleshooting, inventory collection

### 3. **Events Model** (11 files, 10 categories)

**Purpose:** YANG-Push event notifications

**Categories:** interfaces, routing, security, platform, wireless, vpn, sdwan, services, qos, other

**When to use:** Real-time event subscriptions and monitoring

### 4. **RPC Operations Model** (10 files, 9 categories)

**Purpose:** Execute operational commands

**Categories:** network-ops, wireless-ops, system-ops, security-ops, config-ops, debug-ops, platform-ops, cloud-ops, other

**When to use:** Triggering actions like ping, traceroute, clearing counters

---

## Common Workflows

### Workflow 1: Daily Health Check

```python
#!/usr/bin/env python3
"""Daily device health check"""

import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEVICE = {"host": "10.0.0.1", "username": "admin", "password": "cisco123"}
BASE_URL = f"https://{DEVICE['host']}/restconf/data"

def get_data(endpoint):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={"Accept": "application/yang-data+json"},
        auth=(DEVICE['username'], DEVICE['password']),
        verify=False
    )
    return response.json() if response.status_code == 200 else None

# 1. Check CPU utilization
cpu_data = get_data("Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization")
print(f"CPU 5-sec: {cpu_data['Cisco-IOS-XE-process-cpu-oper:cpu-utilization']['five-seconds']}%")

# 2. Check memory usage
mem_data = get_data("Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic")
print(f"Memory used: {mem_data['Cisco-IOS-XE-memory-oper:memory-statistic'][0]['used-memory']} bytes")

# 3. Check interface errors
intf_data = get_data("Cisco-IOS-XE-interfaces-oper:interfaces")
for intf in intf_data['Cisco-IOS-XE-interfaces-oper:interfaces']['interface']:
    if intf.get('statistics', {}).get('in-errors', 0) > 0:
        print(f"WARNING: {intf['name']} has input errors")
```

### Workflow 2: Interface Provisioning

```bash
#!/bin/bash
# Provision a new interface with IP, description, and enable

DEVICE="10.0.0.1"
USER="admin"
PASS="cisco123"
INTERFACE="2"

curl -k -X PATCH \
  "https://${DEVICE}/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=${INTERFACE}" \
  -H "Accept: application/yang-data+json" \
  -H "Content-Type: application/yang-data+json" \
  -u "${USER}:${PASS}" \
  -d '{
    "Cisco-IOS-XE-native:GigabitEthernet": {
      "name": "'${INTERFACE}'",
      "description": "Data Link to Branch Office",
      "ip": {
        "address": {
          "primary": {
            "address": "192.168.10.1",
            "mask": "255.255.255.0"
          }
        }
      },
      "shutdown": false
    }
  }'
```

### Workflow 3: Backup Configuration

```python
#!/usr/bin/env python3
"""Backup device configuration to JSON file"""

import requests
import json
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEVICE = {"host": "10.0.0.1", "username": "admin", "password": "cisco123"}

# Get full native configuration
response = requests.get(
    f"https://{DEVICE['host']}/restconf/data/Cisco-IOS-XE-native:native",
    headers={"Accept": "application/yang-data+json"},
    auth=(DEVICE['username'], DEVICE['password']),
    verify=False
)

if response.status_code == 200:
    config = response.json()
    
    # Save to file with timestamp
    filename = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration backed up to {filename}")
else:
    print(f"Error: {response.status_code}")
```

---

## Troubleshooting

### Issue: "Connection Refused"

**Problem:** Can't connect to device

**Solutions:**
1. Verify RESTCONF is enabled: `show running-config | include restconf`
2. Check HTTPS server: `show running-config | include ip http`
3. Verify network connectivity: `ping 10.0.0.1`
4. Check firewall rules

### Issue: "401 Unauthorized"

**Problem:** Authentication failure

**Solutions:**
1. Verify credentials are correct
2. Check user privilege level (needs privilege 15)
3. Confirm AAA configuration
4. Try creating a new user account

### Issue: "404 Not Found"

**Problem:** Endpoint doesn't exist

**Solutions:**
1. Verify the YANG model is supported on your device
2. Check IOS-XE version compatibility
3. Use correct namespace in URL
4. Browse Swagger UI to find correct path

### Issue: "400 Bad Request"

**Problem:** Malformed request body

**Solutions:**
1. Validate JSON syntax
2. Check namespace matches the path
3. Verify required fields are included
4. Review examples in Swagger UI

### Issue: "SSL Certificate Error"

**Problem:** SSL verification fails

**Solutions:**
1. Use `-k` flag in curl
2. Set `verify=False` in Python requests
3. Set `validate_certs: no` in Ansible
4. Install device certificate (production)

---

## Best Practices

### 1. Use HTTPS Always

Never transmit credentials over unencrypted HTTP.

### 2. Start with GET Requests

Test connectivity and authentication with safe read operations before attempting configuration changes.

### 3. Use Quick-Start Collections

Our curated collections contain the most commonly used endpoints - start there before exploring the full API.

### 4. Handle Errors Gracefully

```python
try:
    response = requests.get(url, ...)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
except requests.exceptions.ConnectionError:
    print("Could not connect to device")
except json.JSONDecodeError:
    print("Invalid JSON response")
```

### 5. Use the Code Generator

Visit [code-generator.html](../code-generator.html) to automatically generate curl, Python, and Ansible code for any endpoint.

### 6. Implement Rate Limiting

Don't overwhelm the device with rapid API calls. Add delays between requests:

```python
import time
time.sleep(0.5)  # 500ms delay between requests
```

### 7. Validate Before Configuration

Always retrieve current configuration before making changes:

```python
# 1. GET current config
current = get_config(endpoint)

# 2. Modify as needed
new_config = modify_config(current)

# 3. PATCH changes
update_config(endpoint, new_config)

# 4. Verify change
verify_config(endpoint)
```

### 8. Use Descriptive Variable Names

```python
# Bad
r = requests.get(u, h=h, a=(u,p))

# Good
response = requests.get(
    url=api_endpoint,
    headers=restconf_headers,
    auth=(username, password)
)
```

### 9. Log API Interactions

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"GET {url}")
response = requests.get(url, ...)
logger.info(f"Status: {response.status_code}")
```

### 10. Test in Lab First

Always test configuration changes in a lab environment before deploying to production.

---

## Next Steps

1. **Explore Quick-Starts:** Visit the [main page](../index.html) and try the 6 quick-start collections
2. **Generate Code:** Use the [code generator](../code-generator.html) for your specific use case
3. **Browse Full APIs:** Explore all models to discover additional capabilities
4. **Read Documentation:** Check [PROJECT_REQUIREMENTS.md](../PROJECT_REQUIREMENTS.md) for project structure
5. **Review Examples:** See consolidated files for production-realistic examples

---

## Additional Resources

- **Swagger UI Documentation:** Browse interactive API docs at the main page
- **YANG Models:** Check `references/17181-YANG-modules/` for source YANG files
- **Cisco DevNet:** https://developer.cisco.com/docs/ios-xe/
- **RESTCONF RFC:** https://datatracker.ietf.org/doc/html/rfc8040
- **YANG RFC:** https://datatracker.ietf.org/doc/html/rfc7950

---

**Need Help?** Review the troubleshooting section above or explore the Swagger UI for detailed endpoint documentation and examples.
