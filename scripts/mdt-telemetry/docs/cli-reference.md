# CLI & RESTCONF Reference — Catalyst 9300 MDT Telemetry

Cross-reference of IOS XE **show commands**, **YANG module**, **XPath**, and live **RESTCONF GET** output for each telemetry feature.

**Device:** `jcohoe-c9300-2.cisco.com` (C9300-24UX, IOS XE 17.18.2)
**Collected:** 2026-04-12

---

## Table of Contents

- [1. CPU Utilization](#1-cpu-utilization) · [CLI](#1-cli-output) · [RESTCONF](#1-restconf-output)
- [2. Memory Statistics](#2-memory-statistics) · [CLI](#2-cli-output) · [RESTCONF](#2-restconf-output)
- [3. Process Memory](#3-process-memory) · [CLI](#3-cli-output) · [RESTCONF](#3-restconf-output)
- [4. System DRAM (Platform Software)](#4-system-dram-platform-software) · [CLI](#4-cli-output) · [RESTCONF](#4-restconf-output)
- [5. Environment Sensors](#5-environment-sensors) · [CLI](#5-cli-output) · [RESTCONF](#5-restconf-output)
- [6. Power over Ethernet (PoE)](#6-power-over-ethernet-poe) · [CLI](#6-cli-output) · [RESTCONF](#6-restconf-output)
- [7. Interface Statistics](#7-interface-statistics) · [CLI](#7-cli-output) · [RESTCONF](#7-restconf-output)
- [8. Spanning Tree Protocol (STP)](#8-spanning-tree-protocol-stp) · [CLI](#8-cli-output) · [RESTCONF](#8-restconf-output)
- [9. Stack Health](#9-stack-health) · [CLI](#9-cli-output) · [RESTCONF](#9-restconf-output)
- [10. VLANs](#10-vlans) · [CLI](#10-cli-output) · [RESTCONF](#10-restconf-output)
- [11. MAC Address Table](#11-mac-address-table) · [CLI](#11-cli-output) · [RESTCONF](#11-restconf-output)
- [12. ARP Table](#12-arp-table) · [CLI](#12-cli-output) · [RESTCONF](#12-restconf-output)
- [13. LLDP Neighbors](#13-lldp-neighbors) · [CLI](#13-cli-output) · [RESTCONF](#13-restconf-output)
- [14. CDP Neighbors](#14-cdp-neighbors) · [CLI](#14-cli-output) · [RESTCONF](#14-restconf-output)
- [15. Platform Components](#15-platform-components) · [CLI](#15-cli-output) · [RESTCONF](#15-restconf-output)
- [16. Device Hardware](#16-device-hardware) · [CLI](#16-cli-output) · [RESTCONF](#16-restconf-output)
- [17. Switchport](#17-switchport) · [CLI](#17-cli-output) · [RESTCONF](#17-restconf-output)
- [18. Transceiver / Optics](#18-transceiver-optics) · [CLI](#18-cli-output) · [RESTCONF](#18-restconf-output)
- [19. UDLD](#19-udld) · [CLI](#19-cli-output) · [RESTCONF](#19-restconf-output)
- [20. 802.1X / Identity Sessions](#20-8021x-identity-sessions) · [CLI](#20-cli-output) · [RESTCONF](#20-restconf-output)
- [21. TCAM Utilization](#21-tcam-utilization) · [CLI](#21-cli-output) · [RESTCONF](#21-restconf-output)
- [22. MDT Subscription Health](#22-mdt-subscription-health) · [CLI](#22-cli-output) · [RESTCONF](#22-restconf-output)
- [23. Software Install](#23-software-install) · [CLI](#23-cli-output) · [RESTCONF](#23-restconf-output)
- [24. BGP State](#24-bgp-state) · [CLI](#24-cli-output) · [RESTCONF](#24-restconf-output)
- [25. OSPF State](#25-ospf-state) · [CLI](#25-cli-output) · [RESTCONF](#25-restconf-output)
- [26. IETF Routing Table (RIB)](#26-ietf-routing-table-rib) · [CLI](#26-cli-output) · [RESTCONF](#26-restconf-output)
- [27. DHCP Pool Stats](#27-dhcp-pool-stats) · [CLI](#27-cli-output) · [RESTCONF](#27-restconf-output)
- [28. High Availability State](#28-high-availability-state) · [CLI](#28-cli-output) · [RESTCONF](#28-restconf-output)
- [29. Linecard Status](#29-linecard-status) · [CLI](#29-cli-output) · [RESTCONF](#29-restconf-output)
- [30. TrustSec (SGT/SXP)](#30-trustsec-sgtsxp) · [CLI](#30-cli-output) · [RESTCONF](#30-restconf-output)
- [31. LACP / Port-Channel](#31-lacp-port-channel) · [CLI](#31-cli-output) · [RESTCONF](#31-restconf-output)
- [32. ACL Hit Counters](#32-acl-hit-counters) · [CLI](#32-cli-output) · [RESTCONF](#32-restconf-output)
- [33. NTP Synchronization](#33-ntp-synchronization) · [CLI](#33-cli-output) · [RESTCONF](#33-restconf-output)
- [34. BFD Sessions](#34-bfd-sessions) · [CLI](#34-cli-output) · [RESTCONF](#34-restconf-output)
- [35. HSRP State](#35-hsrp-state) · [CLI](#35-cli-output) · [RESTCONF](#35-restconf-output)
- [36. VRRP State](#36-vrrp-state) · [CLI](#36-cli-output) · [RESTCONF](#36-restconf-output)
- [37. Flexible NetFlow / Flow Monitor](#37-flexible-netflow-flow-monitor) · [CLI](#37-cli-output) · [RESTCONF](#37-restconf-output)
- [38. IP SLA Probes](#38-ip-sla-probes) · [CLI](#38-cli-output) · [RESTCONF](#38-restconf-output)
- [39. AAA / RADIUS / TACACS Statistics](#39-aaa-radius-tacacs-statistics) · [CLI](#39-cli-output) · [RESTCONF](#39-restconf-output)
- [40. Port Security](#40-port-security) · [CLI](#40-cli-output) · [RESTCONF](#40-restconf-output)
- [41. MACsec / MKA Encryption](#41-macsec-mka-encryption) · [CLI](#41-cli-output) · [RESTCONF](#41-restconf-output)
- [42. VRF Operational State](#42-vrf-operational-state) · [CLI](#42-cli-output) · [RESTCONF](#42-restconf-output)
- [43. Data Plane Resources (TCAM/EM per Feature)](#43-data-plane-resources-tcamem-per-feature) · [CLI](#43-cli-output) · [RESTCONF](#43-restconf-output)
- [44. CPU Punt/Inject Counters](#44-cpu-puntinject-counters) · [CLI](#44-cli-output) · [RESTCONF](#44-restconf-output)
- [45. PoE Health (Detailed Port-Level)](#45-poe-health-detailed-port-level) · [CLI](#45-cli-output) · [RESTCONF](#45-restconf-output)
- [46. CEF / FIB State](#46-cef-fib-state) · [CLI](#46-cli-output) · [RESTCONF](#46-restconf-output)
- [47. EIGRP Routing](#47-eigrp-routing) · [CLI](#47-cli-output) · [RESTCONF](#47-restconf-output)
- [48. IS-IS Routing](#48-is-is-routing) · [CLI](#48-cli-output) · [RESTCONF](#48-restconf-output)

---

## 1. CPU Utilization

**YANG Module:** `Cisco-IOS-XE-process-cpu-oper.yang`
**Telemetry XPath:** `/process-cpu-ios-xe-oper:cpu-usage/cpu-utilization`

### CLI Show Commands

```
show processes cpu
show processes cpu history
show processes cpu sorted
```

### <a id="1-cli-output"></a>CLI Output

**`show processes cpu`**

```
CPU utilization for five seconds: 1%/0%; one minute: 1%; five minutes: 1%
 PID Runtime(ms)     Invoked      uSecs   5Sec   1Min   5Min TTY Process
   1           3          21        142  0.00%  0.00%  0.00%   0 Chunk Manager
   2       48407      275277        175  0.00%  0.00%  0.00%   0 Load Meter
   3          54         963         56  0.00%  0.00%  0.00%   0 SpanTree Flush
   4         534          17      31411  0.00%  0.00%  0.00%   0 RF Slave Main Th
   5           0           1          0  0.00%  0.00%  0.00%   0 Retransmission o
   6           0           1          0  0.00%  0.00%  0.00%   0 IPC ISSU Dispatc
   7           0           1          0  0.00%  0.00%  0.00%   0 RO Notify Timers
   8         289       45880          6  0.00%  0.00%  0.00%   0 VIDB BACKGD MGR
   9      750379      209638       3579  0.00%  0.04%  0.05%   0 Check heaps
  10        3713       22940        161  0.00%  0.00%  0.00%   0 Pool Manager
  11           0           1          0  0.00%  0.00%  0.00%   0 DiscardQ Backgro
  12           0           2          0  0.00%  0.00%  0.00%   0 Timers
  13          55       11213          4  0.00%  0.00%  0.00%   0 WATCH_AFS
  14           0           3          0  0.00%  0.00%  0.00%   0 DB Lock Manager
  15        9786     1376377          7  0.00%  0.00%  0.00%   0 GraphIt
  16           1           3        333  0.00%  0.00%  0.00%   0 DB Notification
  17      142055    15062264          9  0.00%  0.00%  0.00%   0 DB offload write
  18        5440      688170          7  0.00%  0.00%  0.00%   0 IOSXE heartbeat
  19          11          16        687  0.00%  0.00%  0.00%   0 PrstVbl
  20           0           1          0  0.00%  0.00%  0.00%   0 IPC Apps Task
  21      555503     6042325         91  0.07%  0.03%  0.03%   0 ARP Input
  22       16198     1436484         11  0.00%  0.00%  0.00%   0 ARP Background
  23           0           1          0  0.00%  0.00%  0.00%   0 AAA_SERVER_DEADT
  24           0           1          0  0.00%  0.00%  0.00%   0 Policy Manager
  25           0           2          0  0.00%  0.00%  0.00%   0 DDR Timers
  26          47          35       1342  0.00%  0.00%  0.00%   0 Entity MIB API
  27           0           1          0  0.00%  0.00%  0.00%   0 ifIndex Receive
  28           0           1          0  0.00%  0.00%  0.00%   0 IFS Agent Manage
  29        1593      275274          5  0.00%  0.00%  0.00%   0 IPC Event Notifi
  30       10208     1344025          7  0.00%  0.00%  0.00%   0 IPC Mcast Pendin
  31           0           1          0  0.00%  0.00%  0.00%   0 Platform appsess
  32         151       22940          6  0.00%  0.00%  0.00%   0 IPC Dynamic Cach
  33        1797      275274          6  0.00%  0.00%  0.00%   0 IPC Service NonC
  34           0           1          0  0.00%  0.00%  0.00%   0 IPC Zone Manager
  35       11183     1344024          8  0.00%  0.00%  0.00%   0 IPC Periodic Tim
  36        9186     1344024          6  0.00%  0.00%  0.00%   0 IPC Deferred Por
  37           0           1          0  0.00%  0.00%  0.00%   0 IPC Process leve
  38           0           1          0  0.00%  0.00%  0.00%   0 IPC Seat Manager
  39         498       78651          6  0.00%  0.00%  0.00%   0 IPC Check Queue
  40           0           1          0  0.00%  0.00%  0.00%   0 IPC Seat RX Cont
  41           0           1          0  0.00%  0.00%  0.00%   0 IPC Seat TX Cont
  42        1113      137640          8  0.00%  0.00%  0.00%   0 IPC Keep Alive M
  43        4161      275274         15  0.00%  0.00%  0.00%   0 IPC Loadometer
  44           0           1          0  0.00%  0.00%  0.00%   0 IPC Session Deta
  45           0           1          0  0.00%  0.00%  0.00%   0 SENSOR-MGR event
  46           0           2          0  0.00%  0.00%  0.00%   0 Serial Backgroun
  47           0           1          0  0.00%  0.00%  0.00%   0 RMI RM Notify Wa
  48           0           3          0  0.00%  0.00%  0.00%   0 Graceful Reload
  49           0           2          0  0.00%  0.00%  0.00%   0 ATM Idle Timer
  50           0           1          0  0.00%  0.00%  0.00%   0 ATM ASYNC PROC
  51           0           1          0  0.00%  0.00%  0.00%   0 CEF MIB API
  52          17           9       1888  0.00%  0.00%  0.00%   0 SL Platform Back
  53           0           1          0  0.00%  0.00%  0.00%   0 License IPC stat
  54           0           1          0  0.00%  0.00%  0.00%   0 License IPC serv
  55          40        1386         28  0.00%  0.00%  0.00%   0 Net Input
  56           0           1          0  0.00%  0.00%  0.00%   0 IOSXE signals IO
  57           0           1          0  0.00%  0.00%  0.00%   0 client_entity_se
  58           0           1          0  0.00%  0.00%  0.00%   0 SERIAL A'detect
... (567 more lines truncated)
```

**`show processes cpu history`**

```
11111111111111111111111111111111111111111111111111111111
  100
   90
   80
   70
   60
   50
   40
   30
   20
   10
     0....5....1....1....2....2....3....3....4....4....5....5....6
               0    5    0    5    0    5    0    5    0    5    0
               CPU% per second (last 60 seconds)




                                               1
      111111111211122116621111211636711127321211652111121111221112
  100
   90
   80
   70
   60
   50
   40
   30
   20
   10                  **        * **    *     ***
     0....5....1....1....2....2....3....3....4....4....5....5....6
               0    5    0    5    0    5    0    5    0    5    0
               CPU% per minute (last 60 minutes)
              * = maximum CPU%   # = average CPU%




      1
      133333333334333333323333333333333333334333333343333343333333334333333333
  100
   90
   80
   70
   60
   50
   40
   30
   20
   10 *
     0....5....1....1....2....2....3....3....4....4....5....5....6....6....7..
               0    5    0    5    0    5    0    5    0    5    0    5    0
                   CPU% per hour (last 72 hours)
                  * = maximum CPU%   # = average CPU%
```

**`show processes cpu sorted`**

```
CPU utilization for five seconds: 2%/0%; one minute: 1%; five minutes: 1%
 PID Runtime(ms)     Invoked      uSecs   5Sec   1Min   5Min TTY Process
 108      287575       13765      20891  1.27%  0.10%  0.02%   0 Crimson Database
 612     1568071    10339323        151  0.15%  0.14%  0.13%   0 SISF Switcher Th
 186      104415      884728        118  0.07%  0.01%  0.00%   0 Exec
 130      498343    85584551          5  0.07%  0.03%  0.01%   0 L2 LISP Punt Pro
 211      264755    21503974         12  0.07%  0.02%  0.00%   0 VRRS Main thread
 150       26967      761119         35  0.07%  0.00%  0.00%   0 SASRcvWQWrk3
 215      254845    42898841          5  0.07%  0.02%  0.00%   0 IP ARP Retry Age
  74       16919     1382909         12  0.07%  0.00%  0.00%   0 TTY Background
 204      188062      474173        396  0.07%  0.01%  0.00%   0 CDP Protocol
 364       88095      651593        135  0.07%  0.00%  0.00%   0 LLDP Protocol
 126      289666    10885482         26  0.07%  0.03%  0.00%   0 IOSXE-RP Punt Se
  59      621479     6819354         91  0.07%  0.06%  0.05%   0 ARP Snoop
 371      101065     6819090         14  0.07%  0.00%  0.00%   0 DAI Packet Proce
 131      492879    85584550          5  0.07%  0.03%  0.02%   0 SIS Punt Process
 170      131697      273632        481  0.07%  0.00%  0.00%   0 IOMD IPC process
 586          60         175        342  0.07%  0.07%  0.01%   2 SSH Process
  17      142056    15062381          9  0.07%  0.01%  0.00%   0 DB offload write
 110      234703     5505285         42  0.07%  0.01%  0.00%   0 Crimson config p
 178      163747     2349906         69  0.07%  0.00%  0.00%   0 FED IPC process
  18        5440      688175          7  0.00%  0.00%  0.00%   0 IOSXE heartbeat
  16           1           3        333  0.00%  0.00%  0.00%   0 DB Notification
  15        9786     1376388          7  0.00%  0.00%  0.00%   0 GraphIt
  19          11          16        687  0.00%  0.00%  0.00%   0 PrstVbl
  20           0           1          0  0.00%  0.00%  0.00%   0 IPC Apps Task
  25           0           2          0  0.00%  0.00%  0.00%   0 DDR Timers
  14           0           3          0  0.00%  0.00%  0.00%   0 DB Lock Manager
  27           0           1          0  0.00%  0.00%  0.00%   0 ifIndex Receive
  13          55       11215          4  0.00%  0.00%  0.00%   0 WATCH_AFS
  21      555507     6042356         91  0.00%  0.03%  0.03%   0 ARP Input
  22       16198     1436496         11  0.00%  0.00%  0.00%   0 ARP Background
  31           0           1          0  0.00%  0.00%  0.00%   0 Platform appsess
  23           0           1          0  0.00%  0.00%  0.00%   0 AAA_SERVER_DEADT
  12           0           2          0  0.00%  0.00%  0.00%   0 Timers
  34           0           1          0  0.00%  0.00%  0.00%   0 IPC Zone Manager
  35       11183     1344035          8  0.00%  0.00%  0.00%   0 IPC Periodic Tim
  24           0           1          0  0.00%  0.00%  0.00%   0 Policy Manager
  11           0           1          0  0.00%  0.00%  0.00%   0 DiscardQ Backgro
  38           0           1          0  0.00%  0.00%  0.00%   0 IPC Seat Manager
  39         498       78652          6  0.00%  0.00%  0.00%   0 IPC Check Queue
  40           0           1          0  0.00%  0.00%  0.00%   0 IPC Seat RX Cont
  26          47          35       1342  0.00%  0.00%  0.00%   0 Entity MIB API
  28           0           1          0  0.00%  0.00%  0.00%   0 IFS Agent Manage
  43        4161      275276         15  0.00%  0.00%  0.00%   0 IPC Loadometer
  44           0           1          0  0.00%  0.00%  0.00%   0 IPC Session Deta
  45           0           1          0  0.00%  0.00%  0.00%   0 SENSOR-MGR event
  29        1593      275276          5  0.00%  0.00%  0.00%   0 IPC Event Notifi
  47           0           1          0  0.00%  0.00%  0.00%   0 RMI RM Notify Wa
  30       10208     1344035          7  0.00%  0.00%  0.00%   0 IPC Mcast Pendin
  49           0           2          0  0.00%  0.00%  0.00%   0 ATM Idle Timer
  32         151       22941          6  0.00%  0.00%  0.00%   0 IPC Dynamic Cach
  51           0           1          0  0.00%  0.00%  0.00%   0 CEF MIB API
  52          17           9       1888  0.00%  0.00%  0.00%   0 SL Platform Back
  53           0           1          0  0.00%  0.00%  0.00%   0 License IPC stat
  10        3713       22941        161  0.00%  0.00%  0.00%   0 Pool Manager
  55          40        1386         28  0.00%  0.00%  0.00%   0 Net Input
   9      750379      209638       3579  0.00%  0.03%  0.05%   0 Check heaps
  33        1797      275276          6  0.00%  0.00%  0.00%   0 IPC Service NonC
  58           0           1          0  0.00%  0.00%  0.00%   0 SERIAL A'detect
... (567 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
```

### <a id="1-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-process-cpu-oper:cpu-utilization": {
    "five-seconds": 1,
    "five-seconds-intr": 0,
    "one-minute": 1,
    "five-minutes": 1,
    "cpu-usage-processes": {
      "cpu-usage-process": []
    }
  }
}
```

---

## 2. Memory Statistics

**YANG Module:** `Cisco-IOS-XE-memory-oper.yang`
**Telemetry XPath:** `/memory-ios-xe-oper:memory-statistics/memory-statistic`

### CLI Show Commands

```
show memory statistics
show memory platform
```

### <a id="2-cli-output"></a>CLI Output

**`show memory statistics`**

```
Tracekey : 1#b99a8a189b9a7f7003a80862c51f6093

                Head    Total(b)     Used(b)     Free(b)   Lowest(b)  Largest(b)
Processor  7CCF19AE8048   1074181564   339035348   735146216   729537324   733842368
reserve P  7CCF19AE80A0      102404          92      102312      102312      102312
 lsmpi_io  7CCF026331A8     6295128     6294304         824         824         412
```

**`show memory platform`**

```
Virtual memory   : 69880102912
  Pages resident   : 1543405
  Major page faults: 23598
  Minor page faults: 2340475911

  Architecture     : x86_64
  Memory (kB)
    Physical       : 7678304
    Total          : 7678304
    Used           : 4163184
    Free           : 3515120
    Active         : 2125128
    Inactive       : 2798864
    Inact-dirty    : 0
    Inact-clean    : 0
    Dirty          : 0
    AnonPages      : 2020212
    Bounce         : 0
    Cached         : 2855364
    Commit Limit   : 3830960
    Committed As   : 7965092
    High Total     : 0
    High Free      : 0
    Low Total      : 7678304
    Low Free       : 3212172
    Mapped         : 1199420
    NFS Unstable   : 0
    Page Tables    : 55424
    Slab           : 371664
    Writeback      : 0
    HugePages Total: 8
    HugePages Free : 8
    HugePages Rsvd : 0
    HugePage Size  : 2048

  Swap (kB)
    Total          : 0
    Used           : 0
    Free           : 0
    Cached         : 0

  Buffers (kB)     : 115488

  Load Average
    1-Min          : 0.66
    5-Min          : 0.52
    15-Min         : 0.49
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics"
```

### <a id="2-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-memory-oper:memory-statistics": {
    "memory-statistic": [
      {
        "name": "Processor",
        "total-memory": "1074181564",
        "used-memory": "338155612",
        "free-memory": "736025952",
        "lowest-usage": "729537324",
        "highest-usage": "733842368"
      },
      {
        "name": "reserve Processor",
        "total-memory": "102404",
        "used-memory": "92",
        "free-memory": "102312",
        "lowest-usage": "102312",
        "highest-usage": "102312"
      },
      {
        "name": "lsmpi_io",
        "total-memory": "6295128",
        "used-memory": "6294304",
        "free-memory": "824",
        "lowest-usage": "824",
        "highest-usage": "412"
      }
    ]
  }
}
```

---

## 3. Process Memory

**YANG Module:** `Cisco-IOS-XE-process-memory-oper.yang`
**Telemetry XPath:** `/process-memory-ios-xe-oper:memory-usage-processes`

### CLI Show Commands

```
show processes memory sorted
show processes memory
```

### <a id="3-cli-output"></a>CLI Output

**`show processes memory sorted`**

```
Processor Pool Total: 1074181564 Used:  339079024 Free:  735102540
reserve P Pool Total:     102404 Used:         88 Free:     102316
 lsmpi_io Pool Total:    6295128 Used:    6294296 Free:        832

 PID TTY  Allocated      Freed    Holding    Getbufs    Retbufs Process
   0   0  306018224   61817032  242471496          0          0 *Init*
   4   0   22537432     114744   22277632          0          0 RF Slave Main Th
  80   0  869015072     772296   21946480          0          0 IOSD ipc task
 530   0    5339504    1215912    4165552     849828          0 EEM ED Syslog
   0   0 4766766960 4737012016    3434416   24110359    1233588 *Dead*
 354  64   31848416   27462312    3186584          0          0 IOSP-Server VTY
 152   0 13388595184 13385587360    2445080          0          0 SAMsgThread
  70   0    4088992     802272    2125072          0          0 Net Background
 544   0  432051520  430184560    1906088          0          0 EEM Server
 186   0  274557824  228155168    1871856          0          0 Exec
 486   0    5395424    4104864    1163320          0          0 Crypto CA
   0   0          0          0    1117448          0          0 *MallocLite*
 319   0     961856      75040     939624          0          0 CEF: IPv4 proces
 586   2    1269384     374152     919928          0          0 SSH Process
 214   0     934960      81240     907824          0          0 IP ARP Adjacency
   1   0     848840       6976     871824          0          0 Chunk Manager
 537   1    3721600    2851120     866240          0          0 SSH Process
 285   0     969320     424104     545216          0          0 mDNS
 459   0     462872        896     499984          0          0 EST Client
 531   0     409416       9464     441912      72316          0 EEM ED Generic
 491   0     366056        728     419288          0          0 Crypto IKEv2
 419   0     447112        456     386736          0          0 LSD Main Proc
 612   0 1834593480          0     324976          0          0 SISF Switcher Th
 392   0     263176        432     316272          0          0 ADJ resolve proc
 178   0   20888168   19654008     272600          0          0 FED IPC process
 613   0  492667304 2326770592     272560          0          0 SISF Main Thread
 514   0      23184       1648     268288          0          0 IOSP-Server VTY
 516  65      19688       1808     264728          0          0 IOSP-Server VTY
 292   0     153728          0     255688          0          0 st_pw_oam
 411   0       1824          0     247784          0          0 COPS
  78   0    2031112    1856560     229840          0          0 SASRcvWQWrk1
 111   0   22262336   22115608     222048          0          0 DBAL EVENTS
 596   0     167848        448     221360          0          0 MRIB Process
  10   0 1595154768 1595175120     217304 1521661416 1521673108 Pool Manager
 611   0     206624       1992     216696          0          0 ONEP Network Ele
 329   0   52066792   16087328     197512          0          0 HTTP CORE
 408   0     140600        328     169992          0          0 L2FIB Event Disp
 476   0     515904     521016     167240          0          0 AAA Proxy
 399   0  115120272  115012056     162032          0          0 system secure co
 559   0     191528       6240     155224          0          0 Call Home proces
 428   0     100944        448     154456          0          0 OAM DPM
 281   0      98736          0     152696          0          0 IPAM Manager
 249   0    2609232    2566536     138216          0          0 PKI/SSL WLC IPC
 470   0     102752          0     132712          0          0 MMA DB TIMER
  21   0 2638312640 2638206704     130608          0          0 ARP Input
 223   0     100560          0     130520          0          0 radius radsec cl
 225   0     100560          0     130520          0          0 tplus secure pro
 247   0      26968          0     128928          0          0 PKI_SSL LSC Enro
 202   0      98784          0     128744          0          0 ACCT Periodic Pr
 461   0      99192        448     128704          0          0 Timer Library
 457   0      66112        160     125952          0          0 PDM core
 615   0     162512      16456     125504          0          0 DHCPD Receive
 471   0      68064          0     122024          0          0 mDNS snooping
 236   0      12144        288     114104          0          0 SKA IPC process
 585   0          0          0     112056          0          0 PnP-Monitor
... (575 more lines truncated)
```

**`show processes memory`**

```
Processor Pool Total: 1074181564 Used:  339038584 Free:  735142980
reserve P Pool Total:     102404 Used:         88 Free:     102316
 lsmpi_io Pool Total:    6295128 Used:    6294296 Free:        832

 PID TTY  Allocated      Freed    Holding    Getbufs    Retbufs Process
   0   0  306018224   61817032  242471496       2611   34694852 *Init*
   0   0       2584 1443818896       2584          0          0 *Sched*
   0   0 4766884640 4737130984    3434416      25066       8495 *Dead*
   0   0          0          0    1117448          0          0 *MallocLite*
   1   0     848840       6976     871824          0          0 Chunk Manager
   2   0        448        448      18096          0          0 Load Meter
   3   0          0    3406624      29960          0          0 SpanTree Flush
   4   0   22537432     114744   22277632          0          0 RF Slave Main Th
   5   0          0          0      29960          0          0 Retransmission o
   6   0          0          0      29960          0          0 IPC ISSU Dispatc
   7   0          0          0      29960          0          0 RO Notify Timers
   8   0          0          0      29960          0          0 VIDB BACKGD MGR
   9   0       8872        448      38384          0          0 Check heaps
  10   0 1595154768 1595175120     217304         51          0 Pool Manager
  11   0          0          0      29960          0          0 DiscardQ Backgro
  12   0        448        448      29960          0          0 Timers
  13   0          0          0      17960          0          0 WATCH_AFS
  14   0        448        448      29960          0          0 DB Lock Manager
  15   0        448        448      29960          0          0 GraphIt
  16   0       1408          0      31368          0          0 DB Notification
  17   0          0      81000      29960          0          0 DB offload write
  18   0          0          0      29960          0          0 IOSXE heartbeat
  19   0       6952       6952      29960          0          0 PrstVbl
  20   0          0          0      29960          0          0 IPC Apps Task
  21   0 2638329888 2638223952     130608    7483902    7483902 ARP Input
  22   0      87472      50216      29960         43         43 ARP Background
  23   0          0          0      29960          0          0 AAA_SERVER_DEADT
  24   0          0          0      53960          0          0 Policy Manager
  25   0        448        448      29960          0          0 DDR Timers
  26   0     193328     150616      73784        105        105 Entity MIB API
  27   0          0          0      29960          0          0 ifIndex Receive
  28   0          0          0      29960          0          0 IFS Agent Manage
  29   0          0          0      29960          0          0 IPC Event Notifi
  30   0          0          0      29960          0          0 IPC Mcast Pendin
  31   0          0          0      29960          0          0 Platform appsess
  32   0          0          0      29960          0          0 IPC Dynamic Cach
  33   0          0          0      29960          0          0 IPC Service NonC
  34   0          0          0      29960          0          0 IPC Zone Manager
  35   0          0          0      29960          0          0 IPC Periodic Tim
  36   0          0          0      29960          0          0 IPC Deferred Por
  37   0          0          0      29960          0          0 IPC Process leve
  38   0       2192          0      32152          0          0 IPC Seat Manager
  39   0          0          0      29960          0          0 IPC Check Queue
  40   0          0          0      29960          0          0 IPC Seat RX Cont
  41   0          0          0      29960          0          0 IPC Seat TX Cont
  42   0          0          0      29960          0          0 IPC Keep Alive M
  43   0          0          0      29960          0          0 IPC Loadometer
  44   0          0          0      29960          0          0 IPC Session Deta
  45   0          0          0      29960          0          0 SENSOR-MGR event
  46   0        448        448      29960          0          0 Serial Backgroun
  47   0          0          0      17960          0          0 RMI RM Notify Wa
  48   0          0          0      29960          0          0 Graceful Reload
  49   0        448        448      29960          0          0 ATM Idle Timer
  50   0          0          0      29960          0          0 ATM ASYNC PROC
  51   0          0          0      29960          0          0 CEF MIB API
... (575 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-process-memory-oper:memory-usage-processes"
```

### <a id="3-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-process-memory-oper:memory-usage-processes": {
    "memory-usage-process": [
      {
        "pid": 1,
        "name": "Chunk Manager",
        "tty": 0,
        "allocated-memory": "848840",
        "freed-memory": "6976",
        "holding-memory": "871824",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 2,
        "name": "Load Meter",
        "tty": 0,
        "allocated-memory": "448",
        "freed-memory": "448",
        "holding-memory": "18096",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 3,
        "name": "SpanTree Flush",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "3406624",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 4,
        "name": "RF Slave Main Thread",
        "tty": 0,
        "allocated-memory": "22537432",
        "freed-memory": "114744",
        "holding-memory": "22277632",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 5,
        "name": "Retransmission of IPC Versioning",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "0",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 6,
        "name": "IPC ISSU Dispatch Process",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "0",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 7,
        "name": "RO Notify Timers",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "0",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 8,
        "name": "VIDB BACKGD MGR",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "0",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 9,
        "name": "Check heaps",
        "tty": 0,
        "allocated-memory": "8872",
        "freed-memory": "448",
        "holding-memory": "38384",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 10,
        "name": "Pool Manager",
        "tty": 0,
        "allocated-memory": "1593847416",
        "freed-memory": "1593867768",
        "holding-memory": "217304",
        "get-buffers": 51,
        "ret-buffers": 0
      },
      {
        "pid": 11,
        "name": "DiscardQ Background Mgr",
        "tty": 0,
        "allocated-memory": "0",
        "freed-memory": "0",
        "holding-memory": "29960",
        "get-buffers": 0,
        "ret-buffers": 0
      },
      {
        "pid": 12,
        "name": "Timers",
        "tty": 0,
        "allocated-memory": "448",
        "freed-memory": "448",
        "holding-memory": "29960",
        "get-buffers": 0,
  ...
}
```

---

## 4. System DRAM (Platform Software)

**YANG Module:** `Cisco-IOS-XE-platform-software-oper.yang`
**Telemetry XPath:** `/platform-sw-ios-xe-oper:cisco-platform-software/control-processes`

### CLI Show Commands

```
show platform software status control-processor brief
show platform software process slot switch active R0 monitor
```

### <a id="4-cli-output"></a>CLI Output

**`show platform software status control-processor brief`**

```
Load Average
 Slot  Status  1-Min  5-Min 15-Min
1-RP0 Healthy   0.56   0.51   0.49

Memory (kB)
 Slot  Status    Total     Used (Pct)     Free (Pct) Committed (Pct)
1-RP0 Healthy  7678304  4163108 (54%)  3515196 (46%)   7962696 (104%)

CPU Utilization
 Slot  CPU   User System   Nice   Idle    IRQ   SIRQ IOwait
1-RP0    0   3.27   0.87   0.00  95.74   0.00   0.10   0.00
         1   2.72   1.19   0.00  96.07   0.00   0.00   0.00
         2   2.61   0.76   0.00  96.51   0.00   0.00   0.10
         3   3.05   0.98   0.00  95.96   0.00   0.00   0.00
         4   3.16   1.41   0.00  95.41   0.00   0.00   0.00
         5   4.37   0.98   0.00  94.64   0.00   0.00   0.00
         6   4.47   0.98   0.00  94.54   0.00   0.00   0.00
         7   6.87   0.65   0.00  92.46   0.00   0.00   0.00
```

**`show platform software process slot switch active R0 monitor`**

```
top - 23:59:43 up 15 days, 22:22,  0 users,  load average: 0.50, 0.50, 0.49
Tasks: 520 total,   1 running, 519 sleeping,   0 stopped,   0 zombie
%Cpu(s):  3.1 us,  3.1 sy,  0.0 ni, 93.8 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :   7498.3 total,   1757.4 free,   2669.2 used,   3071.7 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.   4209.2 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
16529 root      20   0 3754732 383880 122540 S  16.7   5.0   3053:21 fed main +
 8167 root      20   0 3201612 993052 658004 S   5.6  12.9 528:25.12 linux_ios+
 8517 root      20   0 4734076 105032  87496 S   5.6   1.4 113:15.38 cmand
 8777 root      20   0    6408   3712   2688 R   5.6   0.0   0:00.04 top
10015 root      20   0  274472  49456  44256 S   5.6   0.6  47:19.62 btman
    1 root      20   0   42616  20184   8244 S   0.0   0.3  39:40.16 systemd
    2 root      20   0       0      0      0 S   0.0   0.0   0:01.00 kthreadd
    3 root      20   0       0      0      0 S   0.0   0.0   0:00.00 pool_work+
    4 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
    5 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
    6 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
    7 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
    9 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/0+
   12 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
   13 root      20   0       0      0      0 I   0.0   0.0   0:00.00 rcu_tasks+
   14 root      20   0       0      0      0 I   0.0   0.0   0:00.00 rcu_tasks+
   15 root      20   0       0      0      0 S   0.0   0.0   0:54.23 ksoftirqd+
   16 root      20   0       0      0      0 I   0.0   0.0  10:23.73 rcu_sched
   17 root      rt   0       0      0      0 S   0.0   0.0   0:03.22 migration+
   18 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/0
   19 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/1
   20 root      rt   0       0      0      0 S   0.0   0.0   0:03.06 migration+
   21 root      20   0       0      0      0 S   0.0   0.0   0:50.52 ksoftirqd+
   23 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/1+
   24 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/2
   25 root      rt   0       0      0      0 S   0.0   0.0   0:03.04 migration+
   26 root      20   0       0      0      0 S   0.0   0.0   0:49.05 ksoftirqd+
   28 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/2+
   29 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/3
   30 root      rt   0       0      0      0 S   0.0   0.0   0:03.06 migration+
   31 root      20   0       0      0      0 S   0.0   0.0   0:46.80 ksoftirqd+
   33 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/3+
   34 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/4
   35 root      rt   0       0      0      0 S   0.0   0.0   0:03.11 migration+
   36 root      20   0       0      0      0 S   0.0   0.0   0:50.40 ksoftirqd+
   38 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/4+
   39 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/5
   40 root      rt   0       0      0      0 S   0.0   0.0   0:03.07 migration+
   41 root      20   0       0      0      0 S   0.0   0.0   0:48.44 ksoftirqd+
   43 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/5+
   44 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/6
   45 root      rt   0       0      0      0 S   0.0   0.0   0:03.11 migration+
   46 root      20   0       0      0      0 S   0.0   0.0   0:46.41 ksoftirqd+
   48 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/6+
   49 root      20   0       0      0      0 S   0.0   0.0   0:00.00 cpuhp/7
   50 root      rt   0       0      0      0 S   0.0   0.0   0:03.09 migration+
   51 root      20   0       0      0      0 S   0.0   0.0   0:51.67 ksoftirqd+
   53 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/7+
   54 root      20   0       0      0      0 S   0.0   0.0   0:00.00 kdevtmpfs
   55 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker/R+
   56 root      20   0       0      0      0 S   0.0   0.0   0:00.02 kauditd
   57 root      20   0       0      0      0 S   0.0   0.0   0:01.13 khungtaskd
   58 root      20   0       0      0      0 S   0.0   0.0   0:00.00 oom_reaper
... (467 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-platform-software-oper:cisco-platform-software/control-processes"
```

### <a id="4-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-platform-software-oper:control-processes": {
    "control-process": [
      {
        "fru": "fru-rp",
        "slot": 0,
        "bay": 0,
        "chassis": 1,
        "control-process-status": "online",
        "updated": "0",
        "load-average-stats": {},
        "load-avg-minutes": {},
        "memory-stats": {},
        "per-core-stats": {},
        "high-availability-state": "ha-role-active",
        "chassis-state": "ha-role-active"
      }
    ]
  }
}
```

---

## 5. Environment Sensors

**YANG Module:** `Cisco-IOS-XE-environment-oper.yang`
**Telemetry XPath:** `/environment-ios-xe-oper:environment-sensors`

### CLI Show Commands

```
show environment all
show environment temperature
show environment power
show environment fan
```

### <a id="5-cli-output"></a>CLI Output

**`show environment all`**

```
Sensor List: Environmental Monitoring
 Sensor          Location        State               Reading       Range(min-max)
 PS1 Vout        1               FAULTY                 0 mV          na
 PS1 Vin         1               FAULTY                 0 mV        90 - 264
 PS1 CURin       1               FAULTY                 0 mA          na
 PS1 Curout      1               FAULTY                 0 mA          na
 PS1 POWin       1               FAULTY                 0 mW          na
 PS1 POWout      1               FAULTY                 0 mW          na
 PS1 FAN         1               FAULTY                 0 rpm         na
 PS2 Vout        1               GOOD               55984 mV          na
 PS2 Vin         1               GOOD              110500 mV        90 - 264
 PS2 CURin       1               GOOD                1547 mA          na
 PS2 CURout      1               GOOD                2656 mA          na
 PS2 POWin       1               GOOD              163000 mW          na
 PS2 POWout      1               GOOD              148000 mW          na
 PS2 FAN         1               GOOD                2640 rpm         na
 SYSTEM INLET    1               GREEN                 39 Celsius   0 - 56
 SYSTEM OUTLET   1               GREEN                 52 Celsius   0 - 125
 SYSTEM HOTSPOT  1               GREEN                 71 Celsius   0 - 125

Switch	 FAN	 Speed	 State	 Airflow direction
---------------------------------------------------
  1  	  1	5600 	  OK	 Front to Back
  1  	  2	5600 	  OK	 Front to Back
  1  	  3	5600 	  OK	 Front to Back

SW  PID                 Serial#     Status           Sys Pwr  PoE Pwr  Watts
--  ------------------  ----------  ---------------  -------  -------  -----
1A  Unknown             Unknown      No Input Power  Bad      Bad      Unknown
1B  PWR-C1-1100WAC-P    ART2219FA4U  OK              Good     Good     1100

---------------------------------------------------
```

**`show environment temperature`**

```
Switch 1: SYSTEM TEMPERATURE is OK
Inlet Temperature Value: 39 Degree Celsius
Temperature State: GREEN
Yellow Threshold : 46 Degree Celsius
Red Threshold    : 56 Degree Celsius

Outlet Temperature Value: 52 Degree Celsius
Temperature State: GREEN
Yellow Threshold : 105 Degree Celsius
Red Threshold    : 125 Degree Celsius

Hotspot Temperature Value: 71 Degree Celsius
Temperature State: GREEN
Yellow Threshold : 105 Degree Celsius
Red Threshold    : 125 Degree Celsius
```

**`show environment power`**

```
SW  PID                 Serial#     Status           Sys Pwr  PoE Pwr  Watts
--  ------------------  ----------  ---------------  -------  -------  -----
1A  Unknown             Unknown      No Input Power  Bad      Bad      Unknown
1B  PWR-C1-1100WAC-P    ART2219FA4U  OK              Good     Good     1100
```

**`show environment fan`**

```
Switch	 FAN	 Speed	 State	 Airflow direction
---------------------------------------------------
  1  	  1	5600 	  OK	 Front to Back
  1  	  2	5600 	  OK	 Front to Back
  1  	  3	5600 	  OK	 Front to Back
FAN PS-1 is NOT PRESENT
FAN PS-2 is OK
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-environment-oper:environment-sensors"
```

### <a id="5-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-environment-oper:environment-sensors": {
    "environment-sensor": [
      {
        "name": "Inlet Temp Sensor",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 40,
        "sensor-units": "celsius",
        "low-critical-threshold": -10,
        "low-normal-threshold": 0,
        "high-normal-threshold": 46,
        "high-critical-threshold": 56,
        "sensor-name": "temperature",
        "hi-minor-thrsld": 56,
        "hi-major-thrsld": 56
      },
      {
        "name": "Outlet Temp Sensor",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 52,
        "sensor-units": "celsius",
        "low-critical-threshold": -10,
        "low-normal-threshold": 0,
        "high-normal-threshold": 105,
        "high-critical-threshold": 125,
        "sensor-name": "temperature",
        "hi-minor-thrsld": 125,
        "hi-major-thrsld": 125
      },
      {
        "name": "HotSpot Temp Sensor",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 71,
        "sensor-units": "celsius",
        "low-critical-threshold": -10,
        "low-normal-threshold": 0,
        "high-normal-threshold": 105,
        "high-critical-threshold": 125,
        "sensor-name": "temperature",
        "hi-minor-thrsld": 125,
        "hi-major-thrsld": 125
      },
      {
        "name": "FAN - T1 1",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 0,
        "sensor-units": "revolutions-per-minute",
        "low-critical-threshold": 0,
        "low-normal-threshold": 0,
        "high-normal-threshold": 0,
        "high-critical-threshold": 0,
        "sensor-name": "fan",
        "hi-minor-thrsld": 0,
        "hi-major-thrsld": 0
      },
      {
        "name": "FAN - T1 2",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 0,
        "sensor-units": "revolutions-per-minute",
        "low-critical-threshold": 0,
        "low-normal-threshold": 0,
        "high-normal-threshold": 0,
        "high-critical-threshold": 0,
        "sensor-name": "fan",
        "hi-minor-thrsld": 0,
        "hi-major-thrsld": 0
      },
      {
        "name": "FAN - T1 3",
        "location": "Switch 1",
        "state": "Norm",
        "current-reading": 0,
        "sensor-units": "revolutions-per-minute",
        "low-critical-threshold": 0,
        "low-normal-threshold": 0,
        "high-normal-threshold": 0,
        "high-critical-threshold": 0,
        "sensor-name": "fan",
        "hi-minor-thrsld": 0,
        "hi-major-thrsld": 0
      },
      {
        "name": "Power Supply A",
        "location": "Switch 1",
        "state": "Shut",
        "current-reading": 0,
        "sensor-units": "watts",
        "low-critical-threshold": 0,
        "low-normal-threshold": 0,
        "high-normal-threshold": 0,
        "high-critical-threshold": 0,
        "sensor-name": "power",
  ...
}
```

---

## 6. Power over Ethernet (PoE)

**YANG Module:** `Cisco-IOS-XE-poe-oper.yang`
**Telemetry XPath:** `/poe-ios-xe-oper:poe-oper-data`

### CLI Show Commands

```
show power inline
show power inline detail
show power inline consumption
```

### <a id="6-cli-output"></a>CLI Output

**`show power inline`**

```
Module   Available     Used     Remaining
          (Watts)     (Watts)    (Watts)
------   ---------   --------   ---------
1           595.0       71.6       523.4
Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Te1/0/1   auto   off        0.0     n/a                 n/a   60.0
Te1/0/2   auto   off        0.0     n/a                 n/a   60.0
Te1/0/3   auto   off        0.0     n/a                 n/a   60.0
Te1/0/4   auto   off        0.0     n/a                 n/a   60.0
Te1/0/5   auto   off        0.0     n/a                 n/a   60.0
Te1/0/6   auto   off        0.0     n/a                 n/a   60.0
Te1/0/7   auto   off        0.0     n/a                 n/a   60.0
Te1/0/8   auto   off        0.0     n/a                 n/a   60.0
Te1/0/9   auto   off        0.0     n/a                 n/a   60.0
Te1/0/10  auto   off        0.0     n/a                 n/a   60.0
Te1/0/11  auto   off        0.0     n/a                 n/a   60.0
Te1/0/12  auto   off        0.0     n/a                 n/a   60.0
Te1/0/13  auto   off        0.0     n/a                 n/a   60.0
Te1/0/14  auto   on         30.0    CW9166I-A           4     60.0
Te1/0/15  auto   off        0.0     n/a                 n/a   60.0
Te1/0/16  auto   on         41.6    C9136I-A            4     60.0
Te1/0/17  auto   off        0.0     n/a                 n/a   60.0
Te1/0/18  auto   off        0.0     n/a                 n/a   60.0
Te1/0/19  auto   off        0.0     n/a                 n/a   60.0
Te1/0/20  auto   off        0.0     n/a                 n/a   60.0
Te1/0/21  auto   off        0.0     n/a                 n/a   60.0
Te1/0/22  auto   off        0.0     n/a                 n/a   60.0
Te1/0/23  auto   off        0.0     n/a                 n/a   60.0
Te1/0/24  auto   off        0.0     n/a                 n/a   60.0
--------- ------ ---------- ---------- ---------- ------ -----
Totals:          2    on    71.6
```

**`show power inline detail`**

```
^
% Invalid input detected at '^' marker.
```

**`show power inline consumption`**

```
^
% Invalid input detected at '^' marker.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-poe-oper:poe-oper-data"
```

### <a id="6-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-poe-oper:poe-oper-data": {
    "poe-port-detail": [
      {
        "intf-name": "TenGigabitEthernet1/0/14",
        "power-used": "30.0",
        "pd-class": "pd-ieee4",
        "device-detected": true,
        "device-name": " CW9166I-A",
        "police": false,
        "power-admin-max": "60.0",
        "power-from-pse": "30.0",
        "power-to-pd": "30.0",
        "power-consumption": "10.89",
        "max-power-drawn": "12.12",
        "oper-state": "on",
        "admin-state": "admin-state-auto",
        "oper-power": "10.89",
        "admin-police": "police-action-none",
        "oper-police": "oper-police-none",
        "cutoff-power-police": "30.0",
        "power-negotiation-used": "power-negotiation-cdp",
        "four-pair-poe-supported": true,
        "four-pair-poe-enabled": false,
        "four-pair-pd-arch": "pd-architecture-shared",
        "over-current-counter": 0,
        "short-current-counter": 0,
        "power-denied-counter": 0,
        "conn-type": "conn-chk-sp",
        "signal-pair-data": {},
        "spare-pair-data": {},
        "discovery": "discovery-cisco-ieee",
        "lldp-mdi-rx": {},
        "lldp-mdi-tx": {},
        "lldp-med-mdi-rx": {},
        "lldp-med-mdi-tx": {},
        "fast-poe-enabled": false,
        "perpetual-poe-enabled": false,
        "oper-priority": "port-oper-priority-low",
        "post-done": false,
        "upoe-plus-enabled": false,
        "poe-intf-enabled": true,
        "module-id": 1,
        "chassis-num": 1,
        "prot-pd-highest-req-pwr": "30.0",
        "prot-req-state": "proto-in-prog",
        "pwr-state": "pow-dev-fully-powered",
        "meter-start-time": "2026-03-28T00:39:09+00:00",
        "metered-energy-value": "2211775820.0",
        "device-tag": "",
        "last-update-time": "2026-04-12T22:39:57+00:00",
        "bucket-width": 900,
        "number-of-buckets": 12,
        "poe-bucket": [
          6488058,
          9785722,
          9793760,
          9797120,
          9773168,
          9735032,
          9781878,
          9790950,
          9774720,
          9786032,
          9796804,
          9787580
        ],
        "abs-cntr": 0,
        "bad-sgn-cntr": 0
      },
      {
        "intf-name": "TenGigabitEthernet1/0/16",
        "power-used": "41.63",
        "pd-class": "pd-ieee4",
        "device-detected": true,
        "device-name": " C9136I-A",
        "police": false,
        "power-admin-max": "60.0",
        "power-from-pse": "41.63",
        "power-to-pd": "41.63",
        "power-consumption": "13.3",
        "max-power-drawn": "15.1",
        "oper-state": "on",
        "admin-state": "admin-state-auto",
        "oper-power": "13.3",
        "admin-police": "police-action-none",
        "oper-police": "oper-police-none",
        "cutoff-power-police": "41.63",
        "power-negotiation-used": "power-negotiation-cdp",
        "four-pair-poe-supported": true,
        "four-pair-poe-enabled": false,
  ...
}
```

---

## 7. Interface Statistics

**YANG Module:** `Cisco-IOS-XE-interfaces-oper.yang`
**Telemetry XPath:** `/interfaces-ios-xe-oper:interfaces/interface`

### CLI Show Commands

```
show interfaces
show interfaces status
show interfaces counters
show interfaces counters errors
```

### <a id="7-cli-output"></a>CLI Output

**`show interfaces`**

```
Vlan1 is up, line protocol is up , Autostate Enabled
  Hardware is Ethernet SVI, address is 700b.4ff5.c2c7 (bia 700b.4ff5.c2c7)
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive not supported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 2w0d, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/375/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
  5 minute output rate 0 bits/sec, 0 packets/sec
     0 packets input, 0 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 packets output, 0 bytes, 0 underruns
     Output 0 broadcasts (0 IP multicasts)
     0 output errors, 2 interface resets
     0 unknown protocol drops
     0 output buffer failures, 0 output buffers swapped out
Vlan311 is up, line protocol is up , Autostate Enabled
  Hardware is Ethernet SVI, address is 700b.4ff5.c2da (bia 700b.4ff5.c2da)
  Internet address is 10.85.134.70/26
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive not supported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:00, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/375/0/205 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 3000 bits/sec, 5 packets/sec
  5 minute output rate 3392000 bits/sec, 965 packets/sec
     775015 packets input, 89118429 bytes, 0 no buffer
     Received 0 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     188309720 packets output, 91198884018 bytes, 0 underruns
     Output 0 broadcasts (0 IP multicasts)
     0 output errors, 2 interface resets
     0 unknown protocol drops
     0 output buffer failures, 0 output buffers swapped out
Vlan700 is down, line protocol is down , Autostate Enabled
  Hardware is Ethernet SVI, address is 700b.4ff5.c2dc (bia 700b.4ff5.c2dc)
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive not supported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input never, output never, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/375/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 0 bits/sec, 0 packets/sec
... (1235 more lines truncated)
```

**`show interfaces status`**

```
Port         Name               Status       Vlan       Duplex  Speed Type
Te1/0/1      CW_Core_MGMT-C9200 connected    trunk      a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/2      ASR1001-Mgmt       connected    311        a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/3      JCOHOE-9840-WLC    connected    trunk      a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/4      RC_DESC_1769286885 notconnect   1            auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/5      ASR1001-G1         connected    311        a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/6      VNC2-SPINE1-G00    disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/7                         disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/8                         disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/9      VNC2-SPINE1        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/10     VNC2-SPINE2        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/11                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/12     R28-C9300L-ZTP     disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/13     C9600              connected    311        a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/14     AP1-2026-03-18     connected    311        a-full a-5000 100/1000/2.5G/5G/10GBaseTX
Te1/0/15     MX-Appliance       connected    311        a-full a-1000 100/1000/2.5G/5G/10GBaseTX
Te1/0/16     AP2-2026-03-18     connected    311        a-full a-5000 100/1000/2.5G/5G/10GBaseTX
Te1/0/17                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/18                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/19                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/20                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/21                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/22                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/23                        disabled     311          auto   auto 100/1000/2.5G/5G/10GBaseTX
Te1/0/24     UPLINK-TO-TOR1-Te1 connected    trunk      a-full  a-10G 100/1000/2.5G/5G/10GBaseTX
Te1/1/1                         notconnect   1            full   1000 1000BaseSX SFP
Te1/1/2                         notconnect   1            auto   auto unknown
Te1/1/3                         notconnect   1            full   1000 1000BaseSX SFP
Te1/1/4                         notconnect   1            auto   auto unknown
Te1/1/5                         notconnect   1            auto   auto unknown
Te1/1/6                         notconnect   1            auto   auto unknown
Te1/1/7                         notconnect   1            auto   auto unknown
Te1/1/8      C9300L-RU27-T111   connected    311          full    10G SFP-10GBase-CX1
Ap1/0/1                         connected    trunk      a-full a-1000 App-hosting port
```

**`show interfaces counters`**

```
Port               InOctets    InUcastPkts    InMcastPkts    InBcastPkts
Te1/0/1           213729676         137648        2824337            486
Te1/0/2               54632              0            738              0
Te1/0/3           428593162        1534691          71397           1622
Te1/0/4                   0              0              0              0
Te1/0/5           284502193        1414486              0           1584
Te1/0/6                   0              0              0              0
Te1/0/7                   0              0              0              0
Te1/0/8                   0              0              0              0
Te1/0/9                   0              0              0              0
Te1/0/10                  0              0              0              0
Te1/0/11                  0              0              0              0
Te1/0/12             503743            524           3523            542
Te1/0/13           64296312         512850          26271             22
Te1/0/14          242649615         632988          96516          23398
Te1/0/15        59981597677      102712727           7207          11866
Te1/0/16          249971992         601024          96577          45882
Te1/0/17                  0              0              0              0
Te1/0/18                  0              0              0              0
Te1/0/19                  0              0              0              0
Te1/0/20                  0              0              0              0
Te1/0/21                  0              0              0              0
Te1/0/22                  0              0              0              0
Te1/0/23                  0              0              0              0
Te1/0/24        33657553222       76367679        3958408        7637390
Te1/1/1                   0              0              0              0
Te1/1/2                   0              0              0              0
Te1/1/3                   0              0              0              0
Te1/1/4                   0              0              0              0
Te1/1/5                   0              0              0              0
Te1/1/6                   0              0              0              0
Te1/1/7                   0              0              0              0
Te1/1/8          1071181820       15875104          82244           1572
Ap1/0/1            22856287          51849         144446              1

Port              OutOctets   OutUcastPkts   OutMcastPkts   OutBcastPkts
Te1/0/1          1166601638        4292381        2799659        7693635
Te1/0/2           999817934        4290826        1422055        7531026
Te1/0/3          1827670967        6213461        4862898        7692249
Te1/0/4                   0              0              0              0
Te1/0/5          1118434859        5501394        1422801        7529443
Te1/0/6                   0              0              0              0
Te1/0/7                   0              0              0              0
Te1/0/8                   0              0              0              0
Te1/0/9                   0              0              0              0
Te1/0/10                  0              0              0              0
Te1/0/11                  0              0              0              0
Te1/0/12            1020690            787           3437           3311
Te1/0/13         1045547755        4742107        1422068        7531012
Te1/0/14         1099947407        4712592        1393051        7523582
Te1/0/15         7469324108       52707625         196908        1048745
Te1/0/16         1094356797        4697577        1394198        7501546
Te1/0/17                  0              0              0              0
Te1/0/18                  0              0              0              0
Te1/0/19                  0              0              0              0
Te1/0/20                  0              0              0              0
Te1/0/21                  0              0              0              0
Te1/0/22                  0              0              0              0
Te1/0/23                  0              0              0              0
Te1/0/24        63052567807      126941662        1710543          85207
... (9 more lines truncated)
```

**`show interfaces counters errors`**

```
Port           Align-Err     FCS-Err    Xmit-Err     Rcv-Err  UnderSize  OutDiscards
Te1/0/1                0           0           0           0          0            0
Te1/0/2                0           0           0           0          0            0
Te1/0/3                0           0           0           0          0            0
Te1/0/4                0           0           0           0          0            0
Te1/0/5                0           0           0           0          0            0
Te1/0/6                0           0           0           0          0            0
Te1/0/7                0           0           0           0          0            0
Te1/0/8                0           0           0           0          0            0
Te1/0/9                0           0           0           0          0            0
Te1/0/10               0           0           0           0          0            0
Te1/0/11               0           0           0           0          0            0
Te1/0/12               0           0           0           0          0            0
Te1/0/13               0           0           0           0          0            0
Te1/0/14               0           0           0           0          0            0
Te1/0/15               0           0           0           0          0            0
Te1/0/16               0           0           0           0          0            0
Te1/0/17               0           0           0           0          0            0
Te1/0/18               0           0           0           0          0            0
Te1/0/19               0           0           0           0          0            0
Te1/0/20               0           0           0           0          0            0
Te1/0/21               0           0           0           0          0            0
Te1/0/22               0           0           0           0          0            0
Te1/0/23               0           0           0           0          0            0
Te1/0/24               0           0           0           0          0            0
Te1/1/1                0           0           0           0          0            0
Te1/1/2                0           0           0           0          0            0
Te1/1/3                0           0           0           0          0            0
Te1/1/4                0           0           0           0          0            0
Te1/1/5                0           0           0           0          0            0
Te1/1/6                0           0           0           0          0            0
Te1/1/7                0           0           0           0          0            0
Te1/1/8                0           0           0           0          0            0
Ap1/0/1                0           0           0           0          0            0

Port         Single-Col  Multi-Col   Late-Col  Excess-Col  Carri-Sen      Runts
Te1/0/1               0          0          0           0          0          0
Te1/0/2               0          0          0           0          0          0
Te1/0/3               0          0          0           0          0          0
Te1/0/4               0          0          0           0          0          0
Te1/0/5               0          0          0           0          0          0
Te1/0/6               0          0          0           0          0          0
Te1/0/7               0          0          0           0          0          0
Te1/0/8               0          0          0           0          0          0
Te1/0/9               0          0          0           0          0          0
Te1/0/10              0          0          0           0          0          0
Te1/0/11              0          0          0           0          0          0
Te1/0/12              0          0          0           0          0          0
Te1/0/13              0          0          0           0          0          0
Te1/0/14              0          0          0           0          0          0
Te1/0/15              0          0          0           0          0          0
Te1/0/16              0          0          0           0          0          0
Te1/0/17              0          0          0           0          0          0
Te1/0/18              0          0          0           0          0          0
Te1/0/19              0          0          0           0          0          0
Te1/0/20              0          0          0           0          0          0
Te1/0/21              0          0          0           0          0          0
Te1/0/22              0          0          0           0          0          0
Te1/0/23              0          0          0           0          0          0
Te1/0/24              0          0          0           0          0          0
... (44 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces/interface"
```

### <a id="7-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-interfaces-oper:interface": [
    {
      "name": "AppGigabitEthernet1/0/1",
      "interface-type": "iana-iftype-ethernet-csmacd",
      "admin-status": "if-state-up",
      "oper-status": "if-oper-state-ready",
      "last-change": "2026-03-28T00:39:32.909+00:00",
      "if-index": 49,
      "phys-address": "70:0b:4f:f5:c2:a9",
      "speed": "1000000000",
      "statistics": {
        "discontinuity-time": "2026-03-28T00:37:20.565+00:00",
        "in-octets": "22839709",
        "in-unicast-pkts": "196153",
        "in-broadcast-pkts": "144304",
        "in-multicast-pkts": "144303",
        "in-discards": 0,
        "in-errors": 0,
        "in-unknown-protos": 0,
        "out-octets": 1044100730,
        "out-unicast-pkts": "13173835",
        "out-broadcast-pkts": "7523860",
        "out-multicast-pkts": "1276908",
        "out-discards": "0",
        "out-errors": "0",
        "rx-pps": "0",
        "rx-kbps": "0",
        "tx-pps": "9",
        "tx-kbps": "5",
        "num-flaps": "0",
        "in-crc-errors": "0",
        "in-discards-64": "0",
        "in-errors-64": "0",
        "in-unknown-protos-64": "0",
        "out-octets-64": "1044100730"
      },
      "vrf": "",
      "ipv4": "0.0.0.0",
      "ipv4-subnet-mask": "0.0.0.0",
      "description": "",
      "mtu": 1500,
      "input-security-acl": "",
      "output-security-acl": "",
      "v4-protocol-stats": {
        "in-pkts": "0",
        "in-octets": "0",
        "in-error-pkts": "0",
        "in-forwarded-pkts": "0",
        "in-forwarded-octets": "0",
        "in-discarded-pkts": "0",
        "out-pkts": "0",
        "out-octets": "0",
        "out-error-pkts": "0",
        "out-forwarded-pkts": "0",
        "out-forwarded-octets": "0",
        "out-discarded-pkts": "0"
      },
      "v6-protocol-stats": {
        "in-pkts": "0",
        "in-octets": "0",
        "in-error-pkts": "0",
        "in-forwarded-pkts": "0",
        "in-forwarded-octets": "0",
        "in-discarded-pkts": "0",
        "out-pkts": "0",
        "out-octets": "0",
        "out-error-pkts": "0",
        "out-forwarded-pkts": "0",
        "out-forwarded-octets": "0",
        "out-discarded-pkts": "0"
      },
      "bia-address": "70:0b:4f:f5:c2:a9",
      "ipv4-tcp-adjust-mss": 0,
      "ipv6-tcp-adjust-mss": 0,
      "intf-ext-state-support": [
        null
      ],
      "intf-ext-state": {
        "error-type": "port-error-none",
        "port-error-reason": "port-err-none",
        "auto-mdix-enabled": true,
        "mdix-oper-status-enabled": true,
        "fec-enabled": false,
        "mgig-downshift-enabled": false
      },
      "storm-control": {
        "broadcast": {},
        "multicast": {},
        "unicast": {},
        "unknown-unicast": {}
      },
      "auto-upstream-bandwidth": "0",
      "auto-downstream-bandwidth": "0",
      "bw-up-util": "0.0",
      "bw-down-util": "0.0",
      "ether-state": {
        "negotiated-duplex-mode": "full-duplex",
  ...
}
```

---

## 8. Spanning Tree Protocol (STP)

**YANG Module:** `Cisco-IOS-XE-spanning-tree-oper.yang`
**Telemetry XPath:** `/stp-ios-xe-oper:stp-details`

### CLI Show Commands

```
show spanning-tree
show spanning-tree summary
show spanning-tree detail
```

### <a id="8-cli-output"></a>CLI Output

**`show spanning-tree`**

```
VLAN0001
  Spanning tree enabled protocol rstp
  Root ID    Priority    32769
             Address     08ec.f5c7.da00
             Cost        20000
             Port        1 (TenGigabitEthernet1/0/1)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     700b.4ff5.c280
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Te1/0/1             Root FWD 20000     128.1    P2p Edge
Te1/0/3             Desg FWD 20000     128.3    P2p Edge
Te1/0/24            Desg FWD 2000      128.24   P2p



VLAN0100
  Spanning tree enabled protocol rstp
  Root ID    Priority    32868
             Address     08ec.f5c7.da00
             Cost        20000
             Port        1 (TenGigabitEthernet1/0/1)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32868  (priority 32768 sys-id-ext 100)
             Address     700b.4ff5.c280
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Te1/0/1             Root FWD 20000     128.1    P2p Edge
Te1/0/3             Desg FWD 20000     128.3    P2p Edge



VLAN0301
  Spanning tree enabled protocol rstp
  Root ID    Priority    33069
             Address     0005.73e3.56bc
             Cost        22000
             Port        24 (TenGigabitEthernet1/0/24)
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    33069  (priority 32768 sys-id-ext 301)
             Address     700b.4ff5.c280
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Te1/0/1             Desg FWD 20000     128.1    P2p Edge
Te1/0/3             Desg FWD 20000     128.3    P2p Edge
Te1/0/24            Root FWD 2000      128.24   P2p

... (28 more lines truncated)
```

**`show spanning-tree summary`**

```
Switch is in rapid-pvst mode
Root bridge for: none
Extended system ID                      is enabled
Portfast Default                        is disabled
Portfast Edge BPDU Guard Default        is disabled
Portfast Edge BPDU Filter Default       is disabled
Loopguard Default                       is disabled
BPDU sender conflict                    is enabled
PVST Simulation Default                 is enabled but inactive in rapid-pvst mode
Bridge Assurance                        is disabled
EtherChannel misconfig guard            is enabled
UplinkFast                              is disabled
BackboneFast                            is enabled but inactive in rapid-pvst mode
Configured Pathcost method used is long

Name                   Blocking Listening Learning Forwarding STP Active
---------------------- -------- --------- -------- ---------- ----------
VLAN0001                     0         0        0          3          3
VLAN0100                     0         0        0          2          2
VLAN0301                     0         0        0          3          3
VLAN0311                     0         0        0         11         11
---------------------- -------- --------- -------- ---------- ----------
4 vlans                      0         0        0         19         19
```

**`show spanning-tree detail`**

```
VLAN0001 is executing the rstp compatible Spanning Tree protocol
  Bridge Identifier has priority 32768, sysid 1, address 700b.4ff5.c280
  Configured hello time 2, max age 20, forward delay 15, transmit hold-count 6
  Current root has priority 32769, address 08ec.f5c7.da00
  Root port is 1 (TenGigabitEthernet1/0/1), cost of root path is 20000
  Topology change flag not set, detected flag not set
  Number of topology changes 3 last change occurred 2w1d ago
          from TenGigabitEthernet1/0/24
  Times:  hold 1, topology change 35, notification 2
          hello 2, max age 20, forward delay 15
  Timers: hello 0, topology change 0, notification 0, aging 300

 Port 1 (TenGigabitEthernet1/0/1) of VLAN0001 is root forwarding
   Port path cost 20000, Port priority 128, Port Identifier 128.1.
   Designated root has priority 32769, address 08ec.f5c7.da00
   Designated bridge has priority 32769, address 08ec.f5c7.da00
   Designated port id is 128.1, designated path cost 0
   Timers: message age 15, forward delay 0, hold 0
   Number of transitions to forwarding state: 1
   The port is in the portfast mode by portfast trunk configuration
   Link type is point-to-point by default
   BPDU: sent 8, received 687203

 Port 3 (TenGigabitEthernet1/0/3) of VLAN0001 is designated forwarding
   Port path cost 20000, Port priority 128, Port Identifier 128.3.
   Designated root has priority 32769, address 08ec.f5c7.da00
   Designated bridge has priority 32769, address 700b.4ff5.c280
   Designated port id is 128.3, designated path cost 20000
   Timers: message age 0, forward delay 0, hold 0
   Number of transitions to forwarding state: 1
   The port is in the portfast mode by portfast trunk configuration
   Link type is point-to-point by default
   BPDU: sent 687067, received 0

 Port 24 (TenGigabitEthernet1/0/24) of VLAN0001 is designated forwarding
   Port path cost 2000, Port priority 128, Port Identifier 128.24.
   Designated root has priority 32769, address 08ec.f5c7.da00
   Designated bridge has priority 32769, address 700b.4ff5.c280
   Designated port id is 128.24, designated path cost 20000
   Timers: message age 0, forward delay 0, hold 0
   Number of transitions to forwarding state: 1
   Link type is point-to-point by default
   BPDU: sent 687067, received 687025


 VLAN0100 is executing the rstp compatible Spanning Tree protocol
  Bridge Identifier has priority 32768, sysid 100, address 700b.4ff5.c280
  Configured hello time 2, max age 20, forward delay 15, transmit hold-count 6
  Current root has priority 32868, address 08ec.f5c7.da00
  Root port is 1 (TenGigabitEthernet1/0/1), cost of root path is 20000
  Topology change flag not set, detected flag not set
  Number of topology changes 2 last change occurred 2w1d ago
          from TenGigabitEthernet1/0/3
  Times:  hold 1, topology change 35, notification 2
          hello 2, max age 20, forward delay 15
  Timers: hello 0, topology change 0, notification 0, aging 300

 Port 1 (TenGigabitEthernet1/0/1) of VLAN0100 is root forwarding
   Port path cost 20000, Port priority 128, Port Identifier 128.1.
   Designated root has priority 32868, address 08ec.f5c7.da00
... (194 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-spanning-tree-oper:stp-details"
```

### <a id="8-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-spanning-tree-oper:stp-details": {
    "stp-detail": [
      {
        "instance": "VLAN0001",
        "hello-time": 2,
        "max-age": 20,
        "forwarding-delay": 15,
        "hold-count": 6,
        "bridge-priority": 32769,
        "bridge-address": "70:0b:4f:f5:c2:80",
        "designated-root-priority": 32769,
        "designated-root-address": "08:ec:f5:c7:da:00",
        "root-port": 1,
        "root-cost": "20000",
        "hold-time": "1",
        "topology-changes": "3",
        "time-of-last-topology-change": "1970-01-16T21:25:44+00:00",
        "interfaces": {},
        "root-if-name": "TenGigabitEthernet1/0/1",
        "protocol": "stp-proto-rstp",
        "aging-time": 300
      },
      {
        "instance": "VLAN0100",
        "hello-time": 2,
        "max-age": 20,
        "forwarding-delay": 15,
        "hold-count": 6,
        "bridge-priority": 32868,
        "bridge-address": "70:0b:4f:f5:c2:80",
        "designated-root-priority": 32868,
        "designated-root-address": "08:ec:f5:c7:da:00",
        "root-port": 1,
        "root-cost": "20000",
        "hold-time": "1",
        "topology-changes": "2",
        "time-of-last-topology-change": "1970-01-16T22:00:40+00:00",
        "interfaces": {},
        "root-if-name": "TenGigabitEthernet1/0/1",
        "protocol": "stp-proto-rstp",
        "aging-time": 300
      },
      {
        "instance": "VLAN0301",
        "hello-time": 2,
        "max-age": 20,
        "forwarding-delay": 15,
        "hold-count": 6,
        "bridge-priority": 33069,
        "bridge-address": "70:0b:4f:f5:c2:80",
        "designated-root-priority": 33069,
        "designated-root-address": "00:05:73:e3:56:bc",
        "root-port": 24,
        "root-cost": "22000",
        "hold-time": "1",
        "topology-changes": "9",
        "time-of-last-topology-change": "1970-01-15T23:27:02+00:00",
        "interfaces": {},
        "root-if-name": "TenGigabitEthernet1/0/24",
        "protocol": "stp-proto-rstp",
        "aging-time": 300
      },
      {
        "instance": "VLAN0311",
        "hello-time": 2,
        "max-age": 20,
        "forwarding-delay": 15,
        "hold-count": 6,
        "bridge-priority": 33079,
        "bridge-address": "70:0b:4f:f5:c2:80",
        "designated-root-priority": 33079,
        "designated-root-address": "00:05:73:e3:56:bc",
        "root-port": 24,
        "root-cost": "22000",
        "hold-time": "1",
        "topology-changes": "192",
        "time-of-last-topology-change": "1970-01-03T03:58:54+00:00",
        "interfaces": {},
        "root-if-name": "TenGigabitEthernet1/0/24",
        "protocol": "stp-proto-rstp",
        "aging-time": 300
      }
    ],
    "stp-vlan": [
      {
        "id": 1,
        "inst": "VLAN0001",
        "vlan-mode": "stp-mode-rapid-pvst",
        "des-root-pri": 32769,
        "des-root-addr": "08:ec:f5:c7:da:00",
        "des-brg-pri": 32769,
        "des-brg-addr": "70:0b:4f:f5:c2:80",
  ...
}
```

---

## 9. Stack Health

**YANG Module:** `Cisco-IOS-XE-stack-oper.yang`
**Telemetry XPath:** `/stack-ios-xe-oper:stack-oper-data`

### CLI Show Commands

```
show switch
show switch stack-ports
show switch stack-ring speed
```

### <a id="9-cli-output"></a>CLI Output

**`show switch`**

```
Switch/Stack Mac Address : 700b.4ff5.c280 - Local Mac Address
Mac persistency wait time: Indefinite
                                             H/W   Current
Switch#   Role    Mac Address     Priority Version  State
-------------------------------------------------------------------------------------
*1       Active   700b.4ff5.c280     1      V02     Ready
```

**`show switch stack-ports`**

```
Switch#   Port1     Port2
----------------------------
1         DOWN      DOWN
```

**`show switch stack-ring speed`**

```
Stack Ring Speed        : 240G
Stack Ring Configuration: Down
Stack Ring Protocol     : StackWise
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-stack-oper:stack-oper-data"
```

### <a id="9-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-stack-oper:stack-oper-data": {
    "stack-node": [
      {
        "chassis-number": 1,
        "priority": 1,
        "serial-number": "FOC2237U0A1",
        "latency": 0,
        "keepalive-counters": {},
        "interface-mtu": 1500,
        "role": "role-active",
        "node-state": "state-ready",
        "stack-mode": "mode-stackwise-rear",
        "sso-ready-flag": false,
        "mac-address": "70:0b:4f:f5:c2:80",
        "stack-ports": [],
        "reload-reason": "Reload Command",
        "hw-version": "V02",
        "mode": "stack-type-stacking",
        "configured-mode": "stack-mode-config-none",
        "mac-persistency-wait-time": 0,
        "mode-reload-pending": false,
        "topology": "stack-type-n-plus-one",
        "stack-bw": "480"
      }
    ],
    "stack-info": {
      "size": 1,
      "ring-speed": "240",
      "ring-status": "standalone",
      "stack-mac-address": "70:0b:4f:f5:c2:80",
      "stack-boottime": "2026-03-28T00:38:58+00:00"
    }
  }
}
```

---

## 10. VLANs

**YANG Module:** `Cisco-IOS-XE-vlan-oper.yang`
**Telemetry XPath:** `/vlan-ios-xe-oper:vlans`

### CLI Show Commands

```
show vlan brief
show vlan
```

### <a id="10-cli-output"></a>CLI Output

**`show vlan brief`**

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Te1/0/4, Te1/1/1, Te1/1/2, Te1/1/3, Te1/1/4, Te1/1/5, Te1/1/6, Te1/1/7
100  YANG_TEST_VLAN                   active
301  VLAN0301                         active
302  VLAN0302                         active
311  VLAN0311                         active    Te1/0/2, Te1/0/5, Te1/0/6, Te1/0/7, Te1/0/8, Te1/0/9, Te1/0/10, Te1/0/11, Te1/0/12, Te1/0/13, Te1/0/14, Te1/0/15, Te1/0/16, Te1/0/17, Te1/0/18, Te1/0/19
                                                Te1/0/20, Te1/0/21, Te1/0/22, Te1/0/23, Te1/1/8
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup
```

**`show vlan`**

```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Te1/0/4, Te1/1/1, Te1/1/2, Te1/1/3, Te1/1/4, Te1/1/5, Te1/1/6, Te1/1/7
100  YANG_TEST_VLAN                   active
301  VLAN0301                         active
302  VLAN0302                         active
311  VLAN0311                         active    Te1/0/2, Te1/0/5, Te1/0/6, Te1/0/7, Te1/0/8, Te1/0/9, Te1/0/10, Te1/0/11, Te1/0/12, Te1/0/13, Te1/0/14, Te1/0/15, Te1/0/16, Te1/0/17, Te1/0/18, Te1/0/19
                                                Te1/0/20, Te1/0/21, Te1/0/22, Te1/0/23, Te1/1/8
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
1004 fddinet-default                  act/unsup
1005 trnet-default                    act/unsup

VLAN Type  SAID       MTU   Parent RingNo BridgeNo Stp  BrdgMode Trans1 Trans2
---- ----- ---------- ----- ------ ------ -------- ---- -------- ------ ------
1    enet  100001     1500  -      -      -        -    -        0      0
100  enet  100100     1500  -      -      -        -    -        0      0
301  enet  100301     1500  -      -      -        -    -        0      0
302  enet  100302     1500  -      -      -        -    -        0      0
311  enet  100311     1500  -      -      -        -    -        0      0
1002 fddi  101002     1500  -      -      -        -    -        0      0
1003 tr    101003     1500  -      -      -        -    -        0      0
1004 fdnet 101004     1500  -      -      -        ieee -        0      0
1005 trnet 101005     1500  -      -      -        ibm  -        0      0

Remote SPAN VLANs
------------------------------------------------------------------------------


Primary Secondary Type              Ports
------- --------- ----------------- ------------------------------------------
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-vlan-oper:vlans"
```

### <a id="10-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-vlan-oper:vlans": {
    "vlan": [
      {
        "id": 1,
        "name": "default",
        "status": "active",
        "vlan-interfaces": []
      },
      {
        "id": 100,
        "name": "YANG_TEST_VLAN",
        "status": "active"
      },
      {
        "id": 301,
        "name": "VLAN0301",
        "status": "active"
      },
      {
        "id": 302,
        "name": "VLAN0302",
        "status": "active"
      },
      {
        "id": 311,
        "name": "VLAN0311",
        "status": "active",
        "vlan-interfaces": []
      },
      {
        "id": 1002,
        "name": "fddi-default",
        "status": "suspend"
      },
      {
        "id": 1003,
        "name": "token-ring-default",
        "status": "suspend"
      },
      {
        "id": 1004,
        "name": "fddinet-default",
        "status": "suspend"
      },
      {
        "id": 1005,
        "name": "trnet-default",
        "status": "suspend"
      }
    ]
  }
}
```

---

## 11. MAC Address Table

**YANG Module:** `Cisco-IOS-XE-matm-oper.yang`
**Telemetry XPath:** `/matm-ios-xe-oper:matm-oper-data`

### CLI Show Commands

```
show mac address-table
show mac address-table count
```

### <a id="11-cli-output"></a>CLI Output

**`show mac address-table`**

```
Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
 All    0100.0ccc.cccc    STATIC      CPU
 All    0100.0ccc.cccd    STATIC      CPU
 All    0180.c200.0000    STATIC      CPU
 All    0180.c200.0001    STATIC      CPU
 All    0180.c200.0002    STATIC      CPU
 All    0180.c200.0003    STATIC      CPU
 All    0180.c200.0004    STATIC      CPU
 All    0180.c200.0005    STATIC      CPU
 All    0180.c200.0006    STATIC      CPU
 All    0180.c200.0007    STATIC      CPU
 All    0180.c200.0008    STATIC      CPU
 All    0180.c200.0009    STATIC      CPU
 All    0180.c200.000a    STATIC      CPU
 All    0180.c200.000b    STATIC      CPU
 All    0180.c200.000c    STATIC      CPU
 All    0180.c200.000d    STATIC      CPU
 All    0180.c200.000e    STATIC      CPU
 All    0180.c200.000f    STATIC      CPU
 All    0180.c200.0010    STATIC      CPU
 All    0180.c200.0021    STATIC      CPU
 All    ffff.ffff.ffff    STATIC      CPU
   1    08ec.f5c7.da01    DYNAMIC     Te1/0/1
   1    4ce1.76c1.d5ec    DYNAMIC     Te1/0/3
   1    700b.4ff5.c2c7    STATIC      Vl1
   1    701f.539b.0f89    DYNAMIC     Te1/0/24
 311    000c.294d.bf01    DYNAMIC     Te1/0/24
 311    0050.568b.9c56    DYNAMIC     Te1/0/24
 311    00be.7549.f0c4    DYNAMIC     Te1/0/24
 311    00be.7549.f0ca    DYNAMIC     Te1/0/24
 311    0c7b.c8b9.ca1b    DYNAMIC     Te1/0/15
 311    149f.430f.5a80    DYNAMIC     Te1/0/14
 311    1c6a.7a38.2a02    DYNAMIC     Te1/0/24
 311    20cf.ae56.1c00    DYNAMIC     Te1/0/13
 311    4ce1.76c1.d5eb    DYNAMIC     Te1/0/3
 311    5254.dd27.88e5    DYNAMIC     Ap1/0/1
 311    5254.dd28.bed6    DYNAMIC     Ap1/0/1
 311    5254.dd3c.3bad    DYNAMIC     Ap1/0/1
 311    5254.dd49.9963    DYNAMIC     Ap1/0/1
 311    5254.dd4e.23f3    DYNAMIC     Ap1/0/1
 311    5254.dd6f.6a8b    DYNAMIC     Ap1/0/1
 311    5254.dd72.84b8    DYNAMIC     Te1/0/24
 311    5254.dd79.7e1b    DYNAMIC     Ap1/0/1
 311    5254.dd83.9973    DYNAMIC     Te1/0/24
 311    5254.dd88.2d9d    DYNAMIC     Ap1/0/1
 311    5254.dd96.63e3    DYNAMIC     Ap1/0/1
 311    5254.ddcb.7e04    DYNAMIC     Ap1/0/1
 311    6cd6.e359.20fc    DYNAMIC     Te1/0/16
 311    700b.4ff5.c2da    STATIC      Vl311
 311    701f.539b.0f89    DYNAMIC     Te1/0/24
 311    701f.539b.0fda    DYNAMIC     Te1/0/24
 311    70c9.c686.5b40    DYNAMIC     Te1/0/24
 311    a0e0.afcb.b500    DYNAMIC     Te1/0/5
 311    ecf4.0c01.7279    DYNAMIC     Te1/0/24
 311    f4ee.3184.bd46    DYNAMIC     Te1/1/8
 100    08ec.f5c7.da01    DYNAMIC     Te1/0/1
... (4 more lines truncated)
```

**`show mac address-table count`**

```
Mac Entries for Vlan 1:
---------------------------
Dynamic Address Count  : 3
Static  Address Count  : 1
Total Mac Addresses    : 4

Mac Entries for Vlan 311:
---------------------------
Dynamic Address Count  : 28
Static  Address Count  : 1
Total Mac Addresses    : 29

Mac Entries for Vlan 100:
---------------------------
Dynamic Address Count  : 1
Static  Address Count  : 0
Total Mac Addresses    : 1

Mac Entries for Vlan 301:
---------------------------
Dynamic Address Count  : 2
Static  Address Count  : 0
Total Mac Addresses    : 2

Mac Entries for Vlan 302:
---------------------------
Dynamic Address Count  : 1
Static  Address Count  : 0
Total Mac Addresses    : 1

Total Dynamic Address Count  : 35
Total Static  Address Count  : 2
Total Mac Address In Use     : 37
Total Mac Address Space Available: 32731
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-matm-oper:matm-oper-data"
```

### <a id="11-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-matm-oper:matm-oper-data": {
    "matm-table": [
      {
        "table-type": "mat-vlan",
        "vlan-id-number": 1,
        "aging-time": 300,
        "matm-mac-entry": []
      },
      {
        "table-type": "mat-vlan",
        "vlan-id-number": 100,
        "aging-time": 300,
        "matm-mac-entry": []
      },
      {
        "table-type": "mat-vlan",
        "vlan-id-number": 301,
        "aging-time": 300,
        "matm-mac-entry": []
      },
      {
        "table-type": "mat-vlan",
        "vlan-id-number": 302,
        "aging-time": 300,
        "matm-mac-entry": []
      },
      {
        "table-type": "mat-vlan",
        "vlan-id-number": 311,
        "aging-time": 300,
        "matm-mac-entry": []
      },
      {
        "table-type": "mat-vlan-independent",
        "vlan-id-number": 1,
        "aging-time": 0,
        "matm-mac-entry": []
      }
    ]
  }
}
```

---

## 12. ARP Table

**YANG Module:** `Cisco-IOS-XE-arp-oper.yang`
**Telemetry XPath:** `/arp-ios-xe-oper:arp-data`

### CLI Show Commands

```
show arp
show ip arp
```

### <a id="12-cli-output"></a>CLI Output

**`show arp`**

```
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.85.134.65            0   701f.539b.0fda  ARPA   Vlan311
Internet  10.85.134.70            -   700b.4ff5.c2da  ARPA   Vlan311
Internet  10.85.134.103           1   0050.568b.9c56  ARPA   Vlan311
Internet  10.85.134.108           0   00be.7549.f0ca  ARPA   Vlan311
Internet  10.85.134.117           0   0c7b.c8b9.ca1b  ARPA   Vlan311
Internet  10.85.134.126           0   1c6a.7a38.2a02  ARPA   Vlan311
```

**`show ip arp`**

```
Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  10.85.134.65            0   701f.539b.0fda  ARPA   Vlan311
Internet  10.85.134.70            -   700b.4ff5.c2da  ARPA   Vlan311
Internet  10.85.134.103           1   0050.568b.9c56  ARPA   Vlan311
Internet  10.85.134.108           0   00be.7549.f0ca  ARPA   Vlan311
Internet  10.85.134.117           0   0c7b.c8b9.ca1b  ARPA   Vlan311
Internet  10.85.134.126           0   1c6a.7a38.2a02  ARPA   Vlan311
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-arp-oper:arp-data"
```

### <a id="12-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-arp-oper:arp-data": {
    "arp-vrf": [
      {
        "vrf": "Default",
        "arp-oper": [],
        "arp-entry": []
      },
      {
        "vrf": "Mgmt-vrf"
      }
    ]
  }
}
```

---

## 13. LLDP Neighbors

**YANG Module:** `Cisco-IOS-XE-lldp-oper.yang`
**Telemetry XPath:** `/lldp-ios-xe-oper:lldp-entries`

### CLI Show Commands

```
show lldp neighbors
show lldp neighbors detail
```

### <a id="13-cli-output"></a>CLI Output

**`show lldp neighbors`**

```
Capability codes:
    (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
    (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other

Device ID           Local Intf     Hold-time  Capability      Port ID
JCOHOE VNC2 CiscoLabTe1/0/15       120        R               0
JCOHOE-C9300-TOR1.ciTe1/0/24       120        B,R             Te1/0/9
MEMY-C9300L-ZTP.net.Te1/1/8        120        B,R             Te1/1/1
AP149F.430F.5A80    Te1/0/14       120        B               Gi0
AP6CD6.E359.20FC    Te1/0/16       120        B               Gi0

Total entries displayed: 5
```

**`show lldp neighbors detail`**

```
------------------------------------------------
Local Intf: Te1/0/15
Local Intf service instance: -
Chassis id: 0c7b.c8b9.ca1a
Port id: 0
Port Description: internet port 0
System Name: JCOHOE VNC2 CiscoLab - appliance

System Description:
Meraki MX68 Router/Security Appliance

Time remaining: 110 seconds
System Capabilities: R
Enabled Capabilities: R
Management Addresses - not advertised
Auto Negotiation - not supported
Physical media capabilities - not advertised
Media Attachment Unit type - not advertised
Vlan ID: - not advertised
Peer Source MAC: 0c7b.c8b9.ca1b

------------------------------------------------
Local Intf: Te1/0/24
Local Intf service instance: -
Chassis id: 701f.539b.0f80
Port id: Te1/0/9
Port Description: JCOHOE-C9300-2
System Name: JCOHOE-C9300-TOR1.cisco.com

System Description:
Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2025 by Cisco Systems, Inc.
Compiled Fri 19-Dec-25 03:36 by mcpre

Time remaining: 104 seconds
System Capabilities: B,R
Enabled Capabilities: B,R
Management Addresses:
    IP: 10.85.134.193
Auto Negotiation - supported, enabled
Physical media capabilities:
    1000baseT(FD)
    100base-TX(FD)
    100base-TX(HD)
Media Attachment Unit type - not advertised
Vlan ID: 1
Peer Source MAC: 701f.539b.0f89

------------------------------------------------
Local Intf: Te1/1/8
Local Intf service instance: -
Chassis id: f4ee.3184.bd00
Port id: Te1/1/1
Port Description: "et-0/0/0:2 mem2-mc8-1:MS-MC"
System Name: MEMY-C9300L-ZTP.net.twttr.net

System Description:
Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
... (79 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-lldp-oper:lldp-entries/lldp-entry"
```

### <a id="13-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-lldp-oper:lldp-entry": [
    {
      "device-id": "AP6CD6.E359.20FC",
      "local-interface": "Te1/0/16",
      "connecting-interface": "Gi0",
      "ttl": 120,
      "capabilities": {
        "bridge": [
          null
        ]
      },
      "port-vlan-id": 0,
      "mau-type": 30,
      "auto-neg": {
        "enabled": [
          null
        ],
        "supported": [
          null
        ]
      },
      "local-efp-id": 0
    },
    {
      "device-id": "AP149F.430F.5A80",
      "local-interface": "Te1/0/14",
      "connecting-interface": "Gi0",
      "ttl": 120,
      "capabilities": {
        "bridge": [
          null
        ]
      },
      "port-vlan-id": 0,
      "mau-type": 30,
      "auto-neg": {
        "enabled": [
          null
        ],
        "supported": [
          null
        ]
      },
      "local-efp-id": 0
    },
    {
      "device-id": "MEMY-C9300L-ZTP.net.",
      "local-interface": "Te1/1/8",
      "connecting-interface": "Te1/1/1",
      "ttl": 120,
      "capabilities": {
        "bridge": [
          null
        ],
        "router": [
          null
        ]
      },
      "port-vlan-id": 0,
      "mau-type": 31,
      "auto-neg": {
        "enabled": [
          null
        ]
      },
      "local-efp-id": 0
    },
    {
      "device-id": "JCOHOE-C9300-TOR1.ci",
      "local-interface": "Te1/0/24",
      "connecting-interface": "Te1/0/9",
      "ttl": 120,
      "capabilities": {
        "bridge": [
          null
        ],
        "router": [
          null
        ]
      },
      "port-vlan-id": 1,
      "mau-type": 0,
      "auto-neg": {
        "enabled": [
          null
        ],
        "supported": [
          null
        ]
      },
      "local-efp-id": 0
    },
    {
      "device-id": "JCOHOE VNC2 CiscoLab",
      "local-interface": "Te1/0/15",
      "connecting-interface": "0",
      "ttl": 120,
      "capabilities": {
        "router": [
          null
        ]
      },
      "port-vlan-id": 0,
      "mau-type": 0,
      "local-efp-id": 0
    }
  ]
}
```

---

## 14. CDP Neighbors

**YANG Module:** `Cisco-IOS-XE-cdp-oper.yang`
**Telemetry XPath:** `/cdp-ios-xe-oper:cdp-neighbor-details`

### CLI Show Commands

```
show cdp neighbors
show cdp neighbors detail
```

### <a id="14-cli-output"></a>CLI Output

**`show cdp neighbors`**

```
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
MEMY-C9300L-ZTP.net.twttr.net
                 Ten 1/1/8         140             R S I  C9300L-24 Ten 1/1/1
JCOHOE-C9300-TOR1.cisco.com
                 Ten 1/0/24        149             R S I  C9300-24U Ten 1/0/9
CW_Core_MGMT.lab.sda
                 Ten 1/0/1         158              S I   C9200L-24 Gig 1/0/1
JCOHOE-9840-ZTP  Ten 1/0/3         154              R I   C9800-40- Ten 0/0/0
JCOHOE-C9600     Ten 1/0/13        127             R S I  C9606R    Gig 0/0
AP149F.430F.5A80 Ten 1/0/14        133              R T   CW9166I-A Gig 0
AP6CD6.E359.20FC Ten 1/0/16        134              R T   C9136I-A  Gig 0

Total cdp entries displayed : 7
```

**`show cdp neighbors detail`**

```
-------------------------
Device ID: MEMY-C9300L-ZTP.net.twttr.net
Entry address(es):
  IP address: 10.85.134.77
Platform: cisco C9300L-24UXG-4X,  Capabilities: Router Switch IGMP
Interface: TenGigabitEthernet1/1/8,  Port ID (outgoing port): TenGigabitEthernet1/1/1
Holdtime : 135 sec

advertisement version: 2
Peer Source MAC: f4ee.3184.bd46
VTP Management Domain: ''
Duplex: full
Management address(es):
  IP address: 10.85.134.77

-------------------------
Device ID: JCOHOE-C9300-TOR1.cisco.com
Entry address(es):
  IP address: 10.85.134.193
Platform: cisco C9300-24UX,  Capabilities: Router Switch IGMP
Interface: TenGigabitEthernet1/0/24,  Port ID (outgoing port): TenGigabitEthernet1/0/9
Holdtime : 143 sec

Version :
Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2025 by Cisco Systems, Inc.
Compiled Fri 19-Dec-25 03:36 by mcpre

advertisement version: 2
Peer Source MAC: 701f.539b.0f89
VTP Management Domain: ''
Native VLAN: 1
Duplex: full
Management address(es):
  IP address: 10.85.134.193

-------------------------
Device ID: CW_Core_MGMT.lab.sda
Entry address(es):
  IP address: 10.85.134.81
Platform: cisco C9200L-24P-4G,  Capabilities: Switch IGMP
Interface: TenGigabitEthernet1/0/1,  Port ID (outgoing port): GigabitEthernet1/0/1
Holdtime : 153 sec

Version :
Cisco IOS Software [Bengaluru], Catalyst L3 Switch Software (CAT9K_LITE_IOSXE), Version 17.6.3, RELEASE SOFTWARE (fc4)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2022 by Cisco Systems, Inc.
Compiled Wed 30-Mar-22 21:23 by mcpre

advertisement version: 2
Peer Source MAC: 08ec.f5c7.da01
VTP Management Domain: ''
Native VLAN: 1
Duplex: full
Management address(es):
  IP address: 10.85.134.81

-------------------------
... (90 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-cdp-oper:cdp-neighbor-details"
```

### <a id="14-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-cdp-oper:cdp-neighbor-details": {
    "cdp-neighbor-detail": [
      {
        "device-id": 206,
        "device-name": "JCOHOE-C9600",
        "local-intf-name": "TenGigabitEthernet1/0/13",
        "port-id": "GigabitEthernet0/0",
        "capability": "Router Switch IGMP ",
        "platform-name": "cisco C9606R",
        "version": "Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2025 by Cisco Systems, Inc.\nCompiled Fri 19-Dec-25 03:36 by mcpre",
        "duplex": "cdp-full-duplex",
        "adv-version": "cdp-advertised-v2",
        "hello-message": {},
        "vty-mgmt-domain": "",
        "native-vlan": 0,
        "vvid-tag": 0,
        "vvid": 0,
        "power": 0,
        "power-request": {},
        "power-available": {},
        "unidirectional-mode": "cdp-uni-mode-off",
        "spare-pair": {},
        "mgmt-address": "10.85.134.75",
        "ip-address": "10.85.134.75",
        "clns-address": "",
        "decnet-addr": "",
        "novell-addr": "",
        "second-port-status": "",
        "table-id": 0,
        "neighbor-identifier": "PID:C9606R,VID:V01,SN:FXS2535Q24U",
        "neighbor-port-mac": "20:cf:ae:56:1c:00"
      },
      {
        "device-id": 1240,
        "device-name": "JCOHOE-C9300-TOR1.cisco.com",
        "local-intf-name": "TenGigabitEthernet1/0/24",
        "port-id": "TenGigabitEthernet1/0/9",
        "capability": "Router Switch IGMP ",
        "platform-name": "cisco C9300-24UX",
        "version": "Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2025 by Cisco Systems, Inc.\nCompiled Fri 19-Dec-25 03:36 by mcpre",
        "duplex": "cdp-full-duplex",
        "adv-version": "cdp-advertised-v2",
        "hello-message": {},
        "vty-mgmt-domain": "",
        "native-vlan": 1,
        "vvid-tag": 0,
        "vvid": 0,
        "power": 0,
        "power-request": {},
        "power-available": {},
        "unidirectional-mode": "cdp-uni-mode-off",
        "spare-pair": {},
        "mgmt-address": "10.85.134.193",
        "ip-address": "10.85.134.193",
        "clns-address": "",
        "decnet-addr": "",
        "novell-addr": "",
        "second-port-status": "",
        "table-id": 0,
        "neighbor-identifier": "PID:C9300-24UX,VID:A0,SN:FCW2134L0VB",
        "neighbor-port-mac": "70:1f:53:9b:0f:89"
      },
      {
        "device-id": 2041,
        "device-name": "CW_Core_MGMT.lab.sda",
        "local-intf-name": "TenGigabitEthernet1/0/1",
        "port-id": "GigabitEthernet1/0/1",
        "capability": "Switch IGMP ",
        "platform-name": "cisco C9200L-24P-4G",
  ...
}
```

---

## 15. Platform Components

**YANG Module:** `Cisco-IOS-XE-platform-oper.yang`
**Telemetry XPath:** `/platform-ios-xe-oper:components`

### CLI Show Commands

```
show platform
show inventory
```

### <a id="15-cli-output"></a>CLI Output

**`show platform`**

```
Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver.
------  -----   ---------             -----------  --------------  -------       --------
 1       41     C9300-24UX            FOC2237U0A1  700b.4ff5.c280  V02           17.18.02
Switch/Stack Mac Address : 700b.4ff5.c280 - Local Mac Address
Mac persistency wait time: Indefinite
                                   Current
Switch#   Role        Priority      State
-------------------------------------------
*1       Active          1          Ready
```

**`show inventory`**

```
NAME: "c93xx Stack", DESCR: "c93xx Stack"
PID: C9300-24UX        , VID: V02  , SN: FOC2237U0A1

NAME: "Switch 1", DESCR: "C9300-24UX"
PID: C9300-24UX        , VID: V02  , SN: FOC2237U0A1

NAME: "Switch 1 - Power Supply B", DESCR: "Switch 1 - Power Supply B"
PID: PWR-C1-1100WAC-P  , VID: V01  , SN: ART2219FA4U

NAME: "Switch 1 FRU Uplink Module 1", DESCR: "8x10G Uplink Module"
PID: C9300-NM-8X       , VID: V02  , SN: FOC22471DGB

NAME: "Te1/1/1", DESCR: "1000BaseSX SFP"
PID:                     , VID:      , SN: AGM12011449

NAME: "Te1/1/3", DESCR: "1000BaseSX SFP"
PID:                     , VID:      , SN: AGM1614L4U5

NAME: "Te1/1/8", DESCR: "SFP-10GBase-CX1"
PID: SFP-H10GB-CU1M      , VID: V03  , SN: CSC231211260008

NAME: "usbflash1", DESCR: "usbflash1-1"
PID: SSD-120G          , VID: 3.10 , SN: STP234702U6
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-platform-oper:components"
```

### <a id="15-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-platform-oper:components": {
    "component": [
      {
        "cname": "Fan1/1",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "Fan1/2",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "Fan1/3",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "Switch1",
        "state": {},
        "platform-properties": {},
        "platform-subcomponents": {}
      },
      {
        "cname": "usbflash1",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "c93xx Stack",
        "state": {},
        "platform-subcomponents": {}
      },
      {
        "cname": "RPSContainer1",
        "state": {}
      },
      {
        "cname": "FixedModule1/0",
        "state": {}
      },
      {
        "cname": "PowerSupply1/A",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "PowerSupply1/B",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "FanContainer1/1",
        "state": {}
      },
      {
        "cname": "FanContainer1/2",
        "state": {}
      },
      {
        "cname": "FanContainer1/3",
        "state": {}
      },
      {
        "cname": "InletTempSensor1",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "OutletTempSensor1",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "FRUUplinkModule1/1",
        "state": {}
      },
      {
        "cname": "HotSpotTempSensor1",
        "state": {},
        "platform-properties": {}
      },
      {
        "cname": "FRULinkContainer1/1",
        "state": {}
      },
      {
        "cname": "PowerSupplyContainer1/A",
        "state": {}
      },
      {
        "cname": "PowerSupplyContainer1/B",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/1",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/2",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/3",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/4",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/5",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/6",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/7",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/8",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/9",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/1/1",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/1/3",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/1/8",
        "state": {}
      },
      {
        "cname": "TenGigabitEthernet1/0/10",
        "state": {}
      },
      {
  ...
}
```

---

## 16. Device Hardware

**YANG Module:** `Cisco-IOS-XE-device-hardware-oper.yang`
**Telemetry XPath:** `/device-hardware-xe-oper:device-hardware-data/device-hardware`

### CLI Show Commands

```
show version
show inventory
show platform software device-hardware
```

### <a id="16-cli-output"></a>CLI Output

**`show version`**

```
Cisco IOS XE Software, Version 17.18.02
Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2025 by Cisco Systems, Inc.
Compiled Fri 19-Dec-25 03:36 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2025 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMONBOOTLDR: System Bootstrap, Version 17.15.1r, RELEASE SOFTWARE (P)

JCOHOE-C9300-2 uptime is 2 weeks, 1 day, 22 hours, 23 minutes
Uptime for this control processor is 2 weeks, 1 day, 22 hours, 25 minutes
System returned to ROM by Reload Command at 01:36:02 PDT Sat Mar 28 2026
System image file is "flash:packages.conf"
Last reload reason: Reload Command



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.


Technology Package License Information:

------------------------------------------------------------------------------
Technology-package                                     Technology-package
Current                        Type                       Next reboot
------------------------------------------------------------------------------
network-advantage   	Smart License                 	 network-advantage
dna-advantage       	Subscription Smart License    	 dna-advantage


Smart Licensing Status: Smart Licensing Using Policy

cisco C9300-24UX (X86) processor with 1049141K/6147K bytes of memory.
Processor board ID FOC2237U0A1
3 Virtual Ethernet interfaces
4 Gigabit Ethernet interfaces
... (23 more lines truncated)
```

**`show inventory`**

```
NAME: "c93xx Stack", DESCR: "c93xx Stack"
PID: C9300-24UX        , VID: V02  , SN: FOC2237U0A1

NAME: "Switch 1", DESCR: "C9300-24UX"
PID: C9300-24UX        , VID: V02  , SN: FOC2237U0A1

NAME: "Switch 1 - Power Supply B", DESCR: "Switch 1 - Power Supply B"
PID: PWR-C1-1100WAC-P  , VID: V01  , SN: ART2219FA4U

NAME: "Switch 1 FRU Uplink Module 1", DESCR: "8x10G Uplink Module"
PID: C9300-NM-8X       , VID: V02  , SN: FOC22471DGB

NAME: "Te1/1/1", DESCR: "1000BaseSX SFP"
PID:                     , VID:      , SN: AGM12011449

NAME: "Te1/1/3", DESCR: "1000BaseSX SFP"
PID:                     , VID:      , SN: AGM1614L4U5

NAME: "Te1/1/8", DESCR: "SFP-10GBase-CX1"
PID: SFP-H10GB-CU1M      , VID: V03  , SN: CSC231211260008

NAME: "usbflash1", DESCR: "usbflash1-1"
PID: SSD-120G          , VID: 3.10 , SN: STP234702U6
```

**`show platform software device-hardware`**

```
^
% Invalid input detected at '^' marker.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-device-hardware-oper:device-hardware-data/device-hardware"
```

### <a id="16-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-device-hardware-oper:device-hardware": {
    "device-inventory": [
      {
        "hw-type": "hw-type-emmc",
        "hw-dev-index": 0,
        "version": "V02",
        "part-number": "C9300-24UX",
        "serial-number": "FOC2237U0A1",
        "hw-description": "c93xx Stack",
        "dev-name": "c93xx Stack",
        "field-replaceable": false,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-chassis",
        "hw-dev-index": 1,
        "version": "V02",
        "part-number": "C9300-24UX",
        "serial-number": "FOC2237U0A1",
        "hw-description": "C9300-24UX",
        "dev-name": "Switch 1",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-pem",
        "hw-dev-index": 2,
        "version": "V01",
        "part-number": "PWR-C1-1100WAC-P  ",
        "serial-number": "ART2219FA4U",
        "hw-description": "Switch 1 - Power Supply B",
        "dev-name": "Switch 1 - Power Supply B",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-pim",
        "hw-dev-index": 3,
        "version": "V02",
        "part-number": "C9300-NM-8X       ",
        "serial-number": "FOC22471DGB",
        "hw-description": "8x10G Uplink Module",
        "dev-name": "Switch 1 FRU Uplink Module 1",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-transceiver",
        "hw-dev-index": 4,
        "version": "    ",
        "part-number": "                    ",
        "serial-number": "AGM12011449     ",
        "hw-description": "1000BaseSX SFP",
        "dev-name": "Te1/1/1",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-transceiver",
        "hw-dev-index": 5,
        "version": "    ",
        "part-number": "                    ",
        "serial-number": "AGM1614L4U5     ",
        "hw-description": "1000BaseSX SFP",
        "dev-name": "Te1/1/3",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-transceiver",
        "hw-dev-index": 6,
        "version": "V03 ",
        "part-number": "SFP-H10GB-CU1M      ",
        "serial-number": "CSC231211260008 ",
        "hw-description": "SFP-10GBase-CX1",
        "dev-name": "Te1/1/8",
        "field-replaceable": true,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-dram",
        "hw-dev-index": 7,
        "version": "",
        "part-number": "",
        "serial-number": "",
        "hw-description": "Physical Memory",
        "dev-name": "Memory",
        "field-replaceable": false,
        "hw-class": "hw-class-physical"
      },
      {
        "hw-type": "hw-type-cpu",
        "hw-dev-index": 8,
        "version": " 6",
        "part-number": " GenuineIntel",
  ...
}
```

---

## 17. Switchport

**YANG Module:** `Cisco-IOS-XE-switchport-oper.yang`
**Telemetry XPath:** `/switchport-ios-xe-oper:switchport-oper-data`

### CLI Show Commands

```
show interfaces switchport
show interfaces trunk
```

### <a id="17-cli-output"></a>CLI Output

**`show interfaces switchport`**

```
Name: Te1/0/1
Switchport: Enabled
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: dot1q
Negotiation of Trunking: On
Access Mode VLAN: 1 (default)
Trunking Native Mode VLAN: 1 (default)
Administrative Native VLAN tagging: enabled
Voice VLAN: none
Administrative private-vlan host-association: none
Administrative private-vlan mapping: none
Administrative private-vlan trunk native VLAN: none
Administrative private-vlan trunk Native VLAN tagging: enabled
Administrative private-vlan trunk encapsulation: dot1q
Administrative private-vlan trunk normal VLANs: none
Administrative private-vlan trunk associations: none
Administrative private-vlan trunk mappings: none
Operational private-vlan: none
Trunking VLANs Enabled: ALL
Pruning VLANs Enabled: 2-1001
Capture Mode Disabled
Capture VLANs Allowed: ALL

Protected: false
Unknown unicast blocked: disabled
Unknown multicast blocked: disabled
Vepa Enabled: false
App Interface: false
Appliance trust: none

Name: Te1/0/2
Switchport: Enabled
Administrative Mode: dynamic auto
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: On
Access Mode VLAN: 311 (VLAN0311)
Trunking Native Mode VLAN: 1 (default)
Administrative Native VLAN tagging: enabled
Voice VLAN: none
Administrative private-vlan host-association: none
Administrative private-vlan mapping: none
Administrative private-vlan trunk native VLAN: none
Administrative private-vlan trunk Native VLAN tagging: enabled
Administrative private-vlan trunk encapsulation: dot1q
Administrative private-vlan trunk normal VLANs: none
Administrative private-vlan trunk associations: none
Administrative private-vlan trunk mappings: none
Operational private-vlan: none
Trunking VLANs Enabled: ALL
Pruning VLANs Enabled: 2-1001
Capture Mode Disabled
Capture VLANs Allowed: ALL

Protected: false
Unknown unicast blocked: disabled
Unknown multicast blocked: disabled
... (1013 more lines truncated)
```

**`show interfaces trunk`**

```
Port           Mode             Encapsulation  Status        Native vlan
Te1/0/1        on               802.1q         trunking      1
Te1/0/3        on               802.1q         trunking      1
Te1/0/24       on               802.1q         trunking      1
Ap1/0/1        on               802.1q         trunking      1

Port           Vlans allowed on trunk
Te1/0/1        1-4094
Te1/0/3        1-4094
Te1/0/24       1,301-302,311
Ap1/0/1        311

Port           Vlans allowed and active in management domain
Te1/0/1        1,100,301-302,311
Te1/0/3        1,100,301-302,311
Te1/0/24       1,301-302,311
Ap1/0/1        311

Port           Vlans in spanning tree forwarding state and not pruned
Te1/0/1        1,100,301-302,311
Te1/0/3        1,100,301-302,311
Te1/0/24       1,301-302,311
Ap1/0/1        311
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-switchport-oper:switchport-oper-data"
```

### <a id="17-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-switchport-oper:switchport-oper-data": {
    "switchport-info": [
      {
        "if-name": "TwentyFiveGigE1/1/1",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "TwentyFiveGigE1/1/2",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "GigabitEthernet1/1/1",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "GigabitEthernet1/1/2",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "GigabitEthernet1/1/3",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "GigabitEthernet1/1/4",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto"
      },
      {
        "if-name": "AppGigabitEthernet1/0/1",
        "enabled": [
          null
        ],
        "admin-mode": "admin-trunk",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/1",
        "enabled": [
          null
        ],
        "admin-mode": "admin-trunk",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/2",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/3",
        "enabled": [
          null
        ],
        "admin-mode": "admin-trunk",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/4",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/5",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/6",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/7",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
        "hardware-present": [
          null
        ]
      },
      {
        "if-name": "TenGigabitEthernet1/0/8",
        "enabled": [
          null
        ],
        "admin-mode": "admin-dyn-auto",
        "port-details": {},
  ...
}
```

---

## 18. Transceiver / Optics

**YANG Module:** `Cisco-IOS-XE-transceiver-oper.yang`
**Telemetry XPath:** `/xcvr-ios-xe-oper:transceiver-oper-data`

### CLI Show Commands

```
show interfaces transceiver
show interfaces transceiver detail
```

### <a id="18-cli-output"></a>CLI Output

**`show interfaces transceiver`**

```
No transceiver present
```

**`show interfaces transceiver detail`**

```
No transceiver present
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-transceiver-oper:transceiver-oper-data"
```

### <a id="18-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-transceiver-oper:transceiver-oper-data": {
    "transceiver": [
      {
        "name": "TenGigabitEthernet1/1/1",
        "enabled": true,
        "present": true,
        "identifier": "SFP/SFP+",
        "connector": "LC connector",
        "ethernet-pmd": "1000BaseSX SFP",
        "vendor": "CISCO-AVAGO",
        "vendor-part": "SFBR-5766PZ",
        "vendor-rev": "",
        "serial-no": "AGM12011449",
        "fault-condition": false,
        "date": "080102",
        "sonet": "unknown",
        "otn": "otn-undefined",
        "internal-temp": "0.0",
        "output-power": {},
        "input-power": {},
        "laser-bias-current": {},
        "xcvr-physical-channel": [],
        "fault-reason": "port-err-none",
        "last-event-time": "2026-03-28T00:39:59+00:00",
        "ext-id": "ext-id-defined-by-two-wire-interface",
        "ten-gig-comp": "comp-unknown",
        "ge-comp": "gecomp-1000-base-sx",
        "link-length": "ll-unknown",
        "tech": "tech-unknown",
        "media": "media-unknown",
        "speed": "speed-unknown",
        "enc": "enc-8b10b",
        "bit-rate": {},
        "length": {},
        "wavelength": "850.0",
        "check-code-base": "ed",
        "check-code-ext": "90",
        "options": "00:1a",
        "int-clbr": false,
        "ext-clbr": false,
        "rx-power": "rx-power-oma",
        "address-change": "address-change-not-required",
        "other-info": {},
        "raw-data": "03:04:07:00:00:00:01:00:00:00:00:01:0d:00:00:00:37:1b:00:00:43:49:53:43:4f:2d:41:56:41:47:4f:20:20:20:20:20:00:00:17:6a:53:46:42:52:2d:35:37:36:36:50:5a:20:20:20:20:20:20:20:20:20:03:52:00:ed:00:1a:00:00:41:47:4d:31:32:30:31:31:34:34:39:20:20:20:20:20:30:38:30:31:30:32:20:20:00:00:00:90:00:00:06:3e:49:3d:7e:83:fd:ea:51:ae:d9:7d:a5:d8:c2:47:55:00:00:00:00:00:00:00:00:00:06:e6:1d:32",
        "voltage": {},
        "int-temp-thold": {},
        "cur-thold": {},
        "op-thold": {},
        "ip-thold": {},
        "volt-thold": {},
        "diag-mon-impl": "dm-impl"
      },
      {
        "name": "TenGigabitEthernet1/1/3",
        "enabled": true,
        "present": true,
        "identifier": "SFP/SFP+",
        "connector": "LC connector",
        "ethernet-pmd": "1000BaseSX SFP",
        "vendor": "CISCO-AVAGO",
        "vendor-part": "SFBR-5766PZ-CS2",
        "vendor-rev": "",
        "serial-no": "AGM1614L4U5",
        "fault-condition": false,
        "date": "120406",
        "sonet": "unknown",
        "otn": "otn-undefined",
        "internal-temp": "0.0",
        "output-power": {},
        "input-power": {},
        "laser-bias-current": {},
        "xcvr-physical-channel": [],
        "fault-reason": "port-err-none",
        "last-event-time": "2026-03-28T00:40:00+00:00",
        "ext-id": "ext-id-defined-by-two-wire-interface",
        "ten-gig-comp": "comp-unknown",
        "ge-comp": "gecomp-1000-base-sx",
        "link-length": "ll-unknown",
        "tech": "tech-unknown",
  ...
}
```

---

## 19. UDLD

**YANG Module:** `Cisco-IOS-XE-udld-oper.yang`
**Telemetry XPath:** `/udld-ios-xe-oper:udld-oper-data`

### CLI Show Commands

```
show udld
show udld neighbors
```

### <a id="19-cli-output"></a>CLI Output

**`show udld`**

```
Interface Te1/0/1
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/2
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/3
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/4
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/5
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/6
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/7
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/8
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/9
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

Interface Te1/0/10
---
Port enable administrative configuration setting: Disabled
Port enable operational state: Disabled
Current bidirectional state: Unknown

... (185 more lines truncated)
```

**`show udld neighbors`**

```
Port           Device Name     Device ID    Port ID         Neighbor State
----           -----------     ---------    -------         --------------

Total number of bidirectional entries displayed: 0
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-udld-oper:udld-oper-data"
```

### <a id="19-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 20. 802.1X / Identity Sessions

**YANG Module:** `Cisco-IOS-XE-identity-oper.yang`
**Telemetry XPath:** `/identity-ios-xe-oper:identity-oper-data`

### CLI Show Commands

```
show dot1x all summary
show authentication sessions
show access-session
```

### <a id="20-cli-output"></a>CLI Output

**`show dot1x all summary`**

```
Interface                PAE     Client          Status
------------------------------------------------------------------
```

**`show authentication sessions`**

```
No sessions currently exist
```

**`show access-session`**

```
No sessions currently exist
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-identity-oper:identity-oper-data"
```

### <a id="20-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-identity-oper:identity-oper-data": {
    "dot1x-global-stats": {
      "eapol-rx": 0,
      "eapol-rx-start": 0,
      "eapol-rx-logoff": 0,
      "eapol-rx-resp": 0,
      "eapol-rx-resp-id": 0,
      "eapol-rx-req": 0,
      "eapol-rx-invalid": 0,
      "eapol-rx-len-error": 0,
      "eapol-tx": 0,
      "eapol-tx-start": 0,
      "eapol-tx-logoff": 0,
      "eapol-tx-resp": 0,
      "eapol-tx-req": 0,
      "eapol-retx-req": 0,
      "eapol-retx-req-fail": 0,
      "eapol-tx-req-id": 0,
      "eapol-retx-req-id": 0,
      "eapol-retx-req-id-fail": 0
    },
    "webauth-stats": {
      "http-stats": {},
      "iom-reading": {},
      "method-reading": {},
      "iom-writing": {},
      "method-writing": {},
      "iom-aaa": {},
      "method-aaa": {},
      "num-of-sleeping-clients": 0,
      "session-count": 0,
      "half-open-count": 0,
      "backpressure-counters": {}
    }
  }
}
```

---

## 21. TCAM Utilization

**YANG Module:** `Cisco-IOS-XE-tcam-oper.yang`
**Telemetry XPath:** `/tcam-ios-xe-oper:tcam-details`

### CLI Show Commands

```
show platform hardware fed switch active fwd-asic resource tcam utilization
show sdm prefer
```

### <a id="21-cli-output"></a>CLI Output

**`show platform hardware fed switch active fwd-asic resource tcam utilization`**

```
Codes: EM - Exact_Match, I - Input, O - Output, IO - Input & Output, NA - Not Applicable

CAM Utilization for ASIC  [0]
 Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
 ------------------------------------------------------------------------------------------------------
 Mac Address Table      EM           I       32768       55    0.17%        0        0        0       55
 Mac Address Table      TCAM         I        1024       22    2.15%        0        0        0       22
 L3 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L3 Multicast           TCAM         I         512        9    1.76%        3        6        0        0
 L2 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L2 Multicast           TCAM         I         512       11    2.15%        3        8        0        0
 IP Route Table         EM           I       24576       11    0.04%       10        0        1        0
 IP Route Table         TCAM         I        8192       20    0.24%        7       10        2        1
 QOS ACL                TCAM         IO       5120       85    1.66%       28       38        0       19
                        TCAM         I                   45    0.88%       15       20        0       10
                        TCAM         O                   40    0.78%       13       18        0        9
 Security ACL           TCAM         IO       5120      149    2.91%       26       78        0       45
                        TCAM         I                  106    2.07%       12       54        0       40
                        TCAM         O                   43    0.84%       14       24        0        5
 Netflow ACL            TCAM         I         256        6    2.34%        2        2        0        2
 PBR ACL                TCAM         I        1024       36    3.52%       30        6        0        0
 Netflow ACL            TCAM         O         768        6    0.78%        2        2        0        2
 Flow SPAN ACL          TCAM         IO       1024       13    1.27%        3        6        0        4
                        TCAM         I                    5    0.49%        1        2        0        2
                        TCAM         O                    8    0.78%        2        4        0        2
 Control Plane          TCAM         I         512      290   56.64%      138      106        0       46
 Tunnel Termination     TCAM         I         512       20    3.91%        8       12        0        0
 Lisp Inst Mapping      TCAM         I        2048        1    0.05%        0        0        0        1
 Security Association   TCAM         I         256        4    1.56%        2        2        0        0
 CTS Cell Matrix/VPN
 Label                  EM           O        8192        0    0.00%        0        0        0        0
 CTS Cell Matrix/VPN
 Label                  TCAM         O         512        1    0.20%        0        0        0        1
 Client Table           EM           I        4096        0    0.00%        0        0        0        0
 Client Table           TCAM         I         256        0    0.00%        0        0        0        0
 Input Group LE         TCAM         I        1024        0    0.00%        0        0        0        0
 Output Group LE        TCAM         O        1024        0    0.00%        0        0        0        0
 Macsec SPD             TCAM         I         256        2    0.78%        0        0        0        2
CAM Utilization for ASIC  [1]
 Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
 ------------------------------------------------------------------------------------------------------
 Mac Address Table      EM           I       32768       55    0.17%        0        0        0       55
 Mac Address Table      TCAM         I        1024       22    2.15%        0        0        0       22
 L3 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L3 Multicast           TCAM         I         512        9    1.76%        3        6        0        0
 L2 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L2 Multicast           TCAM         I         512       11    2.15%        3        8        0        0
 IP Route Table         EM           I       24576       11    0.04%       10        0        1        0
 IP Route Table         TCAM         I        8192       20    0.24%        7       10        2        1
 QOS ACL                TCAM         IO       5120       81    1.58%       27       36        0       18
                        TCAM         I                   45    0.88%       15       20        0       10
                        TCAM         O                   36    0.70%       12       16        0        8
 Security ACL           TCAM         IO       5120      149    2.91%       26       78        0       45
                        TCAM         I                  106    2.07%       12       54        0       40
                        TCAM         O                   43    0.84%       14       24        0        5
 Netflow ACL            TCAM         I         256        6    2.34%        2        2        0        2
 PBR ACL                TCAM         I        1024       36    3.52%       30        6        0        0
 Netflow ACL            TCAM         O         768        6    0.78%        2        2        0        2
 Flow SPAN ACL          TCAM         IO       1024       13    1.27%        3        6        0        4
                        TCAM         I                    5    0.49%        1        2        0        2
... (14 more lines truncated)
```

**`show sdm prefer`**

```
Showing SDM Template Info

This is the Access template.
  Number of VLANs:                                     4094
  Unicast MAC addresses:                               32768
  Overflow Unicast MAC addresses:                      1024
  L2 Multicast entries:                                8192
  Overflow L2 Multicast entries:                       512
  L3 Multicast entries:                                8192
  Overflow L3 Multicast entries:                       512
  Directly connected routes:                           24576
  Indirect routes:                                     8192
  Security Access Control Entries:                     5120
  QoS Access Control Entries:                          5120
  Policy Based Routing ACEs:                           1024
  Netflow Input ACEs:                                  256
  Netflow Output ACEs:                                 768
  Flow SPAN ACEs:                                      1024
  Tunnels:                                             512
  LISP Instance Mapping Entries:                       2048
  Control Plane Entries:                               512
  Input Netflow flows:                                 32768
  Output Netflow flows:                                32768
  SGT/DGT (or) MPLS VPN entries:                       8192
  SGT/DGT (or) MPLS VPN Overflow entries:              512
  Wired clients:                                       2048
  MACSec SPD Entries:                                  256
  VRF:                                                 256
  MPLS Labels:                                         8192
  MPLS L3 VPN Routes VRF Mode:                         7168
  MPLS L3 VPN Routes Prefix Mode:                      8192
  MVPN MDT Tunnels:                                    256
  L2 VPN EOMPLS Attachment Circuit:                    256
  MAX VPLS Bridge Domains :                            128
  MAX VPLS Peers Per Bridge Domain:                    32
  MAX VPLS/VPWS Pseudowires :                          1024

These numbers are typical for L2 and IPv4 features.
Some features such as IPv6, use up double the entry size;
so only half as many entries can be created.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-tcam-oper:tcam-details"
```

### <a id="21-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-tcam-oper:tcam-details": {
    "tcam-detail": [
      {
        "asic-no": 0,
        "name": "PBR ACL",
        "hash-entries-max": 0,
        "tcam-entries-max": 1024,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "QOS ACL",
        "hash-entries-max": 0,
        "tcam-entries-max": 5120,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Group LE",
        "hash-entries-max": 0,
        "tcam-entries-max": 1024,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Macsec SPD",
        "hash-entries-max": 0,
        "tcam-entries-max": 256,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Netflow ACL",
        "hash-entries-max": 0,
        "tcam-entries-max": 256,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Client Table",
        "hash-entries-max": 4096,
        "tcam-entries-max": 256,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "L2 Multicast",
        "hash-entries-max": 8192,
        "tcam-entries-max": 512,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "L3 Multicast",
        "hash-entries-max": 8192,
        "tcam-entries-max": 512,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Security ACL",
        "hash-entries-max": 0,
        "tcam-entries-max": 5120,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Control Plane",
        "hash-entries-max": 0,
        "tcam-entries-max": 512,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Flow SPAN ACL",
        "hash-entries-max": 0,
        "tcam-entries-max": 1024,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "IP Route Table",
        "hash-entries-max": 0,
        "tcam-entries-max": 4096,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "CTS Cell Matrix",
        "hash-entries-max": 8192,
        "tcam-entries-max": 512,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Lisp Inst Mapping",
        "hash-entries-max": 0,
        "tcam-entries-max": 2048,
        "hash-entries-used": 0,
        "tcam-entries-used": 0
      },
      {
        "asic-no": 0,
        "name": "Mac Address Table",
        "hash-entries-max": 32768,
        "tcam-entries-max": 1024,
  ...
}
```

---

## 22. MDT Subscription Health

**YANG Module:** `Cisco-IOS-XE-mdt-oper-v2.yang`
**Telemetry XPath:** `/mdt-oper-v2:mdt-oper-v2-data`

### CLI Show Commands

```
show telemetry ietf subscription all
show telemetry ietf subscription all detail
show telemetry connection all
```

### <a id="22-cli-output"></a>CLI Output

**`show telemetry ietf subscription all`**

```
ID         Type       State      State Description
500        Configured Valid      Subscription validated
501        Configured Valid      Subscription validated
502        Configured Valid      Subscription validated
503        Configured Valid      Subscription validated
504        Configured Valid      Subscription validated
750        Configured Valid      Subscription validated
751        Configured Valid      Subscription validated
8882       Configured Valid      Subscription validated
```

**`show telemetry ietf subscription all detail`**

```
Telemetry subscription detail:

  Subscription ID: 500
  Type: Configured
  State: Valid
  Stream: native
  Filter:
    Filter type: tdl-uri
    TDL-URI: /services;serviceName=ios_oper/poe_port_detail
  Update policy:
    Update Trigger: periodic
    Period: 60000
  Encoding: encode-tdl
  Source VRF:
  Source Address: 10.85.134.70
  Receiver Type: protocol
  Notes: Subscription validated

  Named Receivers:
    Name                                              Last State Change  State                 Explanation
    -------------------------------------------------------------------------------------------------------------------------------------------------------
    DNAC_ASSURANCE_RECEIVER                           03/30/26 04:56:20  Connected

  Subscription ID: 501
  Type: Configured
  State: Valid
  Stream: native
  Filter:
    Filter type: tdl-uri
    TDL-URI: /services;serviceName=ios_oper/poe_module
  Update policy:
    Update Trigger: periodic
    Period: 60000
  Encoding: encode-tdl
  Source VRF:
  Source Address: 10.85.134.70
  Receiver Type: protocol
  Notes: Subscription validated

  Named Receivers:
    Name                                              Last State Change  State                 Explanation
    -------------------------------------------------------------------------------------------------------------------------------------------------------
    DNAC_ASSURANCE_RECEIVER                           03/30/26 04:56:20  Connected

  Subscription ID: 502
  Type: Configured
  State: Valid
  Stream: native
  Filter:
    Filter type: tdl-uri
    TDL-URI: /services;serviceName=ios_oper/poe_stack
  Update policy:
    Update Trigger: periodic
    Period: 60000
  Encoding: encode-tdl
  Source VRF:
  Source Address: 10.85.134.70
  Receiver Type: protocol
  Notes: Subscription validated

... (109 more lines truncated)
```

**`show telemetry connection all`**

```
Telemetry connections

Index Peer Address               Port  VRF Source Address             State      State Description
----- -------------------------- ----- --- -------------------------- ---------- --------------------
   23 10.85.134.108              25103 0   10.85.134.70               Active     Connection up
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data"
```

### <a id="22-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-mdt-oper-v2:mdt-oper-v2-data": {
    "mdt-streams": {
      "stream": [
        "native",
        "yang-notif-native",
        "yang-push"
      ]
    },
    "mdt-subscriptions": [
      {
        "subscription-id": 500,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.325373+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 501,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.32664+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 502,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.32774+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 503,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.32866+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 504,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.363586+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 750,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.364815+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 751,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.365767+00:00",
        "mdt-receiver-names": []
      },
      {
        "subscription-id": 8882,
        "base": {},
        "type": "sub-type-static",
        "state": "sub-state-valid",
        "state-explanation": "Subscription validated",
        "last-state-change-time": "2026-03-28T00:39:29.508676+00:00",
        "mdt-receiver-names": []
      }
    ],
    "mdt-named-receivers": [
      {
        "name": "DNAC_ASSURANCE_RECEIVER",
        "profile": "sdn-network-infra-iwan",
        "params": {},
        "state": "named-rcvr-state-valid",
        "last-state-change-time": "2026-03-28T00:39:29.460996+00:00"
      }
    ],
    "mdt-connections": [
      {
        "index": 23,
        "conn-id": {},
        "peer-id": "10.85.134.108:25103:0:10.85.134.70",
  ...
}
```

---

## 23. Software Install

**YANG Module:** `Cisco-IOS-XE-install-oper.yang`
**Telemetry XPath:** `/install-ios-xe-oper:install-oper-data`

### CLI Show Commands

```
show install summary
show version
```

### <a id="23-cli-output"></a>CLI Output

**`show install summary`**

```
[ Switch 1 ] Installed Package(s) Information:
State (St): I - Inactive, U - Activated & Uncommitted,
            C - Activated & Committed, D - Deactivated & Uncommitted
--------------------------------------------------------------------------------
Type  St   Filename/Version
--------------------------------------------------------------------------------
IMG   C    17.18.02.0.4112

--------------------------------------------------------------------------------
Auto abort timer: inactive
--------------------------------------------------------------------------------
```

**`show version`**

```
Cisco IOS XE Software, Version 17.18.02
Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2025 by Cisco Systems, Inc.
Compiled Fri 19-Dec-25 03:36 by mcpre


Cisco IOS-XE software, Copyright (c) 2005-2025 by cisco Systems, Inc.
All rights reserved.  Certain components of Cisco IOS-XE software are
licensed under the GNU General Public License ("GPL") Version 2.0.  The
software code licensed under GPL Version 2.0 is free software that comes
with ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such
GPL code under the terms of GPL Version 2.0.  For more details, see the
documentation or "License Notice" file accompanying the IOS-XE software,
or the applicable URL provided on the flyer accompanying the IOS-XE
software.


ROM: IOS-XE ROMMONBOOTLDR: System Bootstrap, Version 17.15.1r, RELEASE SOFTWARE (P)

JCOHOE-C9300-2 uptime is 2 weeks, 1 day, 22 hours, 25 minutes
Uptime for this control processor is 2 weeks, 1 day, 22 hours, 26 minutes
System returned to ROM by Reload Command at 01:36:02 PDT Sat Mar 28 2026
System image file is "flash:packages.conf"
Last reload reason: Reload Command



This product contains cryptographic features and is subject to United
States and local country laws governing import, export, transfer and
use. Delivery of Cisco cryptographic products does not imply
third-party authority to import, export, distribute or use encryption.
Importers, exporters, distributors and users are responsible for
compliance with U.S. and local country laws. By using this product you
agree to comply with applicable laws and regulations. If you are unable
to comply with U.S. and local laws, return this product immediately.

A summary of U.S. laws governing Cisco cryptographic products may be found at:
http://www.cisco.com/wwl/export/crypto/tool/stqrg.html

If you require further assistance please contact us by sending email to
export@cisco.com.


Technology Package License Information:

------------------------------------------------------------------------------
Technology-package                                     Technology-package
Current                        Type                       Next reboot
------------------------------------------------------------------------------
network-advantage   	Smart License                 	 network-advantage
dna-advantage       	Subscription Smart License    	 dna-advantage


Smart Licensing Status: Smart Licensing Using Policy

cisco C9300-24UX (X86) processor with 1049141K/6147K bytes of memory.
Processor board ID FOC2237U0A1
3 Virtual Ethernet interfaces
4 Gigabit Ethernet interfaces
... (23 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-install-oper:install-oper-data"
```

### <a id="23-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 24. BGP State

**YANG Module:** `Cisco-IOS-XE-bgp-oper.yang`
**Telemetry XPath:** `/bgp-ios-xe-oper:bgp-state-data`

### CLI Show Commands

```
show bgp summary
show bgp all summary
show bgp ipv4 unicast summary
```

### <a id="24-cli-output"></a>CLI Output

**`show bgp summary`**

```
% Command accepted but obsolete, unreleased or unsupported; see documentation.
% BGP not active
```

**`show bgp all summary`**

```
% BGP not active
```

**`show bgp ipv4 unicast summary`**

```
% BGP not active
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-bgp-oper:bgp-state-data"
```

### <a id="24-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-bgp-oper:bgp-state-data": {
    "bgp-route-vrfs": {
      "bgp-route-vrf": []
    },
    "bgp-route-rds": {
      "bgp-route-rd": []
    }
  }
}
```

---

## 25. OSPF State

**YANG Module:** `Cisco-IOS-XE-ospf-oper.yang`
**Telemetry XPath:** `/ospf-ios-xe-oper:ospf-oper-data`

### CLI Show Commands

```
show ip ospf
show ip ospf neighbor
show ip ospf interface brief
```

### <a id="25-cli-output"></a>CLI Output

**`show ip ospf`**

> Feature not active — no output returned.

**`show ip ospf neighbor`**

> Feature not active — no output returned.

**`show ip ospf interface brief`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-ospf-oper:ospf-oper-data"
```

### <a id="25-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-ospf-oper:ospf-oper-data": {
    "ospf-state": {
      "op-mode": "ospf-ships-in-the-night"
    }
  }
}
```

---

## 26. IETF Routing Table (RIB)

**YANG Module:** `ietf-routing.yang`
**Telemetry XPath:** `/ietf-routing:routing-state`

### CLI Show Commands

```
show ip route
show ip route summary
show ipv6 route
```

### <a id="26-cli-output"></a>CLI Output

**`show ip route`**

```
Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2, m - OMP
       n - NAT, Ni - NAT inside, No - NAT outside, Nd - NAT DIA
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       H - NHRP, G - NHRP registered, g - NHRP registration summary
       o - ODR, P - periodic downloaded static route, l - LISP
       a - application route
       + - replicated route, % - next hop override, p - overrides from PfR
       & - replicated local route overrides by connected

Gateway of last resort is 10.85.134.65 to network 0.0.0.0

S*    0.0.0.0/0 [1/0] via 10.85.134.65
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.85.134.64/26 is directly connected, Vlan311
L        10.85.134.70/32 is directly connected, Vlan311
```

**`show ip route summary`**

```
IP routing table name is default (0x0)
IP routing table maximum-paths is 32
Route Source    Networks    Subnets     Replicates  Overhead    Memory (bytes)
static          1           0           0           112         312
connected       0           2           0           224         624
internal        1                                               632
Total           2           2           0           336         1568
```

**`show ipv6 route`**

```
IPv6 Routing Table - default - 1 entries
Codes: C - Connected, L - Local, S - Static, U - Per-user Static route
       B - BGP, R - RIP, H - NHRP, HG - NHRP registered
       Hg - NHRP registration summary, HE - NHRP External, I1 - ISIS L1
       I2 - ISIS L2, IA - ISIS interarea, IS - ISIS summary, D - EIGRP
       EX - EIGRP external, RL - RPL, O - OSPF Intra, OI - OSPF Inter
       OE1 - OSPF ext 1, OE2 - OSPF ext 2, ON1 - OSPF NSSA ext 1
       ON2 - OSPF NSSA ext 2, la - LISP alt, lr - LISP site-registrations
       ld - LISP dyn-eid, lA - LISP away, le - LISP extranet-policy
       lp - LISP publications, ls - LISP destinations-summary
L   FF00::/8 [0/0]
     via Null0, receive
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/ietf-routing:routing-state"
```

### <a id="26-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "ietf-routing:routing-state": {
    "routing-instance": [
      {
        "name": "default",
        "type": "ietf-routing:default-routing-instance",
        "router-id": "0.0.0.0",
        "routing-protocols": {},
        "ribs": {}
      },
      {
        "name": "Mgmt-vrf",
        "type": "ietf-routing:vrf-routing-instance",
        "router-id": "0.0.0.0",
        "interfaces": {},
        "ribs": {}
      },
      {
        "name": "__Platform_iVRF:_ID00_",
        "type": "ietf-routing:vrf-routing-instance",
        "router-id": "0.0.0.0",
        "interfaces": {},
        "routing-protocols": {},
        "ribs": {}
      }
    ]
  }
}
```

---

## 27. DHCP Pool Stats

**YANG Module:** `Cisco-IOS-XE-dhcp-oper.yang`
**Telemetry XPath:** `/dhcp-ios-xe-oper:dhcp-oper-data`

### CLI Show Commands

```
show ip dhcp pool
show ip dhcp binding
show ip dhcp statistics
```

### <a id="27-cli-output"></a>CLI Output

**`show ip dhcp pool`**

> Feature not active — no output returned.

**`show ip dhcp binding`**

```
Bindings from all pools not associated with VRF:
IP address      Client-ID/ 		Lease expiration 	Type       State      Interface
		Hardware address/
		User name
```

**`show ip dhcp statistics`**

```
^
% Invalid input detected at '^' marker.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-dhcp-oper:dhcp-oper-data"
```

### <a id="27-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-dhcp-oper:dhcp-oper-data": {
    "dhcpv6-relay-binding-stats": {
      "bndg-cnt": 0,
      "iana-bndg-cnt": 0,
      "iapd-bndg-cnt": 0,
      "bulk-lq-bndg-cnt": 0
    }
  }
}
```

---

## 28. High Availability State

**YANG Module:** `Cisco-IOS-XE-ha-oper.yang`
**Telemetry XPath:** `/ha-ios-xe-oper:ha-oper-data`

### CLI Show Commands

```
show redundancy
show redundancy states
```

### <a id="28-cli-output"></a>CLI Output

**`show redundancy`**

```
Redundant System Information :
------------------------------
       Available system uptime = 2 weeks, 1 day, 22 hours, 26 minutes
Switchovers system experienced = 0
              Standby failures = 0
        Last switchover reason = none

                 Hardware Mode = Simplex
    Configured Redundancy Mode = sso
     Operating Redundancy Mode = Non-redundant
              Maintenance Mode = Disabled
                Communications = Down      Reason: Failure

Current Processor Information :
-------------------------------
               Active Location = slot 1
        Current Software state = ACTIVE
       Uptime in current state = 2 weeks, 1 day, 22 hours, 26 minutes
                 Image Version = Cisco IOS Software [IOSXE], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.18.2, RELEASE SOFTWARE (fc3)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2025 by Cisco Systems, Inc.
Compiled Fri 19-Dec-25 03:36 by mcpre
                          BOOT = flash:packages.conf;
             Fast Switchover   = Enabled
                Initial Garp   = Enabled

Peer (slot: 0) information is not available because it is in 'DISABLED' state
```

**`show redundancy states`**

```
my state = 13 -ACTIVE
     peer state = 1  -DISABLED
           Mode = Simplex
           Unit = Primary
        Unit ID = 1

Redundancy Mode (Operational) = Non-redundant
Redundancy Mode (Configured)  = sso
Redundancy State              = Non Redundant
     Maintenance Mode = Disabled
    Manual Swact = disabled (system is simplex (no peer unit))
 Communications = Down      Reason: Simplex mode

   client count = 123
 client_notification_TMR = 30000 milliseconds
           RF debug mask = 0x0
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-ha-oper:ha-oper-data"
```

### <a id="28-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-ha-oper:ha-oper-data": {
    "ha-infra": {
      "ha-state": "db-rf-active",
      "peer-state": "db-rf-disabled",
      "last-switchover-time": "1970-01-01T00:00:00+00:00",
      "last-switchover-reason": "none",
      "image-version": "17.18.2",
      "leaf-mode": "SSO",
      "ha-enabled": false,
      "has-switchover-occured": false,
      "switchover-count": 0,
      "standby-failure-count": 0
    }
  }
}
```

---

## 29. Linecard Status

**YANG Module:** `Cisco-IOS-XE-linecard-oper.yang`
**Telemetry XPath:** `/linecard-ios-xe-oper:linecard-oper-data`

### CLI Show Commands

```
show platform
show module
```

### <a id="29-cli-output"></a>CLI Output

**`show platform`**

```
Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver.
------  -----   ---------             -----------  --------------  -------       --------
 1       41     C9300-24UX            FOC2237U0A1  700b.4ff5.c280  V02           17.18.02
Switch/Stack Mac Address : 700b.4ff5.c280 - Local Mac Address
Mac persistency wait time: Indefinite
                                   Current
Switch#   Role        Priority      State
-------------------------------------------
*1       Active          1          Ready
```

**`show module`**

```
Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver.
------  -----   ---------             -----------  --------------  -------       --------
 1       41     C9300-24UX            FOC2237U0A1  700b.4ff5.c280  V02           17.18.02
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-linecard-oper:linecard-oper-data"
```

### <a id="29-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 30. TrustSec (SGT/SXP)

**YANG Module:** `Cisco-IOS-XE-trustsec-oper.yang`
**Telemetry XPath:** `/trustsec-ios-xe-oper:trustsec-state`

### CLI Show Commands

```
show cts environment-data
show cts role-based sgt-map all
show cts sxp connections brief
```

### <a id="30-cli-output"></a>CLI Output

**`show cts environment-data`**

```
CTS Environment Data
====================
Current state = START
Last status = In Progress
Environment data is empty
State Machine is running
Retry_timer (60 secs) is not running
```

**`show cts role-based sgt-map all`**

```
Active IPv4-SGT Bindings Information

IP Address              SGT     Source
============================================
Active IPv6-SGT Bindings Information

IP Address                                  SGT     Source
================================================================
```

**`show cts sxp connections brief`**

```
SXP              : Disabled
 Highest Version Supported: 5
 Default Password : Not Set
 Default Key-Chain: Not Set
 Default Key-Chain Name: Not Applicable
 Default Source IP: Not Set
Connection retry open period: 120 secs
Reconcile period: 120 secs
Retry open timer is not running
Peer-Sequence traverse limit for export: Not Set
Peer-Sequence traverse limit for import: Not Set

There are no SXP Connections.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-trustsec-oper:trustsec-state"
```

### <a id="30-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-trustsec-oper:trustsec-state": {
    "cts-pac": {},
    "cts-env-data": {
      "status": "env-download-in-progress",
      "device-sgt": 0,
      "total-num-servers": 0,
      "life-time": 0,
      "last-updated-time": "1970-01-01T00:00:00+00:00",
      "next-refresh-time": "1970-01-01T00:00:00+00:00"
    }
  }
}
```

---

## 31. LACP / Port-Channel

**YANG Module:** `Cisco-IOS-XE-interfaces-oper.yang`
**Telemetry XPath:** `/interfaces-ios-xe-oper:interfaces/interface/lag-aggregate-state`

### CLI Show Commands

```
show etherchannel summary
show lacp neighbor
show lacp counters
```

### <a id="31-cli-output"></a>CLI Output

**`show etherchannel summary`**

```
Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator

        M - not in use, minimum links not met
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port

        A - formed by Auto LAG


Number of channel-groups in use: 0
Number of aggregators:           0

Group  Port-channel  Protocol    Ports
------+-------------+-----------+-----------------------------------------------
```

**`show lacp neighbor`**

> Feature not active — no output returned.

**`show lacp counters`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-interfaces-oper:interfaces/interface"
```

### <a id="31-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 32. ACL Hit Counters

**YANG Module:** `Cisco-IOS-XE-acl-oper.yang`
**Telemetry XPath:** `/acl-ios-xe-oper:access-lists/access-list`

### CLI Show Commands

```
show access-lists
show ip access-lists
```

### <a id="32-cli-output"></a>CLI Output

**`show access-lists`**

```
Standard IP access list SACL1
    10 deny   10.0.0.0, wildcard bits 0.0.0.255 log
Extended IP access list IP-Adm-V4-Int-ACL-global
    10 permit tcp any any eq www
    20 permit tcp any any eq 443
Extended IP access list a42e11-DEFAULT-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 deny ip any 10.198.70.0 0.0.0.255
    50 deny ip any 10.16.214.0 0.0.0.255
    60 deny ip any 10.16.214.192 0.0.0.15
    70 deny ip any 10.16.214.112 0.0.0.7
    80 deny ip any 10.198.131.0 0.0.0.255
    90 deny ip any 10.22.157.0 0.0.0.255
    100 deny ip any 10.22.209.0 0.0.0.255
    110 deny ip any 10.192.97.0 0.0.0.255
    120 deny ip any 10.198.128.0 0.0.0.255
    130 deny ip any 10.221.20.224 0.0.0.15
    140 deny ip any 1.0.0.0 0.255.255.255
    150 deny ip any 2.0.0.0 0.255.255.255
    160 deny ip any 3.0.0.0 0.255.255.255
    170 permit ip any any
Extended IP access list a42e11-KIVA-Ka42e11-PROXY-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 permit ip any 10.16.214.48 0.0.0.7
    50 permit ip any 10.16.214.0 0.0.0.7
    60 permit ip any 3.0.0.0 0.255.255.255
    70 permit ip any 192.168.0.0 0.0.255.255
    80 deny ip any 10.198.70.0 0.0.0.255
    90 deny ip any 10.16.214.0 0.0.0.255
    100 deny ip any 10.16.214.192 0.0.0.15
    110 deny ip any 10.16.214.112 0.0.0.7
    120 deny ip any 10.198.131.0 0.0.0.255
    130 deny ip any 10.22.157.0 0.0.0.255
    140 deny ip any 10.22.209.0 0.0.0.255
    150 deny ip any 10.192.97.0 0.0.0.255
    160 deny ip any 10.198.128.0 0.0.0.255
    170 deny ip any 10.221.20.224 0.0.0.15
    180 deny ip any 1.0.0.0 0.255.255.255
    190 deny ip any 2.0.0.0 0.255.255.255
    200 permit ip any any
Extended IP access list a42e11-MGMT-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 permit ip any host 10.221.20.228
    50 permit ip any 10.10.214.16 0.0.0.15
    60 permit ip any 10.10.214.96 0.0.0.15
    70 permit ip any 10.10.97.0 0.0.0.255
    80 deny ip any 10.10.70.0 0.0.0.255
    90 deny ip any 10.10.214.0 0.0.0.255
    100 deny ip any 10.10.214.192 0.0.0.15
    110 deny ip any 10.10.214.112 0.0.0.7
    120 deny ip any 10.10.131.0 0.0.0.255
    130 deny ip any 10.10.157.0 0.0.0.255
    140 deny ip any 10.10.209.0 0.0.0.255
    150 deny ip any 10.192.97.0 0.0.0.255
... (83 more lines truncated)
```

**`show ip access-lists`**

```
Standard IP access list SACL1
    10 deny   10.0.0.0, wildcard bits 0.0.0.255 log
Extended IP access list IP-Adm-V4-Int-ACL-global
    10 permit tcp any any eq www
    20 permit tcp any any eq 443
Extended IP access list a42e11-DEFAULT-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 deny ip any 10.198.70.0 0.0.0.255
    50 deny ip any 10.16.214.0 0.0.0.255
    60 deny ip any 10.16.214.192 0.0.0.15
    70 deny ip any 10.16.214.112 0.0.0.7
    80 deny ip any 10.198.131.0 0.0.0.255
    90 deny ip any 10.22.157.0 0.0.0.255
    100 deny ip any 10.22.209.0 0.0.0.255
    110 deny ip any 10.192.97.0 0.0.0.255
    120 deny ip any 10.198.128.0 0.0.0.255
    130 deny ip any 10.221.20.224 0.0.0.15
    140 deny ip any 1.0.0.0 0.255.255.255
    150 deny ip any 2.0.0.0 0.255.255.255
    160 deny ip any 3.0.0.0 0.255.255.255
    170 permit ip any any
Extended IP access list a42e11-KIVA-Ka42e11-PROXY-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 permit ip any 10.16.214.48 0.0.0.7
    50 permit ip any 10.16.214.0 0.0.0.7
    60 permit ip any 3.0.0.0 0.255.255.255
    70 permit ip any 192.168.0.0 0.0.255.255
    80 deny ip any 10.198.70.0 0.0.0.255
    90 deny ip any 10.16.214.0 0.0.0.255
    100 deny ip any 10.16.214.192 0.0.0.15
    110 deny ip any 10.16.214.112 0.0.0.7
    120 deny ip any 10.198.131.0 0.0.0.255
    130 deny ip any 10.22.157.0 0.0.0.255
    140 deny ip any 10.22.209.0 0.0.0.255
    150 deny ip any 10.192.97.0 0.0.0.255
    160 deny ip any 10.198.128.0 0.0.0.255
    170 deny ip any 10.221.20.224 0.0.0.15
    180 deny ip any 1.0.0.0 0.255.255.255
    190 deny ip any 2.0.0.0 0.255.255.255
    200 permit ip any any
Extended IP access list a42e11-MGMT-ACC-IN
    10 permit icmp any any echo
    20 permit icmp any any echo-reply
    30 permit icmp any any unreachable
    40 permit ip any host 10.221.20.228
    50 permit ip any 10.10.214.16 0.0.0.15
    60 permit ip any 10.10.214.96 0.0.0.15
    70 permit ip any 10.10.97.0 0.0.0.255
    80 deny ip any 10.10.70.0 0.0.0.255
    90 deny ip any 10.10.214.0 0.0.0.255
    100 deny ip any 10.10.214.192 0.0.0.15
    110 deny ip any 10.10.214.112 0.0.0.7
    120 deny ip any 10.10.131.0 0.0.0.255
    130 deny ip any 10.10.157.0 0.0.0.255
    140 deny ip any 10.10.209.0 0.0.0.255
    150 deny ip any 10.192.97.0 0.0.0.255
... (65 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-acl-oper:access-lists"
```

### <a id="32-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-acl-oper:access-lists": {
    "access-list": [
      {
        "access-control-list-name": "SACL1",
        "access-list-entries": {},
        "access-control-list-type": "v4-standard-acl",
        "access-control-list-type-flags": ""
      },
      {
        "access-control-list-name": "IP-Adm-V4-Int-ACL-global",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "a42e11-DEFAULT-ACC-IN",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": ""
      },
      {
        "access-control-list-name": "a42e11-KIVA-Ka42e11-PROXY-ACC-IN",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": ""
      },
      {
        "access-control-list-name": "a42e11-MGMT-ACC-IN",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": ""
      },
      {
        "access-control-list-name": "a42e11-USER-ACC-IN",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": ""
      },
      {
        "access-control-list-name": "implicit_deny",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "implicit_permit",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "preauth_v4",
        "access-list-entries": {},
        "access-control-list-type": "v4-extended-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "implicit_deny_v6",
        "access-list-entries": {},
        "access-control-list-type": "v6-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "implicit_permit_v6",
        "access-list-entries": {},
        "access-control-list-type": "v6-acl",
        "access-control-list-type-flags": "internal"
      },
      {
        "access-control-list-name": "preauth_v6",
        "access-list-entries": {},
        "access-control-list-type": "v6-acl",
        "access-control-list-type-flags": "internal"
      }
    ]
  }
}
```

---

## 33. NTP Synchronization

**YANG Module:** `Cisco-IOS-XE-ntp-oper.yang`
**Telemetry XPath:** `/ntp-ios-xe-oper:ntp-oper-data/ntp-status-info`

### CLI Show Commands

```
show ntp status
show ntp associations
show ntp associations detail
```

### <a id="33-cli-output"></a>CLI Output

**`show ntp status`**

```
Clock is unsynchronized, stratum 16, no reference clock
nominal freq is 250.0000 Hz, actual freq is 249.9977 Hz, precision is 2**10
ntp uptime is 137682600 (1/100 of seconds), resolution is 4016
reference time is 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
clock offset is 0.0000 msec, root delay is 0.00 msec
root dispersion is 20652.37 msec, peer dispersion is 0.00 msec
loopfilter state is 'FSET' (Drift set from file), drift is 0.000008992 s/s
system poll interval is 8, never updated.
```

**`show ntp associations`**

```
address         ref clock       st   when   poll reach  delay  offset   disp
 ~10.1.7.2        .TIME.          16      -     64     0  0.000   0.000 15937.
 ~10.11.13.10     .TIME.          16      -     64     0  0.000   0.000 15937.
 * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured
```

**`show ntp associations detail`**

```
10.1.7.2 configured, ipv4, insane, invalid, unsynced, stratum 16
ref ID .TIME., time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
our mode client, peer mode unspec, our poll intvl 64, peer poll intvl 1024
root delay 0.00 msec, root disp 0.00, reach 0, sync dist 15938.38
delay 0.00 msec, offset 0.0000 msec, dispersion 15937.50, jitter 0.00 msec
precision 2**10, version 4
assoc id 48932, assoc name 10.1.7.2
assoc in packets 0, assoc out packets 21020, assoc error packets 0
org time ED86A3C3.60C49CB0 (00:05:39.378 PDT Mon Apr 13 2026)
rec time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
xmt time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
filtdelay =     0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00
filtoffset =    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00
filterror =  16000.0 16000.0 16000.0 16000.0 16000.0 16000.0 16000.0 16000.0
minpoll = 6, maxpoll = 10

10.11.13.10 configured, ipv4, insane, invalid, unsynced, stratum 16
ref ID .TIME., time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
our mode client, peer mode unspec, our poll intvl 64, peer poll intvl 1024
root delay 0.00 msec, root disp 0.00, reach 0, sync dist 15937.66
delay 0.00 msec, offset 0.0000 msec, dispersion 15937.50, jitter 0.00 msec
precision 2**10, version 4
assoc id 48933, assoc name 10.11.13.10
assoc in packets 0, assoc out packets 21026, assoc error packets 0
org time ED86A3F3.610625E8 (00:06:27.379 PDT Mon Apr 13 2026)
rec time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
xmt time 00000000.00000000 (00:00:00.000 UTC Mon Jan 1 1900)
filtdelay =     0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00
filtoffset =    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00
filterror =  16000.0 16000.0 16000.0 16000.0 16000.0 16000.0 16000.0 16000.0
minpoll = 6, maxpoll = 10
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-ntp-oper:ntp-oper-data/ntp-status-info"
```

### <a id="33-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-ntp-oper:ntp-status-info": {
    "refid": {
      "kod-data": {}
    },
    "reftime": "1970-01-01T00:00:00+00:00",
    "sys-poll": 3,
    "stratum": 16,
    "root-delay": "0.0",
    "root-disp": "20629.3",
    "offset": "0.0",
    "ntp-associations": [
      {
        "assoc-id": 48932,
        "peer-reach": 0,
        "peer-stratum": 16,
        "refid": {},
        "reftime": "1970-01-01T00:00:00+00:00",
        "last-poll-time": "0",
        "poll": 6,
        "delay": "0.0",
        "offset": "0.0",
        "jitter": "0.0",
        "ntp-address": {},
        "num-events": 1,
        "last-peer-event": "ntp-peer-event-mobilize",
        "peer-selection-status": "ntp-peer-rejected",
        "peer-authentication-status": "ntp-auth-none",
        "serv-type": "ntp-server",
        "psw-crypto": "crypto-flag-sig"
      },
      {
        "assoc-id": 48933,
        "peer-reach": 0,
        "peer-stratum": 16,
        "refid": {},
        "reftime": "1970-01-01T00:00:00+00:00",
        "last-poll-time": "0",
        "poll": 6,
        "delay": "0.0",
        "offset": "0.0",
        "jitter": "0.0",
        "ntp-address": {},
        "num-events": 1,
        "last-peer-event": "ntp-peer-event-mobilize",
        "peer-selection-status": "ntp-peer-rejected",
        "peer-authentication-status": "ntp-auth-none",
        "serv-type": "ntp-server",
        "psw-crypto": "crypto-flag-sig"
      }
    ],
    "freq-drift-ppm": "0.0"
  }
}
```

---

## 34. BFD Sessions

**YANG Module:** `Cisco-IOS-XE-bfd-oper.yang`
**Telemetry XPath:** `/bfd-ios-xe-oper:bfd-state/sessions`

### CLI Show Commands

```
show bfd neighbors
show bfd neighbors details
```

### <a id="34-cli-output"></a>CLI Output

**`show bfd neighbors`**

> Feature not active — no output returned.

**`show bfd neighbors details`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-bfd-oper:bfd-state/sessions"
```

### <a id="34-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 35. HSRP State

**YANG Module:** `Cisco-IOS-XE-hsrp-oper.yang`
**Telemetry XPath:** `/hsrp-ios-xe-oper:hsrp-oper-data/hsrp-group-info`

### CLI Show Commands

```
show standby
show standby brief
```

### <a id="35-cli-output"></a>CLI Output

**`show standby`**

> Feature not active — no output returned.

**`show standby brief`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-hsrp-oper:hsrp-oper-data/hsrp-group-info"
```

### <a id="35-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 36. VRRP State

**YANG Module:** `Cisco-IOS-XE-vrrp-oper.yang`
**Telemetry XPath:** `/vrrp-ios-xe-oper:vrrp-oper-data/vrrp-oper-state`

### CLI Show Commands

```
show vrrp
show vrrp brief
```

### <a id="36-cli-output"></a>CLI Output

**`show vrrp`**

> Feature not active — no output returned.

**`show vrrp brief`**

```
Interface          Grp Pri Time  Own Pre State   Master addr     Group addr
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-vrrp-oper:vrrp-oper-data/vrrp-oper-state"
```

### <a id="36-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 37. Flexible NetFlow / Flow Monitor

**YANG Module:** `Cisco-IOS-XE-flow-monitor-oper.yang`
**Telemetry XPath:** `/flow-monitor-ios-xe-oper:flow-monitors/flow-monitor`

### CLI Show Commands

```
show flow monitor
show flow monitor statistics
```

### <a id="37-cli-output"></a>CLI Output

**`show flow monitor`**

> Feature not active — no output returned.

**`show flow monitor statistics`**

```
^
% Invalid input detected at '^' marker.
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-flow-monitor-oper:flow-monitors/flow-monitor"
```

### <a id="37-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 38. IP SLA Probes

**YANG Module:** `Cisco-IOS-XE-ip-sla-oper.yang`
**Telemetry XPath:** `/ip-sla-ios-xe-oper:ip-sla-stats/sla-oper-entry`

### CLI Show Commands

```
show ip sla statistics
show ip sla summary
```

### <a id="38-cli-output"></a>CLI Output

**`show ip sla statistics`**

```
IPSLAs Latest Operation Statistics
```

**`show ip sla summary`**

```
IPSLAs Latest Operation Summary
Codes: * active, ^ inactive, ~ pending
All Stats are in milliseconds. Stats with u are in microseconds

ID           Type        Destination       Stats       Return      Last
                                                       Code        Run
-----------------------------------------------------------------------
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-ip-sla-oper:ip-sla-stats/sla-oper-entry"
```

### <a id="38-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 39. AAA / RADIUS / TACACS Statistics

**YANG Module:** `Cisco-IOS-XE-aaa-oper.yang`
**Telemetry XPath:** `/aaa-ios-xe-oper:aaa-data/aaa-radius-stats`

### CLI Show Commands

```
show aaa servers
show radius statistics
```

### <a id="39-cli-output"></a>CLI Output

**`show aaa servers`**

> Feature not active — no output returned.

**`show radius statistics`**

```
Auth.      Acct.       Both
         Maximum inQ length:         NA         NA          0
       Maximum waitQ length:         NA         NA          0
       Maximum doneQ length:         NA         NA          0
       Total responses seen:          0          0          0
     Packets with responses:          0          0          0
  Packets without responses:          0          0          0
  Access Rejects           :          0
  Access Accepts           :          0
 Average response delay(ms):          0          0          0
 Maximum response delay(ms):          0          0          0
  Number of Radius timeouts:          0          0          0
      Radius Timers Started:          0          0          0
      Radius Timers Created:          0          0          0
Radius Timers Create Failed:          0          0          0
      Radius Timers Stopped:          0          0          0
  Radius Timers Stop Failed:          0          0          0
  Radius Timers Outstanding:          0          0          0
        Radius Timers Added:          0          0          0
   Radius Timers Add Failed:          0          0          0
    Radius Timers Jitterred:          0          0          0
Radius Timers Jitter Failed:          0          0          0
       Duplicate ID detects:          0          0          0
 Buffer Allocation Failures:          0          0          0
Maximum Buffer Size (bytes):          0          0          0
Malformed Responses        :          0          0          0
Bad Authenticators         :          0          0          0
Unknown Responses          :          0          0          0
 Source Port Range: (2 ports only)
 1645 - 1646
 Last used Source Port/Identifier:
 1645/0
 1646/0

  Elapsed time since counters last cleared: 2w1d22h28m
Radius Latency Distribution:
<= 2ms :          0          0
3-5ms  :          0          0
5-10ms :          0          0
10-20ms:          0          0
20-50ms:          0          0
50-100m:          0          0
>100ms :          0          0

Current inQ length  : 0
Current doneQ length: 0
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-aaa-oper:aaa-data/aaa-radius-stats"
```

### <a id="39-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 40. Port Security

**YANG Module:** `Cisco-IOS-XE-psecure-oper.yang`
**Telemetry XPath:** `/psecure-ios-xe-oper:psecure-oper-data/psecure-state`

### CLI Show Commands

```
show port-security
show port-security address
```

### <a id="40-cli-output"></a>CLI Output

**`show port-security`**

```
Secure Port  MaxSecureAddr  CurrentAddr  SecurityViolation  Security Action
                (Count)       (Count)          (Count)
---------------------------------------------------------------------------
---------------------------------------------------------------------------
Total Addresses in System (excluding one mac per port)     : 0
Max Addresses limit in System (excluding one mac per port) : 4096
```

**`show port-security address`**

```
Secure Mac Address Table
-------------------------------------------------------------------------------
Vlan    Mac Address       Type                          Ports   Remaining Age
                                                                   (mins)
----    -----------       ----                          -----   -------------
-------------------------------------------------------------------------------
Total Addresses in System (excluding one mac per port)     : 0
Max Addresses limit in System (excluding one mac per port) : 4096
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-psecure-oper:psecure-oper-data/psecure-state"
```

### <a id="40-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 41. MACsec / MKA Encryption

**YANG Module:** `Cisco-IOS-XE-macsec-oper.yang + Cisco-IOS-XE-mka-oper.yang`
**Telemetry XPath:** `/macsec-ios-xe-oper:macsec-oper-data/macsec-statistics`

### CLI Show Commands

```
show macsec summary
show macsec interface
show mka sessions
show mka statistics
```

### <a id="41-cli-output"></a>CLI Output

**`show macsec summary`**

```
%No Secure Channels
```

**`show macsec interface`**

```
% Incomplete command.
```

**`show mka sessions`**

```
Total MKA Sessions....... 0
      Secured Sessions... 0
      Pending Sessions... 0

====================================================================================================
Interface       Local-TxSCI          Policy-Name       Inherited          Key-Server
Port-ID         Peer-RxSCI           MACsec-Peers      Status             CKN
====================================================================================================
```

**`show mka statistics`**

```
MKA Global Statistics
=====================
MKA Session Totals
   Secured.................... 0
   Fallback Secured........... 0
   Reauthentication Attempts.. 0

   Deleted (Secured).......... 0
   Keepalive Timeouts......... 0

CA Statistics
   Pairwise CAKs Derived...... 0
   Pairwise CAK Rekeys........ 0
   Group CAKs Generated....... 0
   Group CAKs Received........ 0

SA Statistics
   SAKs Generated.............. 0
   SAKs Rekeyed................ 0
   SAKs Received............... 0
   SAK Responses Received...... 0
   SAK Rekeyed as KN Mismatch.. 0

MKPDU Statistics
   MKPDUs Validated & Rx...... 0
      "Distributed SAK"..... 0
      "Distributed CAK"..... 0
   MKPDUs Transmitted......... 0
      "Distributed SAK"..... 0
      "Distributed CAK"..... 0

MKA Error Counter Totals
========================
Session Failures
   Bring-up Failures................ 0
   Reauthentication Failures........ 0
   Duplicate Auth-Mgr Handle........ 0

SAK Failures
   SAK Generation................... 0
   Hash Key Generation.............. 0
   SAK Encryption/Wrap.............. 0
   SAK Decryption/Unwrap............ 0
   SAK Cipher Mismatch.............. 0

CA Failures
   Group CAK Generation............. 0
   Group CAK Encryption/Wrap........ 0
   Group CAK Decryption/Unwrap...... 0
   Pairwise CAK Derivation.......... 0
   CKN Derivation................... 0
   ICK Derivation................... 0
   KEK Derivation................... 0
   Invalid Peer MACsec Capability... 0

MACsec Failures
   Rx SC Creation................... 0
   Tx SC Creation................... 0
   Rx SA Installation............... 0
   Tx SA Installation............... 0
... (11 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-macsec-oper:macsec-oper-data/macsec-statistics"
```

### <a id="41-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-macsec-oper:macsec-statistics": [
    {
      "if-name": "AppGigabitEthernet1/0/1",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "FortyGigabitEthernet1/1/1",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "FortyGigabitEthernet1/1/2",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "GigabitEthernet0/0",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "GigabitEthernet1/1/1",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "GigabitEthernet1/1/2",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "GigabitEthernet1/1/3",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "GigabitEthernet1/1/4",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/1",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/10",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/11",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/12",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/13",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/14",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
      "rx-badtag-pkts": "0",
      "rx-unknownsci-pkts": "0",
      "rx-nosci-pkts": "0"
    },
    {
      "if-name": "TenGigabitEthernet1/0/15",
      "tx-untag-pkts": "0",
      "rx-notag-pkts": "0",
  ...
}
```

---

## 42. VRF Operational State

**YANG Module:** `Cisco-IOS-XE-vrf-oper.yang`
**Telemetry XPath:** `/vrf-ios-xe-oper:vrf-oper-data/vrf-entry`

### CLI Show Commands

```
show vrf
show ip vrf detail
```

### <a id="42-cli-output"></a>CLI Output

**`show vrf`**

```
Name                             Default RD            Protocols   Interfaces
  Mgmt-vrf                         <not set>             ipv4,ipv6   Gi0/0

  Platform iVRF Name               iVRF Id               Interfaces
  __Platform_iVRF:_ID00_           0                     LI18/2
```

**`show ip vrf detail`**

```
VRF Mgmt-vrf (VRF Id = 1); default RD <not set>; default VPNID <not set>
  New CLI format, supports multiple address-families
  Flags: 0x1808
  Interfaces:
    Gi0/0
Address family ipv4 unicast (Table ID = 0x1):
  Flags: 0x0
  No Export VPN route-target communities
  No Import VPN route-target communities
  No import route-map
  No global export route-map
  No export route-map
  VRF label distribution protocol: not configured
  VRF label allocation mode: per-prefix

VRF __Platform_iVRF:_ID00_ (VRF Id = 266); default RD <not set>; default VPNID <not set>
  Old CLI format, supports IPv4 only
  Flags: 0x8
  Interfaces:
    LI18/2
Address family ipv4 unicast (Table ID = 0x10A):
  Flags: 0x0
  No Export VPN route-target communities
  No Import VPN route-target communities
  No import route-map
  No global export route-map
  No export route-map
  VRF label distribution protocol: not configured
  VRF label allocation mode: per-prefix
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-vrf-oper:vrf-oper-data"
```

### <a id="42-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-vrf-oper:vrf-oper-data": {
    "vrf-entry": [
      {
        "vrf-name": "Mgmt-vrf",
        "interface": [
          "GigabitEthernet0/0"
        ],
        "address-family-entry": []
      }
    ]
  }
}
```

---

## 43. Data Plane Resources (TCAM/EM per Feature)

**YANG Module:** `Cisco-IOS-XE-switch-dp-resources-oper.yang`
**Telemetry XPath:** `/dp-resources-oper:switch-dp-resources-oper-data/location/dp-feature-resource`

### CLI Show Commands

```
show platform hardware fed switch active fwd-asic resource tcam utilization
show platform hardware fed switch active fwd-asic resource utilization
```

### <a id="43-cli-output"></a>CLI Output

**`show platform hardware fed switch active fwd-asic resource tcam utilization`**

```
Codes: EM - Exact_Match, I - Input, O - Output, IO - Input & Output, NA - Not Applicable

CAM Utilization for ASIC  [0]
 Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
 ------------------------------------------------------------------------------------------------------
 Mac Address Table      EM           I       32768       54    0.16%        0        0        0       54
 Mac Address Table      TCAM         I        1024       22    2.15%        0        0        0       22
 L3 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L3 Multicast           TCAM         I         512        9    1.76%        3        6        0        0
 L2 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L2 Multicast           TCAM         I         512       11    2.15%        3        8        0        0
 IP Route Table         EM           I       24576       11    0.04%       10        0        1        0
 IP Route Table         TCAM         I        8192       20    0.24%        7       10        2        1
 QOS ACL                TCAM         IO       5120       85    1.66%       28       38        0       19
                        TCAM         I                   45    0.88%       15       20        0       10
                        TCAM         O                   40    0.78%       13       18        0        9
 Security ACL           TCAM         IO       5120      149    2.91%       26       78        0       45
                        TCAM         I                  106    2.07%       12       54        0       40
                        TCAM         O                   43    0.84%       14       24        0        5
 Netflow ACL            TCAM         I         256        6    2.34%        2        2        0        2
 PBR ACL                TCAM         I        1024       36    3.52%       30        6        0        0
 Netflow ACL            TCAM         O         768        6    0.78%        2        2        0        2
 Flow SPAN ACL          TCAM         IO       1024       13    1.27%        3        6        0        4
                        TCAM         I                    5    0.49%        1        2        0        2
                        TCAM         O                    8    0.78%        2        4        0        2
 Control Plane          TCAM         I         512      290   56.64%      138      106        0       46
 Tunnel Termination     TCAM         I         512       20    3.91%        8       12        0        0
 Lisp Inst Mapping      TCAM         I        2048        1    0.05%        0        0        0        1
 Security Association   TCAM         I         256        4    1.56%        2        2        0        0
 CTS Cell Matrix/VPN
 Label                  EM           O        8192        0    0.00%        0        0        0        0
 CTS Cell Matrix/VPN
 Label                  TCAM         O         512        1    0.20%        0        0        0        1
 Client Table           EM           I        4096        0    0.00%        0        0        0        0
 Client Table           TCAM         I         256        0    0.00%        0        0        0        0
 Input Group LE         TCAM         I        1024        0    0.00%        0        0        0        0
 Output Group LE        TCAM         O        1024        0    0.00%        0        0        0        0
 Macsec SPD             TCAM         I         256        2    0.78%        0        0        0        2
CAM Utilization for ASIC  [1]
 Table                  Subtype      Dir      Max     Used    %Used       V4       V6     MPLS    Other
 ------------------------------------------------------------------------------------------------------
 Mac Address Table      EM           I       32768       54    0.16%        0        0        0       54
 Mac Address Table      TCAM         I        1024       22    2.15%        0        0        0       22
 L3 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L3 Multicast           TCAM         I         512        9    1.76%        3        6        0        0
 L2 Multicast           EM           I        8192        0    0.00%        0        0        0        0
 L2 Multicast           TCAM         I         512       11    2.15%        3        8        0        0
 IP Route Table         EM           I       24576       11    0.04%       10        0        1        0
 IP Route Table         TCAM         I        8192       20    0.24%        7       10        2        1
 QOS ACL                TCAM         IO       5120       81    1.58%       27       36        0       18
                        TCAM         I                   45    0.88%       15       20        0       10
                        TCAM         O                   36    0.70%       12       16        0        8
 Security ACL           TCAM         IO       5120      149    2.91%       26       78        0       45
                        TCAM         I                  106    2.07%       12       54        0       40
                        TCAM         O                   43    0.84%       14       24        0        5
 Netflow ACL            TCAM         I         256        6    2.34%        2        2        0        2
 PBR ACL                TCAM         I        1024       36    3.52%       30        6        0        0
 Netflow ACL            TCAM         O         768        6    0.78%        2        2        0        2
 Flow SPAN ACL          TCAM         IO       1024       13    1.27%        3        6        0        4
                        TCAM         I                    5    0.49%        1        2        0        2
... (14 more lines truncated)
```

**`show platform hardware fed switch active fwd-asic resource utilization`**

```
Resource Info for ASIC Instance: 0
Resource Name           Allocated     Free
------------------------------------------
RSC_DI                      44       41630
RSC_FAST_DI                  0         192
RSC_RIET_0                   1        1364
RSC_RIET_1                   0           2
RSC_RIET_2                   0        1365
RSC_RIET_3                   0        1365
RSC_RIET_4                   0           2
RSC_RIET_5                   0           2
RSC_RIET_6                   0           2
RSC_RIET_7                   0           2
RSC_VLAN_LE                  5        4087
RSC_L3IF_LE                  3        4020
RIM_RSC_DGT                  1        4095
RSC_VPN_PREFIX_ID            1        8192
RSC_LABEL_STACK_ID           1       65536
RSC_RI                       9       57311
RSC_LI_RI                    0         129
RSC_PORT_LE_RI               0        2048
RSC_PORT_LE                  0        1772
RSC_RI_REP                  10       49143
RSC_VPN_SPOKE_ID             1         255
RSC_SI                     541       64829
RSC_SI_IND                   1         255
RSC_SI_STATS               513       48639
RSC_RCP1_FID                 1        1023
RSC_RCP2_FID                 1        1023
RSC_RCP3_FID                 1        1023
RSC_RCP4_FID                 1        1023
RSC_LV1_ECR                  1          63
RSC_LV2_ECR                  1         255
RSC_ENH_ECR                  1           0
RSC_RPF_MATCH                1         255
RSC_PLC                      1        2047
RSC_PLC_PF                   1         255
RSC_MTU_INDEX                6         250
RSC_EGR_REDIRECT_INDEX       2        2046
RSC_RIL_INDEX                1       32767
RSC_SIF                      2        1022
RSC_GROUP_LE                 1        1023
RSC_RI_REP_LOCAL             1           0
RSC_EXT_SI                   1           0
RSC_ENH_ECR_0                1           0
RSC_ENH_ECR_1                1           0
RSC_ENH_ECR_2                1           0

Resource Info for ASIC Instance: 1
Resource Name           Allocated     Free
------------------------------------------
RSC_DI                      44       41630
RSC_FAST_DI                  0         192
RSC_RIET_0                   1        1364
RSC_RIET_1                   0           2
RSC_RIET_2                   0        1365
RSC_RIET_3                   0        1365
RSC_RIET_4                   0           2
RSC_RIET_5                   0           2
RSC_RIET_6                   0           2
... (131 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-switch-dp-resources-oper:switch-dp-resources-oper-data"
```

### <a id="43-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-switch-dp-resources-oper:switch-dp-resources-oper-data": {
    "location": [
      {
        "fru": "fru-fp",
        "slot": 0,
        "bay": 0,
        "chassis": 1,
        "node": 0,
        "dp-feature-resource": []
      }
    ]
  }
}
```

---

## 44. CPU Punt/Inject Counters

**YANG Module:** `Cisco-IOS-XE-switch-dp-punt-inject-oper.yang`
**Telemetry XPath:** `/switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data/location/punt-inject-cpuq-brief-stats`

### CLI Show Commands

```
show platform hardware fed switch active qos queue stats internal cpu policer
show platform software fed switch active punt cpuq all
```

### <a id="44-cli-output"></a>CLI Output

**`show platform hardware fed switch active qos queue stats internal cpu policer`**

```
CPU Queue Statistics
============================================================================================
                                              (default) (set)     Queue        Queue
QId PlcIdx  Queue Name                Enabled   Rate     Rate      Drop(Bytes)  Drop(Frames)
--------------------------------------------------------------------------------------------
0    11     DOT1X Auth                  Yes     1000      1000     0            0
1    1      L2 Control                  Yes     2000      2000     0            0
2    21     Forus traffic               Yes     1000      5000     0            0
3    20     ICMP GEN                    Yes     600       600      0            0
4    2      Routing Control             Yes     5400      5400     0            0
5    14     Forus Address resolution    Yes     3000      3000     0            0
6    0      ICMP Redirect               Yes     600       600      130752       2043
7    16     Inter FED Traffic           Yes     2000      2000     0            0
8    4      L2 LVX Cont Pack            Yes     1000      1000     0            0
9    19     EWLC Control                Yes     13000     13000    0            0
10   16     EWLC Data                   Yes     2000      2000     0            0
11   13     L2 LVX Data Pack            Yes     1000      1000     0            0
12   0      BROADCAST                   Yes     600       600      382317       2280
13   10     Openflow                    Yes     200       200      0            0
14   13     Sw forwarding               Yes     1000      1000     0            0
15   8      Topology Control            Yes     13000     13000    0            0
16   12     Proto Snooping              Yes     2000      2000     0            0
17   6      DHCP Snooping               Yes     400       400      0            0
18   13     Transit Traffic             Yes     1000      1000     0            0
19   10     RPF Failed                  Yes     200       200      0            0
20   15     MCAST END STATION           Yes     2000      2000     0            0
21   13     LOGGING                     Yes     1000      1000     0            0
22   7      Punt Webauth                Yes     1000      1000     0            0
23   18     High Rate App               Yes     13000     13000    0            0
24   10     Exception                   Yes     200       200      0            0
25   3      System Critical             Yes     1000      1000     0            0
26   10     NFL SAMPLED DATA            Yes     200       200      0            0
27   2      Low Latency                 Yes     5400      5400     0            0
28   10     EGR Exception               Yes     200       200      0            0
29   5      Stackwise Virtual OOB       Yes     8000      8000     0            0
30   9      MCAST Data                  Yes     400       400      0            0
31   3      Gold Pkt                    Yes     1000      1000     0            0

* NOTE: CPU queue policer rates are configured to the closest hardware supported value

                      CPU Queue Policer Statistics
====================================================================
Policer    Policer Accept   Policer Accept  Policer Drop  Policer Drop
  Index         Bytes          Frames        Bytes          Frames
-------------------------------------------------------------------
0          10814710         46200           513069        4323
1          139790486        474272          0             0
2          2208             25              0             0
3          0                0               0             0
4          0                0               0             0
5          0                0               0             0
6          15909331         45367           0             0
7          0                0               0             0
8          405731372        5853324         0             0
9          0                0               0             0
10         0                0               0             0
11         0                0               0             0
12         956099619        12550361        0             0
13         74               1               0             0
14         128              2               0             0
... (87 more lines truncated)
```

**`show platform software fed switch active punt cpuq all`**

```
Punt CPU Q Statistics
===========================================

CPU Q Id                       : 0
CPU Q Name                     : CPU_Q_DOT1X_AUTH
Packets received from ASIC     : 0
Send to IOSd total attempts    : 0
Send to IOSd failed count      : 0
RX suspend count               : 0
RX unsuspend count             : 0
RX unsuspend send count        : 0
RX unsuspend send failed count : 0
RX consumed count              : 0
RX dropped count               : 0
RX non-active dropped count    : 0
RX conversion failure dropped  : 0
RX INTACK count                : 0
RX packets dq'd after intack   : 0
Active RxQ event               : 0
RX spurious interrupt          : 0
RX phy_idb fetch failed: 0
RX table_id fetch failed: 0
RX invalid punt cause: 0

CPU Q Id                       : 1
CPU Q Name                     : CPU_Q_L2_CONTROL
Packets received from ASIC     : 498129
Send to IOSd total attempts    : 498129
Send to IOSd failed count      : 0
RX suspend count               : 0
RX unsuspend count             : 0
RX unsuspend send count        : 0
RX unsuspend send failed count : 0
RX consumed count              : 0
RX dropped count               : 0
RX non-active dropped count    : 0
RX conversion failure dropped  : 0
RX INTACK count                : 498122
RX packets dq'd after intack   : 22
Active RxQ event               : 498122
RX spurious interrupt          : 43
RX phy_idb fetch failed: 0
RX table_id fetch failed: 0
RX invalid punt cause: 0

CPU Q Id                       : 2
CPU Q Name                     : CPU_Q_FORUS_TRAFFIC
Packets received from ASIC     : 761068
Send to IOSd total attempts    : 761068
Send to IOSd failed count      : 0
RX suspend count               : 0
RX unsuspend count             : 0
RX unsuspend send count        : 0
RX unsuspend send failed count : 0
RX consumed count              : 0
RX dropped count               : 0
RX non-active dropped count    : 0
RX conversion failure dropped  : 0
RX INTACK count                : 722485
RX packets dq'd after intack   : 26385
... (621 more lines truncated)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data"
```

### <a id="44-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-switch-dp-punt-inject-oper:switch-dp-punt-inject-oper-data": {
    "location": [
      {
        "fru": "fru-fp",
        "slot": 0,
        "bay": 0,
        "chassis": 1,
        "node": 0,
        "punt-inject-cpuq-brief-stats": []
      }
    ]
  }
}
```

---

## 45. PoE Health (Detailed Port-Level)

**YANG Module:** `Cisco-IOS-XE-poe-health-oper.yang`
**Telemetry XPath:** `/poe-health-oper:poe-health-oper-data/location/poe-port/port-health`

### CLI Show Commands

```
show power inline
```

### <a id="45-cli-output"></a>CLI Output

**`show power inline`**

```
Module   Available     Used     Remaining
          (Watts)     (Watts)    (Watts)
------   ---------   --------   ---------
1           595.0       71.6       523.4
Interface Admin  Oper       Power   Device              Class Max
                            (Watts)
--------- ------ ---------- ------- ------------------- ----- ----
Te1/0/1   auto   off        0.0     n/a                 n/a   60.0
Te1/0/2   auto   off        0.0     n/a                 n/a   60.0
Te1/0/3   auto   off        0.0     n/a                 n/a   60.0
Te1/0/4   auto   off        0.0     n/a                 n/a   60.0
Te1/0/5   auto   off        0.0     n/a                 n/a   60.0
Te1/0/6   auto   off        0.0     n/a                 n/a   60.0
Te1/0/7   auto   off        0.0     n/a                 n/a   60.0
Te1/0/8   auto   off        0.0     n/a                 n/a   60.0
Te1/0/9   auto   off        0.0     n/a                 n/a   60.0
Te1/0/10  auto   off        0.0     n/a                 n/a   60.0
Te1/0/11  auto   off        0.0     n/a                 n/a   60.0
Te1/0/12  auto   off        0.0     n/a                 n/a   60.0
Te1/0/13  auto   off        0.0     n/a                 n/a   60.0
Te1/0/14  auto   on         30.0    CW9166I-A           4     60.0
Te1/0/15  auto   off        0.0     n/a                 n/a   60.0
Te1/0/16  auto   on         41.6    C9136I-A            4     60.0
Te1/0/17  auto   off        0.0     n/a                 n/a   60.0
Te1/0/18  auto   off        0.0     n/a                 n/a   60.0
Te1/0/19  auto   off        0.0     n/a                 n/a   60.0
Te1/0/20  auto   off        0.0     n/a                 n/a   60.0
Te1/0/21  auto   off        0.0     n/a                 n/a   60.0
Te1/0/22  auto   off        0.0     n/a                 n/a   60.0
Te1/0/23  auto   off        0.0     n/a                 n/a   60.0
Te1/0/24  auto   off        0.0     n/a                 n/a   60.0
--------- ------ ---------- ---------- ---------- ------ -----
Totals:          2    on    71.6
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-poe-health-oper:poe-health-oper-data"
```

### <a id="45-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 46. CEF / FIB State

**YANG Module:** `Cisco-IOS-XE-fib-oper.yang`
**Telemetry XPath:** `/fib-ios-xe-oper:fib-oper-data`

### CLI Show Commands

```
show ip cef summary
show ip cef
show adjacency summary
```

### <a id="46-cli-output"></a>CLI Output

**`show ip cef summary`**

```
IPv4 CEF is enabled for distributed and running
VRF Default
 17 prefixes (17/0 fwd/non-fwd)
 Table id 0x0
 Database epoch:        3 (17 entries at this epoch)
```

**`show ip cef`**

```
Prefix               Next Hop             Interface
0.0.0.0/0            10.85.134.65         Vlan311
0.0.0.0/8            drop
0.0.0.0/32           receive
10.85.134.64/26      attached             Vlan311
10.85.134.64/32      receive              Vlan311
10.85.134.65/32      attached             Vlan311
10.85.134.70/32      receive              Vlan311
10.85.134.103/32     attached             Vlan311
10.85.134.108/32     attached             Vlan311
10.85.134.117/32     attached             Vlan311
10.85.134.126/32     attached             Vlan311
10.85.134.127/32     receive              Vlan311
127.0.0.0/8          drop
224.0.0.0/4          drop
224.0.0.0/24         receive
240.0.0.0/4          drop
255.255.255.255/32   receive
```

**`show adjacency summary`**

```
Adjacency table has 6 adjacencies:
  each adjacency consumes 548 bytes (72 bytes platform extension)
  6 complete adjacencies
  0 incomplete adjacencies
  6 adjacencies of linktype IP
    6 complete adjacencies of linktype IP
    0 incomplete adjacencies of linktype IP
    0 adjacencies with fixups of linktype IP
    6 adjacencies with IP redirect of linktype IP
    0 adjacencies post encap punt capable of linktype IP

Adjacency database high availability:
  Database epoch:        0 (6 entries at this epoch)

RP adjacency component enabled
Adjacency manager summary event processing:
 Summary events epoch is 0
 Summary events queue contains 0 events (high water mark 2 events)
```

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-fib-oper:fib-oper-data"
```

### <a id="46-restconf-output"></a>Sample Output (RESTCONF)

```json
{
  "Cisco-IOS-XE-fib-oper:fib-oper-data": {
    "fib-ni-entry": [
      {
        "instance-name": "IPv4:Default",
        "af": "fib-addr-fam-ipv4",
        "num-pfx": 17,
        "num-pfx-fwd": 17,
        "num-pfx-non-fwd": 0,
        "fib-entries": []
      },
      {
        "instance-name": "IPv4:Mgmt-vrf",
        "af": "fib-addr-fam-ipv4",
        "num-pfx": 8,
        "num-pfx-fwd": 8,
        "num-pfx-non-fwd": 0,
        "fib-entries": []
      },
      {
        "instance-name": "IPv6:Default",
        "af": "fib-addr-fam-ipv6",
        "num-pfx": 5,
        "num-pfx-fwd": 5,
        "num-pfx-non-fwd": 0,
        "fib-entries": []
      },
      {
        "instance-name": "IPv6:Mgmt-vrf",
        "af": "fib-addr-fam-ipv6",
        "num-pfx": 5,
        "num-pfx-fwd": 5,
        "num-pfx-non-fwd": 0,
        "fib-entries": []
      }
    ],
    "adjacency-table": {
      "num-adjacencies": 6,
      "num-complete-adjacencies": 6,
      "num-incomplete-adjacencies": 0,
      "adjacency-entry": []
    },
    "cef-state": {
      "fib": {},
      "capability": {}
    },
    "cef-statistics": {
      "ipv4-lisp": {},
      "ipv6-lisp": {},
      "ipv4-switching": [],
      "ipv6-switching": [],
      "ipv4-swi-input-feat": [],
      "ipv4-swi-output-feat": [],
      "ipv4-swi-post-encap-feat": [],
      "ipv4-swi-for-us-feat": [],
      "ipv4-swi-punt-feat": [],
      "ipv4-swi-local-feat": [],
      "ipv6-swi-input-feat": [],
      "ipv6-swi-output-feat": [],
      "ipv6-swi-post-encap-feat": [],
      "ipv6-swi-for-us-feat": [],
      "ipv6-swi-punt-feat": []
    },
    "cef-interface": [
      {
        "if-name": "GigabitEthernet0/0",
        "if-number": 6,
        "if-up": false,
        "hwidb-fast-if-num": 6,
        "hwidb-firstsw-if-num": 6,
        "ip-states": {},
        "bgp-states": {},
        "if-index": 5,
        "ip-mtu": 0,
        "slot-unit": 0,
        "slot-vc": -1
      },
      {
        "if-name": "Null0",
        "if-number": 1,
        "if-up": true,
        "hwidb-fast-if-num": 1,
        "hwidb-firstsw-if-num": 1,
        "ip-states": {},
        "ipv6-sub-block": [
          null
        ],
        "ipv6-states": {},
        "bgp-states": {},
        "if-index": 65534,
        "ip-mtu": 1500,
        "slot-unit": 4294967295,
        "slot-vc": -1
      },
      {
        "if-name": "TenGigabitEthernet1/0/1",
        "if-number": 9,
        "if-up": true,
        "hwidb-fast-if-num": 9,
        "hwidb-firstsw-if-num": 9,
        "ip-states": {},
        "bgp-states": {},
        "if-index": 8,
        "ip-mtu": 0,
        "slot-unit": 1,
        "slot-vc": -1
      },
      {
        "if-name": "TenGigabitEthernet1/0/2",
        "if-number": 10,
        "if-up": true,
        "hwidb-fast-if-num": 10,
        "hwidb-firstsw-if-num": 10,
        "ip-states": {},
        "bgp-states": {},
        "if-index": 9,
        "ip-mtu": 0,
        "slot-unit": 2,
        "slot-vc": -1
      },
      {
  ...
}
```

---

## 47. EIGRP Routing

**YANG Module:** `Cisco-IOS-XE-eigrp-oper.yang`
**Telemetry XPath:** `/eigrp-ios-xe-oper:eigrp-oper-data/eigrp-instance`

### CLI Show Commands

```
show ip eigrp neighbors
show ip eigrp topology
```

### <a id="47-cli-output"></a>CLI Output

**`show ip eigrp neighbors`**

> Feature not active — no output returned.

**`show ip eigrp topology`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-eigrp-oper:eigrp-oper-data/eigrp-instance"
```

### <a id="47-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---

## 48. IS-IS Routing

**YANG Module:** `Cisco-IOS-XE-isis-oper.yang`
**Telemetry XPath:** `/isis-ios-xe-oper:isis-oper-data/isis-instance`

### CLI Show Commands

```
show isis neighbors
show isis database
```

### <a id="48-cli-output"></a>CLI Output

**`show isis neighbors`**

> Feature not active — no output returned.

**`show isis database`**

> Feature not active — no output returned.

---

### RESTCONF GET

```bash
curl -sk -u admin:PASS -H "Accept: application/yang-data+json" \
  "https://jcohoe-c9300-2.cisco.com/restconf/data/Cisco-IOS-XE-isis-oper:isis-oper-data/isis-instance"
```

### <a id="48-restconf-output"></a>Sample Output

> Feature not active on this device — returns HTTP 204 (empty).

---
