# Plan: Catalyst 9300 MDT Telemetry — YANG Data Models, XPaths & KPIs for Splunk Dashboard

Comprehensive reference of every YANG operational data model, XPath, and the specific KPIs/counters/metrics to visualize in the Splunk dashboard for a switching telemetry demo on Catalyst 9300 (IOS XE 17.12+).

---

## Feature KPI Detail — Per YANG Data Model

### 1. CPU Utilization — `Cisco-IOS-XE-process-cpu-oper.yang` — `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization`

**YANG Module:** `Cisco-IOS-XE-process-cpu-oper`
**XPath:** `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| CPU 5-second average | `five-seconds` | gauge (%) | Time chart, single value gauge |
| CPU 1-minute average | `one-minute` | gauge (%) | Time chart overlay |
| CPU 5-minute average | `five-minutes` | gauge (%) | Time chart overlay |

**Splunk Panel:** Time chart showing all three CPU averages over time, per switch. Single-value gauge for current 5-second reading. Alert threshold at >80%.

---

### 2. Memory Statistics — `Cisco-IOS-XE-memory-oper.yang` — `/memory-ios-xe-oper:memory-statistics/memory-statistic`

**YANG Module:** `Cisco-IOS-XE-memory-oper`
**XPath:** `/memory-ios-xe-oper:memory-statistics/memory-statistic`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total memory (bytes) | `total-memory` | gauge | Single value (converted to GB) |
| Used memory (bytes) | `used-memory` | gauge | Bar gauge (% of total) |
| Free memory (bytes) | `free-memory` | gauge | Bar gauge |
| Lowest usage ever | `lowest-usage` | gauge | Reference line |
| Memory pool name | `name` (key) | string | Filter/group-by (Processor, lsmpi_io, reserve Processor) |

**Splunk Panel:** Stacked area chart showing used vs free over time for "Processor" pool. Percent utilization gauge. Group by memory pool name.

---

### 3. Process Memory — `Cisco-IOS-XE-process-memory-oper.yang` — `/process-memory-ios-xe-oper:memory-usage-processes`

**YANG Module:** `Cisco-IOS-XE-process-memory-oper`
**XPath:** `/process-memory-ios-xe-oper:memory-usage-processes`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Process name | `name` (key) | string | Table column / group-by |
| PID | `pid` (key) | int | Table column |
| Allocated memory | `allocated-memory` | counter | Top-N bar chart |
| Freed memory | `freed-memory` | counter | Comparison chart |
| Holding memory | `holding-memory` | gauge | Top-N bar chart |
| Get buffers | `get-buffers` | counter | Table column |
| Ret buffers | `ret-buffers` | counter | Table column |

**Splunk Panel:** Top 10 processes by `holding-memory`. Allocated vs freed comparison chart. Table of all processes sortable by memory.

---

### 4. System DRAM (Platform Software) — `Cisco-IOS-XE-platform-software-oper.yang` — `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes`

**YANG Module:** `Cisco-IOS-XE-platform-software-oper`
**XPath:** `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total DRAM (bytes) | control process memory fields | gauge | Single value (GB) |
| Used DRAM | used memory fields | gauge | Percent gauge |
| Free DRAM | free memory fields | gauge | Time chart |

**Splunk Panel:** System DRAM total/used/free in GB with percentage gauge per switch.

---

### 5. Environment Sensors (Temperature, Fan, Power Supply) — `Cisco-IOS-XE-environment-oper.yang` — `/environment-ios-xe-oper:environment-sensors`

**YANG Module:** `Cisco-IOS-XE-environment-oper`
**XPath:** `/environment-ios-xe-oper:environment-sensors`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Sensor name | `name` (key) | string | Table column / filter |
| Sensor location | `location` | string | Group-by (Switch 1, Switch 2...) |
| Current reading | `current-reading` | gauge | Gauge, time chart |
| Sensor units | `sensor-units` | string | Label (celsius, watts, rpm, mV) |
| State | `state` | enum | Status indicator (GREEN/Normal/NotExist) |
| Sensor type name | `sensor-name` | string | Filter (temperature, power, fan) |
| Low critical threshold | `low-critical-threshold` | int | Reference line |
| High critical threshold | `high-critical-threshold` | int | Reference line |
| Low normal threshold | `low-normal-threshold` | int | Reference line |
| High normal threshold | `high-normal-threshold` | int | Reference line |

**Specific sensor names on C9300:**
- **Inlet Temp Sens** — inlet air temperature (Celsius), GREEN/YELLOW/RED
- **Outlet Temp Sen** — exhaust air temperature (Celsius)
- **HotSpot Temp Se** — ASIC hotspot temperature (Celsius)
- **Power Supply A** — PSU A watts, state=Normal/NotExist
- **Power Supply B** — PSU B watts, state=Normal/NotExist
- **FAN - T1 1/2/3** — fan tray temperatures (Celsius)

**Splunk Panel:** Temperature time chart (Inlet/Outlet/HotSpot), PSU wattage gauge with Normal/NotExist status indicator, fan status table. Alert when state != GREEN/Normal.

---

### 6. Power over Ethernet (PoE) — `Cisco-IOS-XE-poe-oper.yang` — `/poe-ios-xe-oper:poe-oper-data`

**YANG Module:** `Cisco-IOS-XE-poe-oper`
**XPath:** `/poe-ios-xe-oper:poe-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | `poe-port-detail/intf-name` (key) | string | Table column |
| Operational power (mW) | `poe-port-detail/oper-power` | gauge | Bar chart per port |
| Operational state | `poe-port-detail/oper-state` | enum | Status indicator |
| PD class | `poe-port-detail/pd-class` | string | Table column |
| Power used (mW) | `poe-port-detail/power-used` | gauge | Stacked bar chart |
| LLDP power requested | `poe-port-detail/lldp-mdi-rx/power-requested` | gauge | Comparison |
| LLDP power allocated | `poe-port-detail/lldp-mdi-rx/power-allocated` | gauge | Comparison |
| Power priority | `poe-port-detail/lldp-mdi-rx/power-priority` | string | Table column |
| Power source | `poe-port-detail/lldp-mdi-rx/power-source` | string | Table column |
| Power type | `poe-port-detail/lldp-mdi-rx/power-type` | string | Table column |
| PSE max available power | `poe-port-detail/lldp-mdi-rx/pse-max-available-power` | gauge | Reference line |
| Dual-sig power class A/B | `poe-port-detail/lldp-mdi-rx/dual-sig-pwr-class-mode-a/b` | string | Detail table |

**Splunk Panel:** Per-port power consumption bar chart, total switch PoE budget gauge (sum vs max), PoE status table with PD class/priority, power requested vs allocated comparison.
**Reference:** https://grafana.com/grafana/dashboards/17238-catalyst-poe-dashboard/, https://github.com/jeremycohoe/cisco-mdt-poe

---

### 7. Interface Statistics — `Cisco-IOS-XE-interfaces-oper.yang` — `/interfaces-ios-xe-oper:interfaces/interface`

**YANG Module:** `Cisco-IOS-XE-interfaces-oper`
**XPath:** `/interfaces-ios-xe-oper:interfaces/interface`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | `name` (key) | string | Filter / group-by |
| Admin status | `admin-status` | enum | Status indicator |
| Oper status | `oper-status` | enum | Status indicator (up/down) |
| Speed (bps) | `speed` | gauge | Table column |
| IP address | `ipv4` | string | Table column |
| Physical address | `phys-address` | string | Table column |
| **RX rate (Kbps)** | `statistics/rx-kbps` | gauge | **Time chart** |
| **TX rate (Kbps)** | `statistics/tx-kbps` | gauge | **Time chart** |
| **RX rate (pps)** | `statistics/rx-pps` | gauge | Time chart |
| **TX rate (pps)** | `statistics/tx-pps` | gauge | Time chart |
| In octets | `statistics/in-octets` | counter | Derivative for bps |
| Out octets | `statistics/out-octets` | counter | Derivative for bps |
| In unicast pkts | `statistics/in-unicast-pkts` | counter | Table |
| In broadcast pkts | `statistics/in-broadcast-pkts` | counter | Table |
| In multicast pkts | `statistics/in-multicast-pkts` | counter | Table |
| Out unicast/broadcast/multicast | `statistics/out-*-pkts` | counter | Table |
| **In errors** | `statistics/in-errors` | counter | **Alert panel** |
| **In CRC errors** | `statistics/in-crc-errors` | counter | **Alert panel** |
| **In discards** | `statistics/in-discards` | counter | **Alert panel** |
| Out errors | `statistics/out-errors` | counter | Alert panel |
| Out discards | `statistics/out-discards` | counter | Alert panel |
| **Num flaps** | `statistics/num-flaps` | counter | **Single value / alert** |
| Interface type | `interface-type` | enum | Filter |
| **Ether state** (17.14+) | `ether-state/negotiated-duplex-mode`, `negotiated-port-speed`, `media-type`, `auto-negotiate`, `enable-flow-control` | various | Detail table |
| **Ether stats** (17.14+) | `ether-stats/in-mac-pause-frames`, `in-8021q-frames`, `in-jabber-frames`, `in-oversize-frames`, `in-fragment-frames` | counter | Detail table |
| **Dot3 error counters** (17.14+) | `dot3-error-counters-v2/dot3-fcs-errors`, `dot3-alignment-errors`, `dot3-late-collisions`, `dot3-symbol-errors`, etc. | counter | Error detail table |

**Splunk Panel:** RX/TX Kbps time chart per interface, RX/TX pps time chart, error/discard counters with alert thresholds, interface status table (up/down/flaps), top-N by traffic volume.

---

### 8. Spanning Tree Protocol (STP) — `Cisco-IOS-XE-spanning-tree-oper.yang` — `/stp-ios-xe-oper:stp-details`

**YANG Module:** `Cisco-IOS-XE-spanning-tree-oper`
**XPath:** `/stp-ios-xe-oper:stp-details`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| STP instance | `stp-detail/instance` (key) | int | Group-by |
| Designated root address | `stp-detail/designated-root-address` | string | Table |
| Designated root priority | `stp-detail/designated-root-priority` | int | Table |
| Root cost | `stp-detail/root-cost` | int | Table |
| Root port | `stp-detail/root-port` | string | Table |
| **Interface name** | `stp-detail/interfaces/interface/name` (key) | string | Table row |
| **Port role** | `stp-detail/interfaces/interface/role` | enum | **Status indicator** (root/designated/alternate/backup) |
| **Port state** | `stp-detail/interfaces/interface/state` | enum | **Status indicator** (forwarding/blocking/listening/learning) |
| Port cost | `stp-detail/interfaces/interface/cost` | int | Table |
| Port priority | `stp-detail/interfaces/interface/port-priority` | int | Table |
| **BPDU sent** | `stp-detail/interfaces/interface/bpdu-sent` | counter | Time chart |
| **BPDU received** | `stp-detail/interfaces/interface/bpdu-received` | counter | Time chart |
| BPDU guard | `stp-detail/interfaces/interface/bpdu-guard` | enum | Status indicator |
| BPDU filter | `stp-detail/interfaces/interface/bpdu-filter` | enum | Table |
| Forward transitions | `stp-detail/interfaces/interface/forward-transitions` | counter | **Alert** (topology change) |
| Guard type | `stp-detail/interfaces/interface/guard` | enum | Table |
| Designated bridge address/priority | `stp-detail/interfaces/interface/designated-bridge-*` | various | Table |

**Splunk Panel:** STP instance overview table (root bridge, root port), per-port state/role status grid (color-coded: forwarding=green, blocking=orange), BPDU counters time chart, alert on forward-transitions increment (topology change detected).

---

### 9. Stack Health — `Cisco-IOS-XE-stack-oper.yang` — `/stack-ios-xe-oper:stack-oper-data`

**YANG Module:** `Cisco-IOS-XE-stack-oper`
**XPath:** `/stack-ios-xe-oper:stack-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Chassis number | `stack-node/chassis-number` (key) | int | Table row |
| **Role** | `stack-node/role` | enum | **Status indicator** (Active/Standby/Member) |
| **Node state** | `stack-node/node-state` | enum | **Status indicator** (Ready/NotReady) |
| Priority | `stack-node/priority` | int (1-15) | Table |
| Serial number | `stack-node/serial-number` | string | Table (asset tracking) |
| MAC address | `stack-node/mac-address` | string | Table |
| Reload reason | `stack-node/reload-reason` | string | Table |
| SSO ready flag | `stack-node/sso-ready-flag` | bool | Status indicator |
| Stack mode | `stack-node/stack-mode` | enum | Table |
| Interface MTU | `stack-node/interface-mtu` | int | Table |
| Latency | `stack-node/latency` | int | Time chart |
| **Stack port number** | `stack-node/stack-ports/port-num` | int | Table |
| **Stack port state** | `stack-node/stack-ports/port-state` | enum | Status indicator |
| Stack port neighbor switch | `stack-node/stack-ports/switch-nbr-port` | string | Table |
| **KA sent** | `stack-node/keepalive-counters/sent` | counter | Time chart |
| **KA received** | `stack-node/keepalive-counters/received` | counter | Time chart |
| KA sent failure | `stack-node/keepalive-counters/sent-failure` | counter | Alert |
| KA receive failure | `stack-node/keepalive-counters/receive-failure` | counter | Alert |
| KA consecutive losses | `stack-node/keepalive-counters/consecutive-losses` | counter | **Alert** |
| **Stack port stats** | `stack-node/stack-ports/sp-stats/rac-data-crc-err`, `rac-invalid-ringword-err`, `rac-pcs-codeword-err`, `rac-rwcrc-err` | counter | Error alert panel |

**Splunk Panel:** Stack member overview table (chassis, role, state, priority, serial), stack port status grid, keepalive counters time chart, alert on consecutive-losses > 0 or port-state != Up.

---

### 10. VLANs — `Cisco-IOS-XE-vlan-oper.yang` — `/vlan-ios-xe-oper:vlans`

**YANG Module:** `Cisco-IOS-XE-vlan-oper`
**XPath:** `/vlan-ios-xe-oper:vlans`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VLAN ID | `vlan/id` (key) | int | Table row |
| VLAN name | `vlan/name` | string | Table column |
| VLAN status | `vlan/status` | enum (active/suspended) | Status indicator |
| Member interfaces | `vlan/vlan-interfaces/interface` | list | Table column (comma-separated) |

**Splunk Panel:** VLAN inventory table with member port count, active/suspended status indicators per switch.

---

### 11. MAC Address Table (MATM) — `Cisco-IOS-XE-matm-oper.yang` — `/matm-ios-xe-oper:matm-oper-data`

**YANG Module:** `Cisco-IOS-XE-matm-oper`
**XPath:** `/matm-ios-xe-oper:matm-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VLAN ID | `matm-table/vlan-id-number` (key) | int | Group-by |
| Table type | `matm-table/table-type` | string | Filter |
| Aging time | `matm-table/aging-time` | int | Table column |
| MAC address | `matm-table/matm-mac-entry/mac` (key) | string | Table row |
| Entry type | `matm-table/matm-mac-entry/mat-addr-type` | enum (static/dynamic) | Table column |
| Port | `matm-table/matm-mac-entry/port` | string | Table column |

**Splunk Panel:** MAC table entry count per VLAN (bar chart), MAC table total size (single value), table of MAC entries (filterable by VLAN).

---

### 12. ARP Table — `Cisco-IOS-XE-arp-oper.yang` — `/arp-ios-xe-oper:arp-data`

**YANG Module:** `Cisco-IOS-XE-arp-oper`
**XPath:** `/arp-ios-xe-oper:arp-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF name | `arp-vrf/vrf` (key) | string | Filter |
| IP address | `arp-vrf/arp-entry/address` (key) | string | Table row |
| MAC address | `arp-vrf/arp-entry/hardware` | string | Table column |
| Interface | `arp-vrf/arp-entry/interface` | string | Table column |
| Entry type | `arp-vrf/arp-entry/mode` | enum (dynamic/static) | Table column |
| Entry time | `arp-vrf/arp-entry/time` | string | Table column |

**Splunk Panel:** ARP entry count per VRF (single value), ARP table browser with search.

---

### 13. LLDP Neighbors — `Cisco-IOS-XE-lldp-oper.yang` — `/lldp-ios-xe-oper:lldp-entries`

**YANG Module:** `Cisco-IOS-XE-lldp-oper`
**XPath:** `/lldp-ios-xe-oper:lldp-entries`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local interface | `lldp-intf-details/if-name` (key) | string | Table |
| Neighbor device ID | `lldp-intf-details/lldp-neighbor-details/identifier` | string | Table |
| Neighbor port ID | `lldp-intf-details/lldp-neighbor-details/port-id` | string | Table |
| Neighbor system name | `lldp-intf-details/lldp-neighbor-details/system-name` | string | Table |
| Capabilities | `lldp-intf-details/lldp-neighbor-details/system-capabilities` | string | Table |
| Management address | `lldp-intf-details/lldp-neighbor-details/mgmt-addrs` | string | Table |

**Splunk Panel:** LLDP neighbor topology table per switch, neighbor count single value, device discovery table.

---

### 14. CDP Neighbors — `Cisco-IOS-XE-cdp-oper.yang` — `/cdp-ios-xe-oper:cdp-neighbor-details`

**YANG Module:** `Cisco-IOS-XE-cdp-oper`
**XPath:** `/cdp-ios-xe-oper:cdp-neighbor-details`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local interface | `cdp-neighbor-detail/local-intf-name` | string | Table |
| Device name | `cdp-neighbor-detail/device-name` | string | Table |
| Platform | `cdp-neighbor-detail/platform-name` | string | Table |
| Remote port | `cdp-neighbor-detail/port-id` | string | Table |
| Capabilities | `cdp-neighbor-detail/capability` | string | Table |
| IP address | `cdp-neighbor-detail/ip-address` | string | Table |
| Software version | `cdp-neighbor-detail/version` | string | Detail table |

**Splunk Panel:** CDP neighbor discovery table, neighbor count by platform type (pie chart).

---

### 15. Platform Components — `Cisco-IOS-XE-platform-oper.yang` — `/platform-ios-xe-oper:components`

**YANG Module:** `Cisco-IOS-XE-platform-oper`
**XPath:** `/platform-ios-xe-oper:components`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Component name | `component/cname` (key) | string | Table row |
| Type | `component/state/type` | string | Table column |
| Description | `component/state/description` | string | Table |
| Part number | `component/state/part-no` | string | Table |
| Serial number | `component/state/serial-no` | string | Table (asset tracking) |
| Status | `component/state/status` | string | Status indicator |
| Status description | `component/state/status-desc` | string | Table |
| Version | `component/state/version` | string | Table |
| Empty slot | `component/state/empty` | bool | Status indicator |
| Parent | `component/state/parent` | string | Hierarchy |

**Splunk Panel:** Hardware inventory table (component name, type, serial, status), status indicators for PSU/fan/module health, filterable by component type.

---

### 16. Device Hardware (Uptime, SW Version, Boot Time) — `Cisco-IOS-XE-device-hardware-oper.yang` — `/device-hardware-xe-oper:device-hardware-data/device-hardware`

**YANG Module:** `Cisco-IOS-XE-device-hardware-oper`
**XPath:** `/device-hardware-xe-oper:device-hardware-data/device-hardware`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| **Software version** | `device-system-data/software-version` | string | **Single value per switch** |
| **Boot time** | `device-system-data/boot-time` | datetime | **Single value** (uptime calc) |
| Reboot reason | `device-system-data/last-reboot-reason` | string | Table column |
| Hardware model | `device-inventory/hw-type` | string | Table |
| Serial number | `device-inventory/serial-number` | string | Table |

**Splunk Panel:** Device overview banner — hostname, software version, boot time (calculated uptime), reboot reason, serial number. One row per switch.

---

### 17. Switchport — `Cisco-IOS-XE-switchport-oper.yang` — `/switchport-ios-xe-oper:switchport-oper-data`

**YANG Module:** `Cisco-IOS-XE-switchport-oper`
**XPath:** `/switchport-ios-xe-oper:switchport-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | key | string | Table row |
| Switchport mode | operational mode (access/trunk) | enum | Table column |
| Access VLAN | access VLAN ID | int | Table column |
| Trunk native VLAN | native VLAN | int | Table column |
| Trunk allowed VLANs | allowed VLANs | string | Table column |

**Splunk Panel:** Switchport mode overview table — interface, mode (access/trunk), VLAN assignment. Port count by mode (pie chart).

---

### 18. Transceiver / Optics — `Cisco-IOS-XE-transceiver-oper.yang` — `/xcvr-ios-xe-oper:transceiver-oper-data`

**YANG Module:** `Cisco-IOS-XE-transceiver-oper`
**XPath:** `/xcvr-ios-xe-oper:transceiver-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface name | key | string | Table row |
| Transceiver type | type/vendor/part | string | Table |
| TX power (dBm) | output power | gauge | Time chart |
| RX power (dBm) | input power | gauge | Time chart |
| Temperature (C) | temperature | gauge | Time chart |
| Voltage (V) | voltage | gauge | Table |
| Bias current (mA) | bias current | gauge | Table |

**Splunk Panel:** Optics health table (port, type, TX/RX power, temp), alert on RX power below threshold.

---

### 19. UDLD — `Cisco-IOS-XE-udld-oper.yang` — `/udld-ios-xe-oper:udld-oper-data`

**YANG Module:** `Cisco-IOS-XE-udld-oper`
**XPath:** `/udld-ios-xe-oper:udld-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | key | string | Table row |
| UDLD neighbor status | neighbor state | enum | Status indicator |
| Direction | direction | string | Table |

**Splunk Panel:** UDLD neighbor status table with bidirectional/unidirectional indicators.

---

### 20. 802.1X / Identity Sessions — `Cisco-IOS-XE-identity-oper.yang` — `/identity-ios-xe-oper:identity-oper-data`

**YANG Module:** `Cisco-IOS-XE-identity-oper`
**XPath:** `/identity-ios-xe-oper:identity-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| MAC address | `session-context-data/mac` | string | Table row |
| Interface name | `session-context-data/intf-name` | string | Table |
| State | `session-context-data/state` | enum | Status indicator |
| Method ID | `session-context-data/method-id` | string | Table |
| IPv4 address | `session-context-data/ipv4` | string | Table |
| VLAN ID | `session-context-data/vlan-id` | int | Table |
| Device name | `session-context-data/device-name` | string | Table |
| Device type | `session-context-data/device-type` | string | Table |
| Policy name | `session-context-data/policy-name` | string | Table |
| Authorized | `session-context-data/authorized` | bool | Status indicator |
| AAA session ID | `session-context-data/aaa-sess-id` | string | Detail |
| AAA server status | `session-context-data/aaa-server/server-status` | string | Table |
| EPM service template | `epm-service-block/template-name` | string | Table |

**Splunk Panel:** Active 802.1X sessions table (MAC, interface, state, device type, VLAN), session count gauge, auth method breakdown (pie chart).

---

### 21. TCAM Utilization — `Cisco-IOS-XE-tcam-oper.yang` — `/tcam-ios-xe-oper:tcam-details`

**YANG Module:** `Cisco-IOS-XE-tcam-oper`
**XPath:** `/tcam-ios-xe-oper:tcam-details`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| ASIC number | `tcam-detail/asic-no` (key) | int | Group-by |
| Table name | `tcam-detail/name` (key) | string | Group-by (Security ACE, Control Plane Entries, etc.) |
| **TCAM entries used** | `tcam-detail/tcam-entries-used` | gauge | **Bar gauge (% of max)** |
| TCAM entries max | (reference value per table/SDM) | int | Reference line |

**Splunk Panel:** TCAM utilization bar chart per SDM table/category per ASIC, percentage gauge, alert when >80% utilized. Variable selector for table name.
**Note:** `/tcam-ios-xe-oper:tcam-details` is marked as "Deprecated" in mdt-capabilities-oper but is still widely used. Verify on 17.12+.

---

### 22. MDT Subscription Health — `Cisco-IOS-XE-mdt-oper-v2.yang` — `/mdt-oper-v2:mdt-oper-v2-data`

**YANG Module:** `Cisco-IOS-XE-mdt-oper-v2`
**XPath:** `/mdt-oper-v2:mdt-oper-v2-data` (or `/mdt-oper:mdt-oper-data/mdt-subscriptions`)

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Subscription ID | key | int | Table row |
| Subscription type | type (configured/dynamic) | string | Table |
| State | state (valid/invalid) | enum | Status indicator |
| XPath filter | filter xpath | string | Table column |
| Updates sent | update count | counter | Time chart |
| Connection state | receiver state | enum | **Status indicator** (Connected/Connecting/Disconnected) |

**Splunk Panel:** MDT health overview table — sub ID, xpath, state, connection status, updates sent. Alert on any "Disconnected" or "Invalid" state.

---

### 23. Software Install — `Cisco-IOS-XE-install-oper.yang` — `/install-ios-xe-oper:install-oper-data`

**YANG Module:** `Cisco-IOS-XE-install-oper`
**XPath:** `/install-ios-xe-oper:install-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Package name | install package name | string | Table |
| Package version | install package version | string | Table |
| Package state | state (active/committed) | enum | Status indicator |

**Splunk Panel:** Installed software packages table per switch (version compliance check).

---

### 24. BGP State — `Cisco-IOS-XE-bgp-oper.yang` — `/bgp-ios-xe-oper:bgp-state-data`

**YANG Module:** `Cisco-IOS-XE-bgp-oper`
**XPath:** `/bgp-ios-xe-oper:bgp-state-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Neighbor ID | `neighbors/neighbor/neighbor-id` (key) | string | Table row |
| **Session state** | `neighbors/neighbor/session-state` | enum | **Status indicator** (Established/Connect/Idle/Active) |
| Prefixes received | `neighbors/neighbor/prefix-activity/received/current-prefixes` | gauge | Table / time chart |
| Prefixes sent | `neighbors/neighbor/prefix-activity/sent/current-prefixes` | gauge | Table |
| Up time | `neighbors/neighbor/up-time` | string | Table |
| AS number | `neighbors/neighbor/as` | int | Table |
| Installed prefixes | `neighbors/neighbor/installed-prefixes` | gauge | Table |
| BGP version | BGP version fields | int | Table |
| Messages received | neighbor message counters | counter | Time chart |
| Messages sent | neighbor message counters | counter | Time chart |

**Splunk Panel:** BGP neighbor summary table (neighbor, AS, state, prefixes received/sent, uptime), status indicator grid (all Established = green), alert on state != Established.

---

### 25. OSPF State — `Cisco-IOS-XE-ospf-oper.yang` — `/ospf-ios-xe-oper:ospf-oper-data`

**YANG Module:** `Cisco-IOS-XE-ospf-oper`
**XPath:** `/ospf-ios-xe-oper:ospf-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance number | `ospf-instance/af` and `router-id` | int/string | Group-by |
| Area ID | `ospf-instance/ospf-area/area-id` | int | Table |
| **Neighbor ID** | `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/neighbor-id` (key) | string | Table row |
| **Neighbor state** | `ospf-instance/ospf-area/ospf-interface/ospf-neighbor/state` | enum | **Status indicator** (Full/2Way/Init/Down) |
| Neighbor address | neighbor address | string | Table |
| Interface name | `ospf-instance/ospf-area/ospf-interface/name` | string | Table |
| Interface cost | `ospf-instance/ospf-area/ospf-interface/cost` | int | Table |
| DR IP | `ospf-instance/ospf-area/ospf-interface/dr-address` | string | Table |
| BDR IP | `ospf-instance/ospf-area/ospf-interface/bdr-address` | string | Table |
| LSA count | area LSA summary | int | Table |

**Splunk Panel:** OSPF neighbor table (neighbor ID, area, interface, state, DR/BDR), state indicator (all Full = green), area summary table.

---

### 26. IETF Routing Table (RIB) — `ietf-routing.yang` — `/ietf-routing:routing/ribs/rib`

**YANG Module:** `ietf-routing`
**XPath:** `/ietf-routing:routing/ribs/rib` (NMDA, 17.12+; pre-NMDA equivalent: `/ietf-routing:routing-state`)

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| RIB name | `rib/name` (key) | string | Filter (ipv4-unicast, ipv6-unicast) |
| Destination prefix | `route/destination-prefix` | string | Table row |
| Next hop | `route/next-hop` | string | Table column |
| Source protocol | `route/source-protocol` | enum (connected/static/ospf/bgp) | Table / pie chart |
| Metric | `route/metric` | int | Table column |
| Route preference | `route/route-preference` | int | Table column |

**Splunk Panel:** Routing table browser (prefix, next-hop, protocol, metric), route count by protocol (pie chart), total route count (single value trending).

---

### 27. DHCP Pool Stats — `Cisco-IOS-XE-dhcp-oper.yang` — `/dhcp-ios-xe-oper:dhcp-oper-data`

**YANG Module:** `Cisco-IOS-XE-dhcp-oper`
**XPath:** `/dhcp-ios-xe-oper:dhcp-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Pool name | key | string | Table row |
| Allocated addresses | allocated count | gauge | Bar chart |
| Available addresses | available count | gauge | Bar chart |
| Utilization % | calculated | gauge | Percent gauge |

**Splunk Panel:** DHCP pool utilization bar chart (allocated vs available), alert when >90% utilized.

---

### 28. High Availability State — `Cisco-IOS-XE-ha-oper.yang` — `/ha-ios-xe-oper:ha-oper-data`

**YANG Module:** `Cisco-IOS-XE-ha-oper`
**XPath:** `/ha-ios-xe-oper:ha-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| HA state | active/standby/init | enum | Single value status |
| Switchover reason | last switchover reason | string | Table |
| Switchover time | last switchover time | datetime | Table |

**Splunk Panel:** HA state indicator per switch (Active/Standby), last switchover reason and time.

---

### 29. Linecard Status — `Cisco-IOS-XE-linecard-oper.yang` — `/linecard-ios-xe-oper:linecard-oper-data`

**YANG Module:** `Cisco-IOS-XE-linecard-oper`
**XPath:** `/linecard-ios-xe-oper:linecard-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Slot number | key | int | Table row |
| Linecard state | state | enum (active/standby/inserted) | Status indicator |
| Card type | type | string | Table |
| Serial number | serial | string | Table |

**Splunk Panel:** Linecard inventory and status table (relevant for C9400/C9600; informational for C9300).

---

### 30. TrustSec (SGT/SXP) — `Cisco-IOS-XE-trustsec-oper.yang` — `/trustsec-ios-xe-oper:trustsec-state`

**YANG Module:** `Cisco-IOS-XE-trustsec-oper`
**XPath:** `/trustsec-ios-xe-oper:trustsec-state`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| SGT tag value | `cts-rolebased-sgtmaps` entries | int | Table |
| SGT IP binding | IP-to-SGT mapping | string | Table |
| SXP connection peer | `cts-sxp-connections` peer IP | string | Table |
| SXP connection state | state | enum | Status indicator |
| SXP connection mode | speaker/listener | enum | Table |

**Splunk Panel:** SGT assignment table, SXP connection status table, SGT count (single value).

---

### 31. LACP / Port-Channel (via interfaces-oper) — `Cisco-IOS-XE-interfaces-oper.yang` — `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

**YANG Module:** `Cisco-IOS-XE-interfaces-oper` (and `Cisco-IOS-XE-lacp-oper` for LACP counters)
**XPath:** `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Aggregate interface name | `name` (Port-channelX) | string | Table row |
| Member links | `lag-aggregate-state/member-link` | list | Table column |
| Member link state | per-member oper state | enum | Status indicator |
| LAG type | static/LACP | string | Table |
| LACP activity counters | `lacp-oper` data | counter | Time chart |

**Splunk Panel:** Port-channel member status table (aggregate, members, status), alert on member down.

---

### 32. ACL Hit Counters — `Cisco-IOS-XE-acl-oper.yang` — `/acl-ios-xe-oper:access-lists/access-list`

**YANG Module:** `Cisco-IOS-XE-acl-oper`
**XPath:** `/acl-ios-xe-oper:access-lists/access-list`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| ACL name | `access-control-list-name` (key) | string | Dimension |
| ACL type | `access-control-list-type` | enum | Table column |
| Rule name | `access-list-entry/rule-name` (key) | string | Dimension |
| Match count | `access-list-entry/match-counter` | counter64 | Time chart (rate) |

**Splunk Panel:** Per-ACL/per-rule match counters time chart (rate of hits over time), top-10 most-hit ACE rules bar chart, zero-hit rules table for cleanup auditing.

---

### 33. NTP Synchronization — `Cisco-IOS-XE-ntp-oper.yang` — `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info`

**YANG Module:** `Cisco-IOS-XE-ntp-oper`
**XPath:** `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Association ID | `ntp-associations/assoc-id` (key) | uint16 | Dimension |
| Peer reachability | `ntp-associations/peer-reach` | uint8 | Gauge |
| Stratum | `ntp-associations/peer-stratum` | uint32 | Single value |
| Delay | `ntp-associations/delay` | decimal64 | Time chart |
| Offset | `ntp-associations/offset` | decimal64 | Time chart |
| Jitter | `ntp-associations/jitter` | decimal64 | Time chart |
| Selection status | `ntp-associations/peer-selection-status` | enum | Status indicator |

**Splunk Panel:** NTP offset/jitter time chart per peer, stratum single value, reachability gauge (255 = all recent polls succeeded), alert on offset > 100ms or reachability < 255.

---

### 34. BFD Sessions — `Cisco-IOS-XE-bfd-oper.yang` — `/bfd-ios-xe-oper:bfd-state/sessions`

**YANG Module:** `Cisco-IOS-XE-bfd-oper`
**XPath:** `/bfd-ios-xe-oper:bfd-state/sessions`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Session type | `session/type` (key) | enum | Dimension |
| Interface | `bfd-nbr/interface` (key) | string | Dimension |
| Neighbor IP | `bfd-nbr/ip` (key) | ip-address | Dimension |
| Local state | `state` | enum | Status indicator |
| Remote state | `remote-state` | enum | Status indicator |

**Splunk Panel:** BFD session status table (neighbor, interface, state), alert on state != Up.

---

### 35. HSRP State — `Cisco-IOS-XE-hsrp-oper.yang` — `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info`

**YANG Module:** `Cisco-IOS-XE-hsrp-oper`
**XPath:** `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Group ID | `group-id` (key) | uint16 | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| Priority | `priority` | uint32 | Single value |
| State | `state` | enum | Status indicator |
| Active IP | `active-ip` | ip-address | Table column |
| Standby IP | `standby-ip` | ip-address | Table column |
| Virtual IP | `virtual-ip` | ip-address | Table column |

**Splunk Panel:** HSRP group status table (group, interface, state, active/standby/virtual IPs, priority), alert on state change from Active to non-Active.

---

### 36. VRRP State — `Cisco-IOS-XE-vrrp-oper.yang` — `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state`

**YANG Module:** `Cisco-IOS-XE-vrrp-oper`
**XPath:** `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-number` (key) | uint32 | Dimension |
| Group ID | `group-id` (key) | uint32 | Dimension |
| Address type | `addr-type` (key) | enum | Dimension |
| VRRP state | `vrrp-state` | enum | Status indicator |
| Priority | `priority` | uint32 | Single value |
| Virtual IP | `virtual-ip` | ip-address | Table column |
| Master IP | `master-ip` | ip-address | Table column |

**Splunk Panel:** VRRP group status table similar to HSRP, alert on state != Master when expected.

---

### 37. Flexible NetFlow / Flow Monitor — `Cisco-IOS-XE-flow-monitor-oper.yang` — `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor`

**YANG Module:** `Cisco-IOS-XE-flow-monitor-oper`
**XPath:** `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Monitor name | `name` (key) | string | Dimension |
| Flows added | `flow-monitor-statistics/flows-added` | uint64 | Time chart (rate) |
| Flows aged | `flow-monitor-statistics/flows-aged` | uint64 | Time chart (rate) |
| Active flows | (flows-added minus flows-aged) | calculated | Gauge |
| Cache entries | `flow-cache-statistics` | uint64 | Gauge |
| Export packets sent | `flow-export-statistics` | uint64 | Time chart (rate) |

**Splunk Panel:** Active flow count gauge per monitor, flows added/aged rate time chart, export statistics counters. Useful for validating NetFlow data is being generated and exported.

---

### 38. IP SLA Probes — `Cisco-IOS-XE-ip-sla-oper.yang` — `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry`

**YANG Module:** `Cisco-IOS-XE-ip-sla-oper`
**XPath:** `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Operation ID | `oper-id` (key) | uint32 | Dimension |
| Operation type | `oper-type` | enum | Table column |
| Return code | `latest-return-code` | enum | Status indicator |
| Success count | `success-count` | uint32 | Time chart |
| Failure count | `failure-count` | uint32 | Time chart |
| Latest RTT | `rtt-info/latest-rtt` | uint64 | Time chart |
| Threshold exceeded | `threshold-occured` | boolean | Alert |
| Start time | `latest-oper-start-time` | date-and-time | Table column |

**Splunk Panel:** Per-probe RTT time chart, success/failure ratio pie chart, return code status table, alert on failure-count increment or threshold-occured = true.

---

### 39. AAA / RADIUS / TACACS Statistics — `Cisco-IOS-XE-aaa-oper.yang` — `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats`

**YANG Module:** `Cisco-IOS-XE-aaa-oper`
**XPath:** `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Server group | `group-name` (key) | string | Dimension |
| Server IP | `radius-server-ip` (key) | ip-address | Dimension |
| Auth port | `auth-port` (key) | uint16 | Dimension |
| Access accepts | `authen-access-accepts` | uint32 | Time chart (rate) |
| Access rejects | `authen-access-rejects` | uint32 | Time chart (rate) |
| Connection opens | `connection-opens` | uint32 | Time chart (rate) |
| TACACS server | `aaa-tacacs-stats/tacacs-server-address` (key) | ip-address | Dimension |

**Splunk Panel:** RADIUS accept/reject ratio time chart per server, TACACS connection status table, total auth request rate, alert on high reject rate or server unreachable.

---

### 40. Port Security — `Cisco-IOS-XE-psecure-oper.yang` — `/psecure-ios-xe-oper:psecure-oper-data/psecure-state`

**YANG Module:** `Cisco-IOS-XE-psecure-oper`
**XPath:** `/psecure-ios-xe-oper:psecure-oper-data/psecure-state`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-name` (key) | string | Dimension |
| VLAN | `psecure-entry/vlan` (key) | uint16 | Dimension |
| MAC address | `psecure-entry/mac` (key) | mac-address | Table column |
| Secure type | `psecure-entry/type` | enum | Table column |
| Age remaining | `psecure-entry/age-remain` | uint32 (min) | Table column |

**Splunk Panel:** Port security summary table (interface, secured MACs, type), count of secured ports (single value), alert on violation events.

---

### 41. MACsec / MKA Encryption — `Cisco-IOS-XE-macsec-oper.yang + Cisco-IOS-XE-mka-oper.yang` — `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics`

**YANG Module:** `Cisco-IOS-XE-macsec-oper` and `Cisco-IOS-XE-mka-oper`
**XPath:** `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` and `/mka-ios-xe-oper:mka-oper-data/mka-statistics`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Interface | `if-name` (key) | string | Dimension |
| TX untagged pkts | `tx-untag-pkts` | uint64 | Time chart |
| RX no-tag pkts | `rx-notag-pkts` | uint64 | Time chart |
| SC encrypted pkts | `sc-encrypt-pkts` | uint64 | Time chart (rate) |
| SC auth-only pkts | `sc-auth-only-pkts` | uint64 | Time chart (rate) |
| MKA PDU RX | `mkpdu-stats-rx` | uint32 | Time chart (rate) |
| MKA PDU TX | `mkpdu-stats-tx` | uint32 | Time chart (rate) |
| SAK generation errors | `mka-err-sak-gen` | uint32 | Alert counter |

**Splunk Panel:** MACsec encrypted/untagged traffic counters per interface, MKA PDU exchange rate, alert on SAK generation errors or untagged packet spikes.

---

### 42. VRF Operational State — `Cisco-IOS-XE-vrf-oper.yang` — `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry`

**YANG Module:** `Cisco-IOS-XE-vrf-oper`
**XPath:** `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| VRF name | `vrf-name` (key) | string | Dimension |
| Address family | `address-family-entry/address-family` | enum | Table column |
| Member interfaces | `interface` (leaf-list) | string[] | Table column |

**Splunk Panel:** VRF membership overview table (VRF name, address family, assigned interfaces), VRF count (single value).

---

### 43. Data Plane Resources (TCAM/EM per Feature) — `Cisco-IOS-XE-switch-dp-resources-oper.yang` — `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource`

**YANG Module:** `Cisco-IOS-XE-switch-dp-resources-oper`
**XPath:** `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Location | `fru/slot/bay/chassis/node` (keys) | string | Dimension |
| Feature | `feature` (key) | enum | Dimension |
| Protocol | `protocol` (key) | enum | Dimension |
| Direction | `direction` (key) | enum | Dimension |
| Max TCAM % used | `max-tcam-percentage-used` | decimal64 | Bar chart / Gauge |
| Max EM % used | `max-em-percentage-used` | decimal64 | Bar chart / Gauge |

**Splunk Panel:** Per-feature TCAM/EM utilization bar chart (grouped by feature+protocol+direction), percentage gauge with alert thresholds, complements section 21 TCAM by showing per-feature breakdown.

---

### 44. CPU Punt/Inject Counters — `Cisco-IOS-XE-switch-dp-punt-inject-oper.yang` — `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats`

**YANG Module:** `Cisco-IOS-XE-switch-dp-punt-inject-oper`
**XPath:** `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| CPU queue ID | `cpuq-id` (key) | uint8 | Dimension |
| Queue name | `cpu-punt-queue-name` | string | Dimension |
| RX received (current) | `rx-recv-cur` | uint64 | Time chart (rate) |
| RX dropped (current) | `rx-dropped-cur` | uint64 | Time chart (rate) |

**Splunk Panel:** Per-CPU-queue punt rate time chart, drop rate time chart, drop-to-receive ratio gauge. Critical for CoPP monitoring — high drops indicate control plane overload.

---

### 45. PoE Health (Detailed Port-Level) — `Cisco-IOS-XE-poe-health-oper.yang` — `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health`

**YANG Module:** `Cisco-IOS-XE-poe-health-oper`
**XPath:** `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Port number | `port-num` (key) | uint32 | Dimension |
| Port state | `port-state` | enum | Status indicator |
| Port event | `port-event` | enum | Table column |
| Port voltage | `port-voltage` | uint64 | Time chart |
| Consumed power (signal) | `signal-pair-info/consumed-power` | uint32 | Time chart |
| Consumed power (spare) | `spare-pair-info/consumed-power` | uint32 | Time chart |
| Shutdown count | `poe-meta-data/port-shutdown-cnt` | uint16 | Counter |
| MOSFET fault count | `poe-meta-data/mosfet-fault-cnt` | uint16 | Alert counter |
| Over-temp count | `poe-meta-data/over-tmp-cnt` | uint16 | Alert counter |
| Internal error count | `poe-meta-data/internal-err-cnt` | uint16 | Alert counter |
| Event time | `event-time` | date-and-time | Time stamp |

**Splunk Panel:** PoE port health event timeline, fault counter summary table, port voltage trend line. Complements section 6 by providing hardware-level diagnostics and fault history.

---

### 46. CEF / FIB State — `Cisco-IOS-XE-fib-oper.yang` — `/fib-ios-xe-oper:fib-oper-data`

**YANG Module:** `Cisco-IOS-XE-fib-oper`
**XPath:** `/fib-ios-xe-oper:fib-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Total adjacencies | `adjacency-table/num-adjacencies` | uint32 | Gauge |
| Complete adjacencies | `adjacency-table/num-complete-adjacencies` | uint32 | Gauge |
| Incomplete adjacencies | `adjacency-table/num-incomplete-adjacencies` | uint32 | Alert counter |
| FIB enabled (IPv4) | `cef-state/fib/ipv4/fib-enabled` | boolean | Status indicator |
| FIB running (IPv4) | `cef-state/fib/ipv4/fib-running` | boolean | Status indicator |
| IPv4 punt total | `cef-statistics/ipv4-switching/total-punt` | uint64 | Time chart (rate) |
| IPv4 drop total | `cef-statistics/ipv4-switching/total-drop` | uint64 | Time chart (rate) |

**Splunk Panel:** CEF adjacency summary gauges (total/complete/incomplete), IPv4/IPv6 punt and drop rate time chart, FIB enabled/running status indicator, alert on incomplete adjacency count increase or high punt/drop rate.

---

### 47. EIGRP Routing (if applicable) — `Cisco-IOS-XE-eigrp-oper.yang` — `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance`

**YANG Module:** `Cisco-IOS-XE-eigrp-oper`
**XPath:** `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| AFI | `afi` (key) | enum | Dimension |
| VRF | `vrf-name` (key) | string | Dimension |
| AS number | `as-num` (key) | uint16 | Dimension |
| Interface | `eigrp-interface/name` (key) | string | Dimension |
| Neighbor address | `eigrp-nbr/nbr-address` (key) | ip-address | Table column |
| Route metric | `eigrp-route/metric` | uint64 | Table column |
| Next hop | `eigrp-route/nexthop` | ip-address | Table column |

**Splunk Panel:** EIGRP neighbor table (address, interface, AS), topology table (prefix, metric, next-hop), neighbor count gauge.

---

### 48. IS-IS Routing (if applicable) — `Cisco-IOS-XE-isis-oper.yang` — `/isis-ios-xe-oper:isis-oper-data/isis-instance`

**YANG Module:** `Cisco-IOS-XE-isis-oper`
**XPath:** `/isis-ios-xe-oper:isis-oper-data/isis-instance`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance tag | `tag` (key) | string | Dimension |
| System ID | `isis-neighbor/system-id` (key) | phys-address | Dimension |
| Level | `isis-neighbor/level` (key) | enum | Dimension |
| Interface | `isis-neighbor/if-name` (key) | string | Dimension |
| Neighbor state | `isis-neighbor/state` | enum | Status indicator |
| Hold time | `isis-neighbor/holdtime` | uint32 (sec) | Gauge |

**Splunk Panel:** IS-IS neighbor adjacency table with state indicators, alert on state != Up.

---

### 49. BGP Neighbor Detail — `Cisco-IOS-XE-bgp-nbr-oper.yang` — `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data`

**YANG Module:** `Cisco-IOS-XE-bgp-nbr-oper`
**XPath:** `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Neighbor address | `bgp-nbr-data/ip` (key) | ip-address | Dimension |
| Interface name | `bgp-nbr-data/if-name` (key) | string | Dimension |
| Address family | `bgp-nbr-data/af` (key) | enum | Dimension |
| VRF / NI | `bgp-nbr-data/ni-name` (key) | string | Dimension |
| TCP FSM state | `bgp-nbr-data/conn/state` | enum | Status indicator |
| Connection mode | `bgp-nbr-data/conn/mode` | enum | Table column |
| Received current prefixes | `bgp-nbr-cntrs/prfx-act/rcvd/cur-prfx` | uint64 | Gauge |
| Sent current prefixes | `bgp-nbr-cntrs/prfx-act/sent/cur-prfx` | uint64 | Gauge |
| Updates received | `bgp-nbr-cntrs/rcvd/updates` | uint32 | Time chart (rate) |
| Updates sent | `bgp-nbr-cntrs/sent/updates` | uint32 | Time chart (rate) |

**Splunk Panel:** Per-neighbor BGP detail table (state, AFI/SAFI, VRF, prefix counts), update counters trend, alert on neighbors leaving established states.

---

### 50. BGP RIB Detail — `Cisco-IOS-XE-bgp-rib-oper.yang` — `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route`

**YANG Module:** `Cisco-IOS-XE-bgp-rib-oper`
**XPath:** `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Prefix | `prefix` (key) | ip-prefix | Dimension |
| VRF / NI | `ni-name` (key) | string | Dimension |
| AFI/SAFI | `afi-safi` (key) | enum | Dimension |
| Route version | `version` | uint32 | Table column |
| Available paths | `avail-paths` | uint32 | Gauge |
| Next hop | `bgp-path/nh` | ip-address | Table column |
| MED | `bgp-path/metric` | uint32 | Table column |
| Local preference | `bgp-path/lp` | uint32 | Table column |
| Weight | `bgp-path/weight` | uint32 | Table column |
| Origin | `bgp-path/origin` | enum | Status indicator |

**Splunk Panel:** BGP prefix table (prefix, VRF, path count, next-hop, local-pref, MED), top prefixes by path fan-out, route-origin distribution chart.

---

### 51. High-Scale ARP — `Cisco-IOS-XE-ip-arp-oper.yang` — `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry`

**YANG Module:** `Cisco-IOS-XE-ip-arp-oper`
**XPath:** `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| IPv4 address | `addr` (key) | ipv4-address | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| MAC address | `hw-addr` | mac-address | Table column |
| ARP mode | `mode` | enum | Status indicator |
| Update time | `update-time` | date-and-time | Table column |

**Splunk Panel:** High-scale ARP table by VRF and interface, mode distribution chart, churn view using update-time recency.

---

### 52. IPv6 Neighbor Discovery — `Cisco-IOS-XE-ipv6-nd-oper.yang` — `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry`

**YANG Module:** `Cisco-IOS-XE-ipv6-nd-oper`
**XPath:** `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| IPv6 address | `v6addr` (key) | ipv6-address | Dimension |
| Interface | `if-name` (key) | string | Dimension |
| MAC address | `mac-addr` | mac-address | Table column |
| ND mode | `mode` | enum | Status indicator |
| Neighbor state | `state` | enum | Status indicator |
| Update time | `update-time` | date-and-time | Table column |
| Is router | `is-router` | boolean | Table column |

**Splunk Panel:** IPv6 neighbor state table, state distribution chart, stale/probe/incomplete alert indicator.

---

### 53. IS-IS Interface Detail — `Cisco-IOS-XE-isis-intf-oper.yang` — `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type`

**YANG Module:** `Cisco-IOS-XE-isis-intf-oper`
**XPath:** `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Instance tag | `tag` (key) | string | Dimension |
| Interface | `isis-if/if-name` (key) | string | Dimension |
| Interface enabled | `isis-if/is-enabled` | boolean | Status indicator |
| Circuit type | `isis-if/circuit-type` | enum | Table column |
| Neighbor system ID | `isis-if-nbr/system-id` (key) | phys-address | Dimension |
| Neighbor level | `isis-if-nbr/level` (key) | enum | Dimension |
| Neighbor state | `isis-if-nbr/adj-state` | enum | Status indicator |
| Neighbor IPv4 | `isis-if-nbr/nbr-ipv4-addr` | ip-address | Table column |
| Neighbor uptime | `isis-if-nbr/up-time` | date-and-time | Table column |

**Splunk Panel:** IS-IS interface and adjacency detail table, adjacency-state summary, per-interface enablement status view.

---

### 54. Multicast Routing State — `Cisco-IOS-XE-mroute-oper.yang` — `/mroute-ios-xe-oper:mroute-oper-data/mroute-state`

**YANG Module:** `Cisco-IOS-XE-mroute-oper`
**XPath:** `/mroute-ios-xe-oper:mroute-oper-data/mroute-state`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Source | `source` (key) | ip-address | Dimension |
| Group | `group` (key) | ip-address | Dimension |
| VRF | `vrf` (key) | string | Dimension |
| Address family | `af` (key) | enum | Dimension |
| Ingress interface | `ingress-if/if-name` | string | Table column |
| RPF neighbor | `rpf-nbr` | ip-address | Table column |
| Multicast mode | `mroute-mode` | enum | Status indicator |
| Software packets/sec | `sw-packets-per-second` | uint64 | Time chart |
| Software kbps | `sw-kbits-per-second` | uint64 | Time chart |
| Software RPF failures | `sw-rpf-failed` | uint64 | Alert counter |

**Splunk Panel:** Multicast tree table (S,G, VRF, RPF), software traffic trends, alert on rising RPF failures.

---

### 55. Stack Member / Stackwise Virtual Detail — `Cisco-IOS-XE-stack-member-oper.yang` — `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info`

**YANG Module:** `Cisco-IOS-XE-stack-member-oper`
**XPath:** `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Chassis number | `chassis-num` (key) | uint8 | Dimension |
| Stack mode | `stack-mode` | enum | Status indicator |
| Boot time | `mbr-boottime` | date-and-time | Table column |
| Peer latency | `latency` | uint32 (ns) | Gauge |
| SVL bandwidth | `svl-bw` | uint32 (Gbps) | Gauge |
| Stack port link OK | `mbr-port/link-ok` | boolean | Status indicator |
| Stack port active | `mbr-port/link-actv` | boolean | Status indicator |

**Splunk Panel:** Stack member inventory table, Stackwise Virtual health gauges, stack-port status view, alert on link loss or peer-latency anomalies.

---

### 56. Tunnel Interface State — `Cisco-IOS-XE-tunnel-oper.yang` — `/ios-tunnel-oper:tunnel-oper-data/tunnel-if`

**YANG Module:** `Cisco-IOS-XE-tunnel-oper`
**XPath:** `/ios-tunnel-oper:tunnel-oper-data/tunnel-if`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Tunnel name | `name` (key) | string | Dimension |
| Tunnel mode | `mode` | enum | Status indicator |
| Interface VRF | `intf-vrf` | string | Dimension |
| Admin status | `admin-status` | enum | Status indicator |
| Oper status | `status` | enum | Status indicator |
| Source address | `src-addr` | ip-address | Table column |
| Destination address | `dst-addr` | ip-address | Table column |
| MTU | `mtu` | uint32 | Gauge |
| TX bandwidth | `tx-bandwidth` | uint32 (kbps) | Time chart |
| RX bandwidth | `rx-bandwidth` | uint32 (kbps) | Time chart |

**Splunk Panel:** Tunnel health table (status, endpoints, VRF, mode), bandwidth trend chart, alert on tunnel down transitions.

---

### 57. YANG Management Plane Interfaces — `Cisco-IOS-XE-yang-interfaces-oper.yang` — `/yang-interfaces-oper:yang-interfaces-oper-data`

**YANG Module:** `Cisco-IOS-XE-yang-interfaces-oper`
**XPath:** `/yang-interfaces-oper:yang-interfaces-oper-data`

| KPI / Counter | Leaf Path | Type | Splunk Viz |
|--------------|-----------|------|------------|
| Local VRF | `local-vrf/vrf-name` (key) | string | Dimension |
| Local VRF state | `local-vrf/state` | enum | Status indicator |
| NETCONF SSH host key | `ssh-server/hostkey-name` | string | Table column |
| RSA-SHA2-256 enabled | `ssh-server/hostkey-alg/rsa-sha2-256` | boolean | Status indicator |
| AES128-CTR enabled | `ssh-server/ciphers/aes128-ctr` | boolean | Status indicator |
| HMAC-SHA2-256 enabled | `ssh-server/macs/hmac-sha2-256` | boolean | Status indicator |

**Splunk Panel:** Management-plane readiness table (VRF reachability and SSH algorithm posture), alert when NETCONF local VRF state is down.

---

## Recommended Polling Intervals

| Tier | Interval | Feature Areas |
|------|----------|---------------|
| Hot (real-time) | 30s (3000 cs) | CPU, interfaces (rx/tx kbps), process memory, punt/inject counters |
| Warm (near-real-time) | 60s (6000 cs) | Environment sensors, platform components, BGP, BGP neighbor detail, OSPF, STP, stack, stack-member detail, PoE, BFD, HSRP/VRRP, IP SLA, NTP, CEF/FIB, IS-IS interface detail, multicast routing, tunnel state, flow monitor |
| Cool (inventory/slow-change) | 300s (30000 cs) | VLANs, MAC table, ARP, high-scale ARP, IPv6 ND, LLDP, CDP, switchport, transceiver, TCAM, DHCP, device-hardware, install, MDT health, HA, linecard, TrustSec, identity, UDLD, IETF routing, ACL counters, AAA/RADIUS, port security, MACsec/MKA, VRF, DP resources, EIGRP, IS-IS, BGP RIB detail, YANG management-plane interfaces |

Recommendation: 60s for environment/interfaces/cpu/platform and 15min for device-hardware.

---

## IOS XE Subscription Configuration (filter xpath)

Complete gRPC dial-out subscription config for all 57 target features and 58 subscriptions. Subscription IDs generally match section numbers. Receiver IP and port are placeholders — update to match your OTel collector.

Variables to customize before applying:
- `RECEIVER_IP` — OTel collector IP address (e.g., 10.1.1.3)
- `RECEIVER_PORT` — gRPC listen port (e.g., 57500)

```
! ============================================================
! Prerequisite: gRPC Dial-Out Receiver Profile
! ============================================================
telemetry receiver protocol otel-collector
 host ip-address RECEIVER_IP RECEIVER_PORT
 protocol grpc-tcp

! ============================================================
! HOT TIER — 30-second polling (3000 centiseconds)
! CPU, Interfaces, Process Memory, Punt/Inject
! ============================================================

! --- §1. CPU Utilization ---
telemetry ietf subscription 1001
 encoding encode-kvgpb
 filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §3. Process Memory ---
telemetry ietf subscription 1003
 encoding encode-kvgpb
 filter xpath /process-memory-ios-xe-oper:memory-usage-processes
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §7. Interface Statistics ---
telemetry ietf subscription 1007
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §44. CPU Punt/Inject Counters ---
telemetry ietf subscription 1044
 encoding encode-kvgpb
 filter xpath /switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats
 stream yang-push
 update-policy periodic 3000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! WARM TIER — 60-second polling (6000 centiseconds)
! Environment, Platform, Routing, STP, Stack, PoE, FHRP, etc.
! ============================================================

! --- §2. Memory Statistics ---
telemetry ietf subscription 1002
 encoding encode-kvgpb
 filter xpath /memory-ios-xe-oper:memory-statistics/memory-statistic
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §4. System DRAM (Platform Software) ---
telemetry ietf subscription 1004
 encoding encode-kvgpb
 filter xpath /platform-sw-ios-xe-oper:cisco-platform-software/control-processes
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §5. Environment Sensors ---
telemetry ietf subscription 1005
 encoding encode-kvgpb
 filter xpath /environment-ios-xe-oper:environment-sensors
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §6. PoE Operational Data ---
telemetry ietf subscription 1006
 encoding encode-kvgpb
 filter xpath /poe-ios-xe-oper:poe-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §8. Spanning Tree ---
telemetry ietf subscription 1008
 encoding encode-kvgpb
 filter xpath /stp-ios-xe-oper:stp-details
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §9. Stack Health ---
telemetry ietf subscription 1009
 encoding encode-kvgpb
 filter xpath /stack-ios-xe-oper:stack-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §15. Platform Components ---
telemetry ietf subscription 1015
 encoding encode-kvgpb
 filter xpath /platform-ios-xe-oper:components
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §24. BGP State ---
telemetry ietf subscription 1024
 encoding encode-kvgpb
 filter xpath /bgp-ios-xe-oper:bgp-state-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §25. OSPF State ---
telemetry ietf subscription 1025
 encoding encode-kvgpb
 filter xpath /ospf-ios-xe-oper:ospf-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §33. NTP Synchronization ---
telemetry ietf subscription 1033
 encoding encode-kvgpb
 filter xpath /ntp-ios-xe-oper:ntp-oper-data/ntp-status-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §34. BFD Sessions ---
telemetry ietf subscription 1034
 encoding encode-kvgpb
 filter xpath /bfd-ios-xe-oper:bfd-state/sessions
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §35. HSRP State ---
telemetry ietf subscription 1035
 encoding encode-kvgpb
 filter xpath /hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §36. VRRP State ---
telemetry ietf subscription 1036
 encoding encode-kvgpb
 filter xpath /vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §37. Flexible NetFlow / Flow Monitor ---
telemetry ietf subscription 1037
 encoding encode-kvgpb
 filter xpath /flow-monitor-ios-xe-oper:flow-monitors/flow-monitor
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §38. IP SLA Probes ---
telemetry ietf subscription 1038
 encoding encode-kvgpb
 filter xpath /ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §45. PoE Health (Detailed Port-Level) ---
telemetry ietf subscription 1045
 encoding encode-kvgpb
 filter xpath /poe-health-oper:poe-health-oper-data/location/poe-port/port-health
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §46. CEF / FIB State ---
telemetry ietf subscription 1046
 encoding encode-kvgpb
 filter xpath /fib-ios-xe-oper:fib-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §49. BGP Neighbor Detail ---
telemetry ietf subscription 1049
 encoding encode-kvgpb
 filter xpath /bgp-nbr-ios-xe-oper:bgp-nbr-oper-data
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §53. IS-IS Interface Detail ---
telemetry ietf subscription 1053
 encoding encode-kvgpb
 filter xpath /isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §54. Multicast Routing State ---
telemetry ietf subscription 1054
 encoding encode-kvgpb
 filter xpath /mroute-ios-xe-oper:mroute-oper-data/mroute-state
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §55. Stack Member / Stackwise Virtual Detail ---
telemetry ietf subscription 1055
 encoding encode-kvgpb
 filter xpath /stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §56. Tunnel Interface State ---
telemetry ietf subscription 1056
 encoding encode-kvgpb
 filter xpath /ios-tunnel-oper:tunnel-oper-data/tunnel-if
 stream yang-push
 update-policy periodic 6000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! COOL TIER — 300-second polling (30000 centiseconds)
! Inventory, slow-changing state, security features
! ============================================================

! --- §10. VLANs ---
telemetry ietf subscription 1010
 encoding encode-kvgpb
 filter xpath /vlan-ios-xe-oper:vlans
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §11. MAC Address Table (MATM) ---
telemetry ietf subscription 1011
 encoding encode-kvgpb
 filter xpath /matm-ios-xe-oper:matm-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §12. ARP Table ---
telemetry ietf subscription 1012
 encoding encode-kvgpb
 filter xpath /arp-ios-xe-oper:arp-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §13. LLDP Neighbors ---
telemetry ietf subscription 1013
 encoding encode-kvgpb
 filter xpath /lldp-ios-xe-oper:lldp-entries
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §14. CDP Neighbors ---
telemetry ietf subscription 1014
 encoding encode-kvgpb
 filter xpath /cdp-ios-xe-oper:cdp-neighbor-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §16. Device Hardware (Uptime, SW Version) ---
telemetry ietf subscription 1016
 encoding encode-kvgpb
 filter xpath /device-hardware-xe-oper:device-hardware-data/device-hardware
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §17. Switchport ---
telemetry ietf subscription 1017
 encoding encode-kvgpb
 filter xpath /switchport-ios-xe-oper:switchport-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §18. Transceiver / Optics ---
telemetry ietf subscription 1018
 encoding encode-kvgpb
 filter xpath /xcvr-ios-xe-oper:transceiver-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §19. UDLD ---
telemetry ietf subscription 1019
 encoding encode-kvgpb
 filter xpath /udld-ios-xe-oper:udld-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §20. 802.1X / Identity Sessions ---
telemetry ietf subscription 1020
 encoding encode-kvgpb
 filter xpath /identity-ios-xe-oper:identity-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §21. TCAM Utilization ---
telemetry ietf subscription 1021
 encoding encode-kvgpb
 filter xpath /tcam-ios-xe-oper:tcam-details
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §22. MDT Subscription Health ---
telemetry ietf subscription 1022
 encoding encode-kvgpb
 filter xpath /mdt-oper-v2:mdt-oper-v2-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §23. Software Install ---
telemetry ietf subscription 1023
 encoding encode-kvgpb
 filter xpath /install-ios-xe-oper:install-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §26. IETF Routing Table (RIB) ---
telemetry ietf subscription 1026
 encoding encode-kvgpb
 filter xpath /ietf-routing:routing/ribs/rib
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §27. DHCP Pool Stats ---
telemetry ietf subscription 1027
 encoding encode-kvgpb
 filter xpath /dhcp-ios-xe-oper:dhcp-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §28. High Availability State ---
telemetry ietf subscription 1028
 encoding encode-kvgpb
 filter xpath /ha-ios-xe-oper:ha-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §29. Linecard Status ---
telemetry ietf subscription 1029
 encoding encode-kvgpb
 filter xpath /linecard-ios-xe-oper:linecard-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §30. TrustSec (SGT/SXP) ---
telemetry ietf subscription 1030
 encoding encode-kvgpb
 filter xpath /trustsec-ios-xe-oper:trustsec-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §31. LACP / Port-Channel ---
telemetry ietf subscription 1031
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §32. ACL Hit Counters ---
telemetry ietf subscription 1032
 encoding encode-kvgpb
 filter xpath /acl-ios-xe-oper:access-lists/access-list
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §39. AAA / RADIUS / TACACS Statistics ---
telemetry ietf subscription 1039
 encoding encode-kvgpb
 filter xpath /aaa-ios-xe-oper:aaa-data/aaa-radius-stats
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §40. Port Security ---
telemetry ietf subscription 1040
 encoding encode-kvgpb
 filter xpath /psecure-ios-xe-oper:psecure-oper-data/psecure-state
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41a. MACsec Encryption ---
telemetry ietf subscription 1041
 encoding encode-kvgpb
 filter xpath /macsec-ios-xe-oper:macsec-oper-data/macsec-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §41b. MKA Statistics ---
telemetry ietf subscription 1141
 encoding encode-kvgpb
 filter xpath /mka-ios-xe-oper:mka-oper-data/mka-statistics
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §42. VRF Operational State ---
telemetry ietf subscription 1042
 encoding encode-kvgpb
 filter xpath /vrf-ios-xe-oper:vrf-oper-data/vrf-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §43. Data Plane Resources (TCAM/EM per Feature) ---
telemetry ietf subscription 1043
 encoding encode-kvgpb
 filter xpath /dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §47. EIGRP Routing ---
telemetry ietf subscription 1047
 encoding encode-kvgpb
 filter xpath /eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §48. IS-IS Routing ---
telemetry ietf subscription 1048
 encoding encode-kvgpb
 filter xpath /isis-ios-xe-oper:isis-oper-data/isis-instance
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §50. BGP RIB Detail ---
telemetry ietf subscription 1050
 encoding encode-kvgpb
 filter xpath /bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §51. High-Scale ARP ---
telemetry ietf subscription 1051
 encoding encode-kvgpb
 filter xpath /ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §52. IPv6 Neighbor Discovery ---
telemetry ietf subscription 1052
 encoding encode-kvgpb
 filter xpath /ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! --- §57. YANG Management Plane Interfaces ---
telemetry ietf subscription 1057
 encoding encode-kvgpb
 filter xpath /yang-interfaces-oper:yang-interfaces-oper-data
 stream yang-push
 update-policy periodic 30000
 receiver ip address RECEIVER_IP RECEIVER_PORT protocol grpc-tcp

! ============================================================
! Verification Commands
! ============================================================
! show telemetry ietf subscription all
! show telemetry ietf subscription 1001 detail
! show telemetry ietf subscription 1001 receiver
! show telemetry internal connection
! show telemetry internal sensor subscription 1001
```

### Subscription Summary Table

| Sub ID | § | Feature | filter xpath | Interval |
|--------|---|---------|-------------|----------|
| 1001 | 1 | CPU Utilization | `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization` | 30s |
| 1002 | 2 | Memory Statistics | `/memory-ios-xe-oper:memory-statistics/memory-statistic` | 60s |
| 1003 | 3 | Process Memory | `/process-memory-ios-xe-oper:memory-usage-processes` | 30s |
| 1004 | 4 | System DRAM | `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes` | 60s |
| 1005 | 5 | Environment Sensors | `/environment-ios-xe-oper:environment-sensors` | 60s |
| 1006 | 6 | PoE | `/poe-ios-xe-oper:poe-oper-data` | 60s |
| 1007 | 7 | Interfaces | `/interfaces-ios-xe-oper:interfaces/interface` | 30s |
| 1008 | 8 | STP | `/stp-ios-xe-oper:stp-details` | 60s |
| 1009 | 9 | Stack | `/stack-ios-xe-oper:stack-oper-data` | 60s |
| 1010 | 10 | VLANs | `/vlan-ios-xe-oper:vlans` | 300s |
| 1011 | 11 | MATM | `/matm-ios-xe-oper:matm-oper-data` | 300s |
| 1012 | 12 | ARP | `/arp-ios-xe-oper:arp-data` | 300s |
| 1013 | 13 | LLDP | `/lldp-ios-xe-oper:lldp-entries` | 300s |
| 1014 | 14 | CDP | `/cdp-ios-xe-oper:cdp-neighbor-details` | 300s |
| 1015 | 15 | Platform Components | `/platform-ios-xe-oper:components` | 60s |
| 1016 | 16 | Device Hardware | `/device-hardware-xe-oper:device-hardware-data/device-hardware` | 300s |
| 1017 | 17 | Switchport | `/switchport-ios-xe-oper:switchport-oper-data` | 300s |
| 1018 | 18 | Transceiver | `/xcvr-ios-xe-oper:transceiver-oper-data` | 300s |
| 1019 | 19 | UDLD | `/udld-ios-xe-oper:udld-oper-data` | 300s |
| 1020 | 20 | Identity/802.1X | `/identity-ios-xe-oper:identity-oper-data` | 300s |
| 1021 | 21 | TCAM | `/tcam-ios-xe-oper:tcam-details` | 300s |
| 1022 | 22 | MDT Health | `/mdt-oper-v2:mdt-oper-v2-data` | 300s |
| 1023 | 23 | Software Install | `/install-ios-xe-oper:install-oper-data` | 300s |
| 1024 | 24 | BGP | `/bgp-ios-xe-oper:bgp-state-data` | 60s |
| 1025 | 25 | OSPF | `/ospf-ios-xe-oper:ospf-oper-data` | 60s |
| 1026 | 26 | IETF Routing/RIB | `/ietf-routing:routing/ribs/rib` | 300s |
| 1027 | 27 | DHCP | `/dhcp-ios-xe-oper:dhcp-oper-data` | 300s |
| 1028 | 28 | HA State | `/ha-ios-xe-oper:ha-oper-data` | 300s |
| 1029 | 29 | Linecard | `/linecard-ios-xe-oper:linecard-oper-data` | 300s |
| 1030 | 30 | TrustSec | `/trustsec-ios-xe-oper:trustsec-state` | 300s |
| 1031 | 31 | LACP/Port-Channel | `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state` | 300s |
| 1032 | 32 | ACL Counters | `/acl-ios-xe-oper:access-lists/access-list` | 300s |
| 1033 | 33 | NTP | `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info` | 60s |
| 1034 | 34 | BFD | `/bfd-ios-xe-oper:bfd-state/sessions` | 60s |
| 1035 | 35 | HSRP | `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info` | 60s |
| 1036 | 36 | VRRP | `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state` | 60s |
| 1037 | 37 | Flow Monitor | `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor` | 60s |
| 1038 | 38 | IP SLA | `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry` | 60s |
| 1039 | 39 | AAA/RADIUS | `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats` | 300s |
| 1040 | 40 | Port Security | `/psecure-ios-xe-oper:psecure-oper-data/psecure-state` | 300s |
| 1041 | 41a | MACsec | `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics` | 300s |
| 1141 | 41b | MKA | `/mka-ios-xe-oper:mka-oper-data/mka-statistics` | 300s |
| 1042 | 42 | VRF | `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry` | 300s |
| 1043 | 43 | DP Resources | `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource` | 300s |
| 1044 | 44 | Punt/Inject | `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats` | 30s |
| 1045 | 45 | PoE Health | `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health` | 60s |
| 1046 | 46 | CEF/FIB | `/fib-ios-xe-oper:fib-oper-data` | 60s |
| 1047 | 47 | EIGRP | `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance` | 300s |
| 1048 | 48 | IS-IS | `/isis-ios-xe-oper:isis-oper-data/isis-instance` | 300s |
| 1049 | 49 | BGP Neighbor Detail | `/bgp-nbr-ios-xe-oper:bgp-nbr-oper-data` | 60s |
| 1050 | 50 | BGP RIB Detail | `/bgp-ios-rib-xe-oper:bgp-rib-oper-data/bgp-route` | 300s |
| 1051 | 51 | High-Scale ARP | `/ip-arp-ios-xe-oper:ip-arp-oper-data/ni-ip-arp/ip-arp-entry` | 300s |
| 1052 | 52 | IPv6 Neighbor Discovery | `/ipv6-nd-ios-xe-oper:ipv6-nd-oper-data/ni-ipv6-nd/ipv6-nd-entry` | 300s |
| 1053 | 53 | IS-IS Interface Detail | `/isis-intf-ios-xe-oper:isis-intf-oper-data/isis-if-tag-type` | 60s |
| 1054 | 54 | Multicast Routing State | `/mroute-ios-xe-oper:mroute-oper-data/mroute-state` | 60s |
| 1055 | 55 | Stack Member / Stackwise Virtual Detail | `/stack-member-ios-xe-oper:stack-member-oper-data/location/stack-member-info` | 60s |
| 1056 | 56 | Tunnel Interface State | `/ios-tunnel-oper:tunnel-oper-data/tunnel-if` | 60s |
| 1057 | 57 | YANG Management Plane Interfaces | `/yang-interfaces-oper:yang-interfaces-oper-data` | 300s |

---

## On-Change Capable Features

These features support on-change telemetry via mdt-capabilities-oper (periodic-only decision stands, but documented for future):

`/platform-ios-xe-oper:components`, `/poe-ios-xe-oper:poe-oper-data`, `/stacking-ios-xe-oper:stacking-oper-data`, `/vlan-ios-xe-oper:vlans`, `/xcvr-ios-xe-oper:transceiver-oper-data`, `/trustsec-ios-xe-oper:trustsec-state`, `/ha-ios-xe-oper:ha-oper-data`, `/linecard-ios-xe-oper:linecard-oper-data`, `/cdp-ios-xe-oper:cdp-neighbor-details`, `/interfaces-ios-xe-oper:interfaces/interface`, `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

---

## Reference Links

- **MDT White Paper:** http://cs.co/mdtwp
- **Grafana Device Health Dashboard 13462:** https://grafana.com/grafana/dashboards/13462
- **Grafana PoE Dashboard 17238:** https://grafana.com/grafana/dashboards/17238-catalyst-poe-dashboard/
- **MDT GitHub (TIG):** https://github.com/jeremycohoe/cisco-ios-xe-mdt
- **MDT PoE GitHub:** https://github.com/jeremycohoe/cisco-mdt-poe
- **OTEL Receiver GitHub:** https://github.com/jeremycohoe/otel-grpc-cisco-receiver
- **IOS XE DevNet:** https://developer.cisco.com/iosxe/
- **YANG Models on GitHub:** https://github.com/YangModels/yang/tree/main/vendor/cisco/xe
- **SNMP OID to YANG XPath Mapping CSV:** https://github.com/YangModels/yang/blob/main/vendor/cisco/xe/17181/iosxe-snmp-OID-xpath-mapping.csv
- **IOS XE OpenAPI Swagger:** https://jeremycohoe.github.io/cisco-ios-xe-openapi-swagger/
- **dCloud Lab:** https://dcloud2.cisco.com/demo/catalyst-9000-ios-xe-programmability-automation-lab-v1
- **MDT Config Guide:** https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1718/b-1718-programmability-cg/model-driven-telemetry.html

---

## YANG Structure to Splunk Field Mapping Guide

This section explains how the RFC 7950 YANG constructs (containers, lists, keys, leaves, leaf-lists) map to Splunk fields when telemetry data arrives via gRPC dial-out with kvGPB encoding.

### How gRPC kvGPB Flattens the YANG Tree

When IOS XE streams a YANG model via kvGPB (key-value Google Protocol Buffers), the hierarchical YANG tree is flattened into a set of key-value pairs per telemetry message:

- **Keys** from YANG `list` nodes become **dimension fields** — they identify _which_ instance the metrics belong to
- **Leaves** (non-key) become **metric fields** — they carry the actual values
- **Nested containers** have their leaf names prefixed with the container path, using `/` as separator
- **Each list entry** produces a separate telemetry message row — one row per unique key combination

### YANG Construct → Splunk Field Mapping

| YANG Construct | kvGPB Behavior | Splunk Index Strategy | Splunk Queries |
|---------------|----------------|----------------------|----------------|
| **`container`** (top-level) | Defines the XPath subscription path | Becomes the `source` or is embedded in the metric name prefix | Filter by `source="/xpath..."` |
| **`list` with `key`** | Each list entry = one telemetry row; key fields are sent as string fields | Key values → **dimensions** in the Metrics Index (indexed fields for fast filtering) | `| mstats ... WHERE interface_name="GigabitEthernet1/0/1"` |
| **`leaf` (non-key, numeric)** | Sent as a numeric value | → **metric_name** in Metrics Index (e.g., `metric_name:in_octets`) | `| mstats avg(in_octets) WHERE ...` |
| **`leaf` (non-key, string/enum)** | Sent as a string value | → **dimension** field (indexed string for filtering, not a metric) | `WHERE oper_status="if-oper-state-ready"` |
| **`leaf-list`** | Repeated values sent as array | → multi-value dimension field or joined string | Use `mvcount()` or `mvindex()` in SPL |
| **Nested `container`** | Leaves prefixed with container name in field path | Field name = `parent_container/leaf_name` or flattened with underscore | `statistics/in_octets` or `statistics_in_octets` depending on collector |
| **Nested `list` inside `list`** | Produces separate rows with both parent and child keys | Both parent and child keys become dimensions; child metrics are in the child rows | Join parent+child keys or use subsearch |
| **`choice`/`case`** | Only the active case leaves are present | Handle absent fields with `coalesce()` or `if(isnotnull(...))` | Different panels per case, or unified with coalesce |

### Practical Examples

#### Example 1: Simple Container (CPU Utilization)
```
YANG tree:
  container cpu-usage
    └─ container cpu-utilization
         ├─ leaf five-seconds (uint8)
         ├─ leaf one-minute (uint8)
         └─ leaf five-minutes (uint8)
```

**Splunk Metrics Index mapping:**
- No keys → one row per switch per poll interval
- `metric_name:five_seconds`, `metric_name:one_minute`, `metric_name:five_minutes`
- Dimension: `source` (switch hostname/IP from telemetry header)

**SPL query:**
```spl
| mstats avg(five_seconds) prestats=true WHERE index=cisco_mdt source="*cpu-usage*"
  BY host span=1m
| timechart avg(five_seconds) BY host
```

#### Example 2: Keyed List (Interface Statistics)
```
YANG tree:
  container interfaces
    └─ list interface [key: name]
         ├─ leaf name (string) ← KEY → dimension
         ├─ leaf oper-status (enum) ← string → dimension
         └─ container statistics
              ├─ leaf in-octets (uint64) ← numeric → metric
              ├─ leaf out-octets (uint64) ← numeric → metric
              ├─ leaf in-errors (uint64) ← numeric → metric
              └─ leaf out-errors (uint64) ← numeric → metric
```

**Splunk Metrics Index mapping:**
- One row per `name` (interface) per poll → each interface is a separate event
- Key `name` → dimension field `name` (e.g., "GigabitEthernet1/0/1")
- `oper-status` → dimension field (string, filterable)
- `statistics/in-octets` → `metric_name:statistics/in_octets` (numeric metric)

**SPL query — Rate calculation (delta per second):**
```spl
| mstats rate(statistics/in_octets) AS rx_bps prestats=true
  WHERE index=cisco_mdt source="*interfaces*" name="GigabitEthernet1/0/*"
  BY host, name span=1m
| timechart avg(rx_bps) BY name
```

#### Example 3: Multi-Key List (Environment Sensors)
```
YANG tree:
  container environment-sensors
    └─ list environment-sensor [key: name, location]
         ├─ leaf name (string) ← KEY
         ├─ leaf location (string) ← KEY
         ├─ leaf state (string) ← dimension
         ├─ leaf current-reading (uint32) ← metric
         ├─ leaf sensor-units (enum) ← dimension
         └─ leaf sensor-name (enum) ← dimension
```

**Splunk Metrics Index mapping:**
- Composite key: `name` + `location` → both are dimensions
- Filter by `sensor_name="temperature"` to isolate temperature sensors
- `current-reading` is the metric; `sensor-units` tells you the unit (celsius, watts, rpm, etc.)

**SPL query — Temperature sensors only:**
```spl
| mstats latest(current_reading) AS reading prestats=true
  WHERE index=cisco_mdt source="*environment*" sensor_name="temperature"
  BY host, name, location span=5m
| timechart latest(reading) BY name
```

#### Example 4: Deeply Nested List (STP per-instance per-interface)
```
YANG tree:
  container stp-details
    └─ list stp-detail [key: instance]
         ├─ leaf instance (string) ← KEY (e.g., VLAN0100)
         ├─ leaf bridge-priority (uint32) ← metric
         └─ container interfaces
              └─ list interface [key: name]
                   ├─ leaf name (string) ← KEY
                   ├─ leaf role (enum) ← dimension
                   ├─ leaf state (enum) ← dimension
                   └─ leaf cost (uint64) ← metric
```

**Splunk handling of nested lists:**
- The subscription XPath determines what level of data you get
- Subscribe to `/stp-ios-xe-oper:stp-details/stp-detail` → get instance-level data
- Subscribe to `/stp-ios-xe-oper:stp-details/stp-detail/interfaces/interface` → get per-interface data with both `instance` (parent key) and `name` (child key) as dimensions
- Best practice: Subscribe at the deepest list level you need metrics from; parent keys are included automatically

**SPL query — STP port states:**
```spl
| mstats latest(cost) prestats=true
  WHERE index=cisco_mdt source="*stp*"
  BY host, instance, name, role, state span=5m
| stats latest(cost) AS cost, latest(role) AS role, latest(state) AS state
  BY host, instance, name
| where state="stp-blocking"
```

#### Example 5: Location-Keyed Platform Data (DP Resources)
```
YANG tree:
  container switch-dp-resources-oper-data
    └─ list location [key: fru, slot, bay, chassis, node]
         └─ list dp-feature-resource [key: feature, protocol, direction]
              ├─ leaf max-tcam-percentage-used (decimal64) ← metric
              └─ leaf max-em-percentage-used (decimal64) ← metric
```

**Splunk handling of 5-part composite keys:**
- All 5 location keys + 3 feature keys = 8 dimension fields per row
- For C9300 stacks, `chassis` differentiates stack members
- In SPL, filter or group by the relevant dimension:

```spl
| mstats max(max_tcam_percentage_used) AS tcam_pct prestats=true
  WHERE index=cisco_mdt source="*dp-resources*"
  BY host, chassis, feature, protocol span=5m
| timechart max(tcam_pct) BY feature
```

### Key Splunk Best Practices for YANG Telemetry

1. **Use Metrics Index (MPREFIX), not Events Index** — telemetry is high-volume numeric data; Metrics Index is 10x more efficient for storage and query speed

2. **Map YANG keys to Splunk dimensions** — Every YANG `list` key should be indexed as a dimension field in the Metrics Index. This enables fast `WHERE` filtering without full event scanning

3. **Map numeric leaves to metric_name** — Use `metric_name:leaf_path` format. The OTel collector typically handles this mapping

4. **Map string/enum leaves to dimensions** — Enum values like `oper-status`, `state`, `role` are string dimensions, not metrics. Use them in `WHERE` clauses and `BY` groupings

5. **Rate calculations for counters** — Most counter64 values (in-octets, match-counter, etc.) are monotonically increasing. Use `| mstats rate(metric) ...` to compute per-second rates, or `| mstats latest(metric) ...` and calculate delta manually

6. **Handle absent fields** — Not all leaves are always present (e.g., `choice`/`case` in YANG, or sensors that don't exist on a platform). Use `coalesce()` or `isnotnull()` guards

7. **Composite keys need all parts** — When a YANG list has multi-part keys (e.g., `name + location` for environment sensors), you need all key fields in your `BY` clause to avoid incorrect aggregation

8. **Subscription XPath depth determines data** — Subscribing to a parent container gets all child data but may be too broad. Subscribing to a specific nested list gets only that data with parent keys included. Choose the narrowest XPath that covers your needed KPIs

9. **Field name encoding** — The gRPC-to-Splunk pipeline (OTel collector) may transform field names: `/` → `_` or `.`, YANG hyphens → underscores. Verify actual field names in Splunk with `| mstats list(_dims)` after first data arrives

10. **Leaf-list handling** — YANG `leaf-list` (e.g., VRF member interfaces) becomes a multi-value field. Use `mvcount()` to count members, `mvindex()` to extract specific values, or `mvexpand()` to create one row per value

---

## Excluded (per scope)

- Wireless — not relevant for switching demo
- On-change / event-driven subscriptions — periodic only in this phase

