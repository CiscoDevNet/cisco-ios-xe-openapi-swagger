#!/usr/bin/env python3
"""Generate CLI & RESTCONF reference markdown from collected RESTCONF samples."""

import json

import os

SAMPLES_FILE = "validation/results/restconf-samples.json"
OUTPUT_FILE = "cli-reference.md"
HOST = os.environ.get("MDT_HOST", "your-switch.example.com")

SECTIONS = [
    {
        "num": 1, "title": "CPU Utilization",
        "yang": "Cisco-IOS-XE-process-cpu-oper.yang",
        "xpath": "/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization",
        "restconf": "Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization",
        "show_cmds": ["show processes cpu", "show processes cpu history", "show processes cpu sorted"],
    },
    {
        "num": 2, "title": "Memory Statistics",
        "yang": "Cisco-IOS-XE-memory-oper.yang",
        "xpath": "/memory-ios-xe-oper:memory-statistics/memory-statistic",
        "restconf": "Cisco-IOS-XE-memory-oper:memory-statistics",
        "show_cmds": ["show memory statistics", "show memory platform"],
    },
    {
        "num": 3, "title": "Process Memory",
        "yang": "Cisco-IOS-XE-process-memory-oper.yang",
        "xpath": "/process-memory-ios-xe-oper:memory-usage-processes",
        "restconf": "Cisco-IOS-XE-process-memory-oper:memory-usage-processes",
        "show_cmds": ["show processes memory sorted", "show processes memory"],
    },
    {
        "num": 4, "title": "System DRAM (Platform Software)",
        "yang": "Cisco-IOS-XE-platform-software-oper.yang",
        "xpath": "/platform-sw-ios-xe-oper:cisco-platform-software/control-processes",
        "restconf": "Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes",
        "show_cmds": ["show platform software status control-processor brief", "show platform software process slot switch active R0 monitor"],
    },
    {
        "num": 5, "title": "Environment Sensors",
        "yang": "Cisco-IOS-XE-environment-oper.yang",
        "xpath": "/environment-ios-xe-oper:environment-sensors",
        "restconf": "Cisco-IOS-XE-environment-oper:environment-sensors",
        "show_cmds": ["show environment all", "show environment temperature", "show environment power", "show environment fan"],
    },
    {
        "num": 6, "title": "Power over Ethernet (PoE)",
        "yang": "Cisco-IOS-XE-poe-oper.yang",
        "xpath": "/poe-ios-xe-oper:poe-oper-data",
        "restconf": "Cisco-IOS-XE-poe-oper:poe-oper-data",
        "show_cmds": ["show power inline", "show power inline detail", "show power inline consumption"],
    },
    {
        "num": 7, "title": "Interface Statistics",
        "yang": "Cisco-IOS-XE-interfaces-oper.yang",
        "xpath": "/interfaces-ios-xe-oper:interfaces/interface",
        "restconf": "Cisco-IOS-XE-interfaces-oper:interfaces/interface",
        "show_cmds": ["show interfaces", "show interfaces status", "show interfaces counters", "show interfaces counters errors"],
    },
    {
        "num": 8, "title": "Spanning Tree Protocol (STP)",
        "yang": "Cisco-IOS-XE-spanning-tree-oper.yang",
        "xpath": "/stp-ios-xe-oper:stp-details",
        "restconf": "Cisco-IOS-XE-spanning-tree-oper:stp-details",
        "show_cmds": ["show spanning-tree", "show spanning-tree summary", "show spanning-tree detail"],
    },
    {
        "num": 9, "title": "Stack Health",
        "yang": "Cisco-IOS-XE-stack-oper.yang",
        "xpath": "/stack-ios-xe-oper:stack-oper-data",
        "restconf": "Cisco-IOS-XE-stack-oper:stack-oper-data",
        "show_cmds": ["show switch", "show switch stack-ports", "show switch stack-ring speed"],
    },
    {
        "num": 10, "title": "VLANs",
        "yang": "Cisco-IOS-XE-vlan-oper.yang",
        "xpath": "/vlan-ios-xe-oper:vlans",
        "restconf": "Cisco-IOS-XE-vlan-oper:vlans",
        "show_cmds": ["show vlan brief", "show vlan"],
    },
    {
        "num": 11, "title": "MAC Address Table",
        "yang": "Cisco-IOS-XE-matm-oper.yang",
        "xpath": "/matm-ios-xe-oper:matm-oper-data",
        "restconf": "Cisco-IOS-XE-matm-oper:matm-oper-data",
        "show_cmds": ["show mac address-table", "show mac address-table count"],
    },
    {
        "num": 12, "title": "ARP Table",
        "yang": "Cisco-IOS-XE-arp-oper.yang",
        "xpath": "/arp-ios-xe-oper:arp-data",
        "restconf": "Cisco-IOS-XE-arp-oper:arp-data",
        "show_cmds": ["show arp", "show ip arp"],
    },
    {
        "num": 13, "title": "LLDP Neighbors",
        "yang": "Cisco-IOS-XE-lldp-oper.yang",
        "xpath": "/lldp-ios-xe-oper:lldp-entries",
        "restconf": "Cisco-IOS-XE-lldp-oper:lldp-entries/lldp-entry",
        "show_cmds": ["show lldp neighbors", "show lldp neighbors detail"],
    },
    {
        "num": 14, "title": "CDP Neighbors",
        "yang": "Cisco-IOS-XE-cdp-oper.yang",
        "xpath": "/cdp-ios-xe-oper:cdp-neighbor-details",
        "restconf": "Cisco-IOS-XE-cdp-oper:cdp-neighbor-details",
        "show_cmds": ["show cdp neighbors", "show cdp neighbors detail"],
    },
    {
        "num": 15, "title": "Platform Components",
        "yang": "Cisco-IOS-XE-platform-oper.yang",
        "xpath": "/platform-ios-xe-oper:components",
        "restconf": "Cisco-IOS-XE-platform-oper:components",
        "show_cmds": ["show platform", "show inventory"],
    },
    {
        "num": 16, "title": "Device Hardware",
        "yang": "Cisco-IOS-XE-device-hardware-oper.yang",
        "xpath": "/device-hardware-xe-oper:device-hardware-data/device-hardware",
        "restconf": "Cisco-IOS-XE-device-hardware-oper:device-hardware-data/device-hardware",
        "show_cmds": ["show version", "show inventory", "show platform software device-hardware"],
    },
    {
        "num": 17, "title": "Switchport",
        "yang": "Cisco-IOS-XE-switchport-oper.yang",
        "xpath": "/switchport-ios-xe-oper:switchport-oper-data",
        "restconf": "Cisco-IOS-XE-switchport-oper:switchport-oper-data",
        "show_cmds": ["show interfaces switchport", "show interfaces trunk"],
    },
    {
        "num": 18, "title": "Transceiver / Optics",
        "yang": "Cisco-IOS-XE-transceiver-oper.yang",
        "xpath": "/xcvr-ios-xe-oper:transceiver-oper-data",
        "restconf": "Cisco-IOS-XE-transceiver-oper:transceiver-oper-data",
        "show_cmds": ["show interfaces transceiver", "show interfaces transceiver detail"],
    },
    {
        "num": 19, "title": "UDLD",
        "yang": "Cisco-IOS-XE-udld-oper.yang",
        "xpath": "/udld-ios-xe-oper:udld-oper-data",
        "restconf": "Cisco-IOS-XE-udld-oper:udld-oper-data",
        "show_cmds": ["show udld", "show udld neighbors"],
    },
    {
        "num": 20, "title": "802.1X / Identity Sessions",
        "yang": "Cisco-IOS-XE-identity-oper.yang",
        "xpath": "/identity-ios-xe-oper:identity-oper-data",
        "restconf": "Cisco-IOS-XE-identity-oper:identity-oper-data",
        "show_cmds": ["show dot1x all summary", "show authentication sessions", "show access-session"],
    },
    {
        "num": 21, "title": "TCAM Utilization",
        "yang": "Cisco-IOS-XE-tcam-oper.yang",
        "xpath": "/tcam-ios-xe-oper:tcam-details",
        "restconf": "Cisco-IOS-XE-tcam-oper:tcam-details",
        "show_cmds": ["show platform hardware fed switch active fwd-asic resource tcam utilization", "show sdm prefer"],
    },
    {
        "num": 22, "title": "MDT Subscription Health",
        "yang": "Cisco-IOS-XE-mdt-oper-v2.yang",
        "xpath": "/mdt-oper-v2:mdt-oper-v2-data",
        "restconf": "Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data",
        "show_cmds": ["show telemetry ietf subscription all", "show telemetry ietf subscription all detail", "show telemetry connection all"],
    },
    {
        "num": 23, "title": "Software Install",
        "yang": "Cisco-IOS-XE-install-oper.yang",
        "xpath": "/install-ios-xe-oper:install-oper-data",
        "restconf": "Cisco-IOS-XE-install-oper:install-oper-data",
        "show_cmds": ["show install summary", "show version"],
    },
    {
        "num": 24, "title": "BGP State",
        "yang": "Cisco-IOS-XE-bgp-oper.yang",
        "xpath": "/bgp-ios-xe-oper:bgp-state-data",
        "restconf": "Cisco-IOS-XE-bgp-oper:bgp-state-data",
        "show_cmds": ["show bgp summary", "show bgp all summary", "show bgp ipv4 unicast summary"],
    },
    {
        "num": 25, "title": "OSPF State",
        "yang": "Cisco-IOS-XE-ospf-oper.yang",
        "xpath": "/ospf-ios-xe-oper:ospf-oper-data",
        "restconf": "Cisco-IOS-XE-ospf-oper:ospf-oper-data",
        "show_cmds": ["show ip ospf", "show ip ospf neighbor", "show ip ospf interface brief"],
    },
    {
        "num": 26, "title": "IETF Routing Table (RIB)",
        "yang": "ietf-routing.yang",
        "xpath": "/ietf-routing:routing-state",
        "restconf": "ietf-routing:routing-state",
        "show_cmds": ["show ip route", "show ip route summary", "show ipv6 route"],
    },
    {
        "num": 27, "title": "DHCP Pool Stats",
        "yang": "Cisco-IOS-XE-dhcp-oper.yang",
        "xpath": "/dhcp-ios-xe-oper:dhcp-oper-data",
        "restconf": "Cisco-IOS-XE-dhcp-oper:dhcp-oper-data",
        "show_cmds": ["show ip dhcp pool", "show ip dhcp binding", "show ip dhcp statistics"],
    },
    {
        "num": 28, "title": "High Availability State",
        "yang": "Cisco-IOS-XE-ha-oper.yang",
        "xpath": "/ha-ios-xe-oper:ha-oper-data",
        "restconf": "Cisco-IOS-XE-ha-oper:ha-oper-data",
        "show_cmds": ["show redundancy", "show redundancy states"],
    },
    {
        "num": 29, "title": "Linecard Status",
        "yang": "Cisco-IOS-XE-linecard-oper.yang",
        "xpath": "/linecard-ios-xe-oper:linecard-oper-data",
        "restconf": "Cisco-IOS-XE-linecard-oper:linecard-oper-data",
        "show_cmds": ["show platform", "show module"],
    },
    {
        "num": 30, "title": "TrustSec (SGT/SXP)",
        "yang": "Cisco-IOS-XE-trustsec-oper.yang",
        "xpath": "/trustsec-ios-xe-oper:trustsec-state",
        "restconf": "Cisco-IOS-XE-trustsec-oper:trustsec-state",
        "show_cmds": ["show cts environment-data", "show cts role-based sgt-map all", "show cts sxp connections brief"],
    },
    {
        "num": 31, "title": "LACP / Port-Channel",
        "yang": "Cisco-IOS-XE-interfaces-oper.yang",
        "xpath": "/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state",
        "restconf": "Cisco-IOS-XE-interfaces-oper:interfaces/interface",
        "show_cmds": ["show etherchannel summary", "show lacp neighbor", "show lacp counters"],
    },
    {
        "num": 32, "title": "ACL Hit Counters",
        "yang": "Cisco-IOS-XE-acl-oper.yang",
        "xpath": "/acl-ios-xe-oper:access-lists/access-list",
        "restconf": "Cisco-IOS-XE-acl-oper:access-lists",
        "show_cmds": ["show access-lists", "show ip access-lists"],
    },
    {
        "num": 33, "title": "NTP Synchronization",
        "yang": "Cisco-IOS-XE-ntp-oper.yang",
        "xpath": "/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info",
        "restconf": "Cisco-IOS-XE-ntp-oper:ntp-oper-data/ntp-status-info",
        "show_cmds": ["show ntp status", "show ntp associations", "show ntp associations detail"],
    },
    {
        "num": 34, "title": "BFD Sessions",
        "yang": "Cisco-IOS-XE-bfd-oper.yang",
        "xpath": "/bfd-ios-xe-oper:bfd-state/sessions",
        "restconf": "Cisco-IOS-XE-bfd-oper:bfd-state/sessions",
        "show_cmds": ["show bfd neighbors", "show bfd neighbors details"],
    },
    {
        "num": 35, "title": "HSRP State",
        "yang": "Cisco-IOS-XE-hsrp-oper.yang",
        "xpath": "/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info",
        "restconf": "Cisco-IOS-XE-hsrp-oper:hsrp-oper-data/hsrp-group-info",
        "show_cmds": ["show standby", "show standby brief"],
    },
    {
        "num": 36, "title": "VRRP State",
        "yang": "Cisco-IOS-XE-vrrp-oper.yang",
        "xpath": "/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state",
        "restconf": "Cisco-IOS-XE-vrrp-oper:vrrp-oper-data/vrrp-oper-state",
        "show_cmds": ["show vrrp", "show vrrp brief"],
    },
    {
        "num": 37, "title": "Flexible NetFlow / Flow Monitor",
        "yang": "Cisco-IOS-XE-flow-monitor-oper.yang",
        "xpath": "/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor",
        "restconf": "Cisco-IOS-XE-flow-monitor-oper:flow-monitors/flow-monitor",
        "show_cmds": ["show flow monitor", "show flow monitor statistics"],
    },
    {
        "num": 38, "title": "IP SLA Probes",
        "yang": "Cisco-IOS-XE-ip-sla-oper.yang",
        "xpath": "/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry",
        "restconf": "Cisco-IOS-XE-ip-sla-oper:ip-sla-stats/sla-oper-entry",
        "show_cmds": ["show ip sla statistics", "show ip sla summary"],
    },
    {
        "num": 39, "title": "AAA / RADIUS / TACACS Statistics",
        "yang": "Cisco-IOS-XE-aaa-oper.yang",
        "xpath": "/aaa-ios-xe-oper:aaa-data/aaa-radius-stats",
        "restconf": "Cisco-IOS-XE-aaa-oper:aaa-data/aaa-radius-stats",
        "show_cmds": ["show aaa servers", "show radius statistics"],
    },
    {
        "num": 40, "title": "Port Security",
        "yang": "Cisco-IOS-XE-psecure-oper.yang",
        "xpath": "/psecure-ios-xe-oper:psecure-oper-data/psecure-state",
        "restconf": "Cisco-IOS-XE-psecure-oper:psecure-oper-data/psecure-state",
        "show_cmds": ["show port-security", "show port-security address"],
    },
    {
        "num": 41, "title": "MACsec / MKA Encryption",
        "yang": "Cisco-IOS-XE-macsec-oper.yang + Cisco-IOS-XE-mka-oper.yang",
        "xpath": "/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics",
        "restconf": "Cisco-IOS-XE-macsec-oper:macsec-oper-data/macsec-statistics",
        "show_cmds": ["show macsec summary", "show macsec interface", "show mka sessions", "show mka statistics"],
    },
    {
        "num": 42, "title": "VRF Operational State",
        "yang": "Cisco-IOS-XE-vrf-oper.yang",
        "xpath": "/vrf-ios-xe-oper:vrf-oper-data/vrf-entry",
        "restconf": "Cisco-IOS-XE-vrf-oper:vrf-oper-data",
        "show_cmds": ["show vrf", "show ip vrf detail"],
    },
    {
        "num": 43, "title": "Data Plane Resources (TCAM/EM per Feature)",
        "yang": "Cisco-IOS-XE-switch-dp-resources-oper.yang",
        "xpath": "/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource",
        "restconf": "Cisco-IOS-XE-switch-dp-resources-oper:switch-dp-resources-oper-data",
        "show_cmds": ["show platform hardware fed switch active fwd-asic resource tcam utilization", "show platform hardware fed switch active fwd-asic resource utilization"],
    },
    {
        "num": 44, "title": "CPU Punt/Inject Counters",
        "yang": "Cisco-IOS-XE-switch-dp-punt-inject-oper.yang",
        "xpath": "/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats",
        "restconf": "Cisco-IOS-XE-switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data",
        "show_cmds": ["show platform hardware fed switch active qos queue stats internal cpu policer", "show platform software fed switch active punt cpuq all"],
    },
    {
        "num": 45, "title": "PoE Health (Detailed Port-Level)",
        "yang": "Cisco-IOS-XE-poe-health-oper.yang",
        "xpath": "/poe-health-oper:poe-health-oper-data/location/poe-port/port-health",
        "restconf": "Cisco-IOS-XE-poe-health-oper:poe-health-oper-data",
        "show_cmds": ["show power inline detail"],
    },
    {
        "num": 46, "title": "CEF / FIB State",
        "yang": "Cisco-IOS-XE-fib-oper.yang",
        "xpath": "/fib-ios-xe-oper:fib-oper-data",
        "restconf": "Cisco-IOS-XE-fib-oper:fib-oper-data",
        "show_cmds": ["show ip cef summary", "show ip cef", "show adjacency summary"],
    },
    {
        "num": 47, "title": "EIGRP Routing",
        "yang": "Cisco-IOS-XE-eigrp-oper.yang",
        "xpath": "/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance",
        "restconf": "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data/eigrp-instance",
        "show_cmds": ["show ip eigrp neighbors", "show ip eigrp topology"],
    },
    {
        "num": 48, "title": "IS-IS Routing",
        "yang": "Cisco-IOS-XE-isis-oper.yang",
        "xpath": "/isis-ios-xe-oper:isis-oper-data/isis-instance",
        "restconf": "Cisco-IOS-XE-isis-oper:isis-oper-data/isis-instance",
        "show_cmds": ["show isis neighbors", "show isis database"],
    },
]


def main():
    with open(SAMPLES_FILE) as f:
        samples = json.load(f)

    lines = []
    lines.append("# CLI & RESTCONF Reference — Catalyst 9300 MDT Telemetry")
    lines.append("")
    lines.append("Cross-reference of IOS XE **show commands**, **YANG module**, **XPath**, and live **RESTCONF GET** output for each telemetry feature.")
    lines.append("")
    lines.append(f"**Device:** `{HOST}` (C9300-24UX, IOS XE 17.18.2)")
    lines.append("**Collected:** 2026-04-12")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    for s in SECTIONS:
        anchor = "{}-{}".format(
            s["num"],
            s["title"].lower().replace(" ", "-").replace("/", "").replace("(", "").replace(")", "").replace(",", ""),
        )
        lines.append("- [{num}. {title}](#{anchor})".format(num=s["num"], title=s["title"], anchor=anchor))
    lines.append("")
    lines.append("---")
    lines.append("")

    for s in SECTIONS:
        num = s["num"]
        lines.append("## {num}. {title}".format(num=num, title=s["title"]))
        lines.append("")
        lines.append("**YANG Module:** `{}`".format(s["yang"]))
        lines.append("**Telemetry XPath:** `{}`".format(s["xpath"]))
        lines.append("")

        # Show commands
        lines.append("### CLI Show Commands")
        lines.append("")
        lines.append("```")
        for cmd in s["show_cmds"]:
            lines.append(cmd)
        lines.append("```")
        lines.append("")

        # RESTCONF GET
        lines.append("### RESTCONF GET")
        lines.append("")
        lines.append("```bash")
        lines.append('curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \\')
        lines.append('  "https://{host}/restconf/data/{path}"'.format(host=HOST, path=s["restconf"]))
        lines.append("```")
        lines.append("")

        # Sample output
        key = str(num)
        if key in samples:
            sample_data = samples[key]["data"]
            sample_json = json.dumps(sample_data, indent=2)
            # Truncate large samples
            if len(sample_json) > 3000:
                cut = sample_json[:3000].rfind("\n")
                if cut < 2000:
                    cut = 3000
                sample_json = sample_json[:cut] + "\n  ...\n}"
            lines.append("### Sample Output (RESTCONF)")
            lines.append("")
            lines.append("```json")
            lines.append(sample_json)
            lines.append("```")
        else:
            lines.append("### Sample Output")
            lines.append("")
            lines.append("> Feature not active on this device — returns HTTP 204 (empty).")

        lines.append("")
        lines.append("---")
        lines.append("")

    output = "\n".join(lines)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("Wrote {} ({} bytes, {} lines)".format(OUTPUT_FILE, len(output), len(lines)))


if __name__ == "__main__":
    main()
