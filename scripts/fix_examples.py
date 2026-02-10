"""
Fix generic/placeholder example values in event notification specs.

Replaces 'example-string', 'example-value', 'example-name', etc.
with realistic, context-aware values derived from the leaf name,
YANG type, MIB column semantics, and module context.

Usage:
    python scripts/fix_examples.py              # dry-run
    python scripts/fix_examples.py --apply      # apply changes
"""
import json
import os
import re
import sys
import copy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVENTS_DIR = os.path.join(BASE, 'swagger-events-model', 'api')
TREES_DIR = os.path.join(BASE, 'yang-trees')
DRY_RUN = '--apply' not in sys.argv

# ──────────────────────────────────────────────────────────────
# Generic values that need replacement
# ──────────────────────────────────────────────────────────────
GENERIC_VALUES = {
    'example-string', 'example-value', 'value', 'value-1',
    'example-name', 'bit0', 'configuration-change',
}

# ──────────────────────────────────────────────────────────────
# Comprehensive leaf-name → realistic example value mapping
# Organized by semantic domain for clarity
# ──────────────────────────────────────────────────────────────
LEAF_EXAMPLES = {
    # ── Network / IP ──
    'ip-address': '10.1.1.1',
    'ipv4-address': '10.1.1.1',
    'ipv6-address': '2001:db8::1',
    'system-ip': '10.1.1.1',
    'address': '10.1.1.1',
    'mask': '255.255.255.0',
    'prefix': '10.1.1.0/24',
    'prefix-length': 24,
    'subnet': '10.1.1.0',
    'nexthop': '10.1.1.254',
    'next-hop': '10.1.1.254',
    'gateway': '10.1.1.1',
    'peer-address': '10.1.1.2',
    'remote-address': '10.1.1.2',
    'local-address': '10.1.1.1',
    'source-address': '10.1.1.1',
    'destination-address': '10.2.2.2',
    'mac-address': '00:1a:2b:3c:4d:5e',
    'client-mac': 'aa:bb:cc:dd:ee:01',
    'wtp-mac': 'aa:bb:cc:dd:ee:02',
    'rogue-mac-address': 'de:ad:be:ef:ca:fe',
    'vlan-id': 100,
    'vlan': 100,
    'vnid': 5000,
    'client-vnid': 5000,
    'client-sgt': 15,

    # ── Interface / Port ──
    'if-name': 'GigabitEthernet1/0/1',
    'interface': 'GigabitEthernet1/0/1',
    'if-index': 1,
    'ifindex': 1,
    'slot-id': 0,
    'ms-ap-slot-id': 0,
    'port': 830,
    'port-number': 443,
    'channel': 36,

    # ── Device Identity ──
    'host-name': 'Switch-01.example.com',
    'hostname': 'Switch-01.example.com',
    'system-name': 'Switch-01',
    'router-id': '1.1.1.1',
    'name': 'policy-map-1',
    'description': 'Interface to WAN core',
    'detail': 'Notification detail information',
    'tag': 'monitoring-sla-1',
    'label': 'primary-uplink',
    'comments': 'Managed license',

    # ── State / Severity ──
    'severity': 'major',
    'severity-level': 'major',
    'state': 'up',
    'status': 'active',
    'oper-status': 'up',
    'admin-status': 'up',
    'mode': 'active',
    'reason': 'link-flap-detected',
    'message': 'Configuration change completed successfully',
    'event-type': 'state-change',
    'type': 'notify',
    'result': 'success',
    'auth-result': 'success',

    # ── Routing / Protocols ──
    'process-id': 1,
    'area-id': '0.0.0.0',
    'vrf-name': 'default',
    'vrf': 'default',
    'af': 'ipv4-unicast',
    'instance-af': 'ipv4-unicast',
    'protocol': 'ospf',
    'routing-protocol-name': 'ospf',
    'as-number': 65001,
    'peer-as': 65002,
    'neighbor-id': '10.0.0.2',
    'nbr-id': '10.0.0.2',
    'nbr-addr': '10.0.0.2',
    'nbr-state': 'full',
    'network-type': 'broadcast',
    'if-state': 'point-to-point',
    'if-addr': 'fe80::1',
    'virtual-link': '0.0.0.0-1.1.1.1',

    # ── Wireless ──
    'ssid': 'Corporate-WiFi',
    'rssi': -65,
    'snr': 30,
    'band-id': 1,
    'audit-session-id': 'AC1001640000002B',

    # ── Identifiers ──
    'id': 10001,
    'session-id': 2147483650,
    'subscription-id': 2147483650,
    'index': 1,
    'uuid': '550e8400-e29b-41d4-a716-446655440000',

    # ── Counters / Stats ──
    'count': 5,
    'entry-count': 10,
    'total-num-of-aps': 100,
    'num-of-aps-predownloaded': 100,
    'num-of-aps-upgraded': 95,
    'aps-selected-for-upgd': 100,
    'num-of-iterations': 3,
    'current-iteration': 2,
    'serial-iter-num': 1,
    'percentage': 85,
    'percentage-completed': 85,
    'percentage-predownloaded': 100,
    'configured-threshold': 80,
    'threshold-reached-clear': False,

    # ── Time ──
    'timestamp': '2026-02-10T10:30:00Z',
    'expire-time': '2026-12-31T23:59:59Z',
    'start-time': '2026-02-10T10:00:00Z',
    'end-time': '2026-02-10T11:00:00Z',
    'expected-end-time': '2026-02-10T11:00:00Z',
    'seconds-left': 86400,
    'active-time': 3600,
    'uptime': 86400,

    # ── Software ──
    'version': '17.18.1',
    'from-version': '17.17.1',
    'to-version': '17.18.1',
    'upgrade-state': 'in-progress',
    'action-type': 'install-add',
    'sub-state': 'downloading',

    # ── Authentication / Security ──
    'username': 'admin',
    'user': 'admin',
    'is-fabric-client': False,
    'is-dot1x': True,
    'is-beacon-ds': False,
    'is-client': True,

    # ── Smart License ──
    'feature-name': 'network-advantage',
    'license-name': 'network-advantage',

    # ── DSL / Controller ──
    'shdsl-controller': 'DSL 0/0/0',
    'controller': 'DSL 0/0/0',

    # ── BGP specific ──
    'bgppeerremoteaddr': '10.0.0.2',
    'bgppeerlasterror': '0x00 0x00',
    'bgppeerstate': 'established',
    'cbgppeer2remoteaddr': '10.0.0.2',
    'cbgppeer2lasterror': '0x00 0x00',
    'cbgppeer2adminstatus': 'start',
    'cbgppeer2state': 'established',
    'cbgppeer2prevstate': 'openconfirm',
    'cbgppeer2localaddr': '10.0.0.1',
    'cbgppeer2prefixadminlimit': 1000,
    'cbgppeer2prefixthreshold': 75,
    'cbgppeer2prefixclearthreshold': 50,
    'cbgppeer2acceptedprefixes': 450,
    'cbgppeeracceptedprefixes': 450,
    'cbgppeerprefixadminlimit': 1000,
    'cbgppeerprefixthreshold': 75,
    'cbgppeerprefixclearthreshold': 50,
    'cbgppeerfsmnewstate': 'established',
    'cbgppeerfsmoldstate': 'openconfirm',

    # ── OSPF specific ──
    'ospfrouterid': '1.1.1.1',
    'ospfifstate': 'point-to-point',
    'ospfvirtifneighbor': '2.2.2.2',
    'ospfnbrstate': 'full',
    'ospfnbrrtrid': '2.2.2.2',
    'ospfnbripaddr': '10.0.0.2',
    'ospfvirtifareaid': '0.0.0.1',
    'ospfvirtifstate': 'point-to-point',
    'ospfvrtrouterid': '1.1.1.1',
    'ospflsdbareaid': '0.0.0.0',
    'ospflsdblsid': '10.0.0.0',
    'ospflsdbrouterid': '1.1.1.1',
    'ospflsdbtype': 'routerLSA',
    'ospfextlsdbtype': 'asExternalLSA',
    'ospfextlsdblsid': '172.16.0.0',
    'ospfextlsdbrouterid': '1.1.1.1',
    'ospfaddresslessif': 0,
    'ospfifipaddress': '10.0.0.1',
    'cospflsdbtype': 'asExternalLSA',
    'cospflsdbrouterid': '1.1.1.1',
    'cospflsdblsid': '10.0.0.0',
    'cospflsdbareaid': '0.0.0.0',
    'cospfshamlinksstatechange': 'up',
    'cospfshamlinkslocalipaddrtype': 'ipv4',
    'cospfshamlinkslocalipaddrress': '10.0.0.1',
    'cospfshamlinksremoteipaddrtype': 'ipv4',
    'cospfshamlinksremoteipaddrress': '10.0.0.2',
    'cospfshamlinksnbrareaid': '0.0.0.0',
    'cospfshamlinksnbrrtrid': '2.2.2.2',
    'cospfshamlinksnbripaddr': '10.0.0.2',
    'cospfshamlinksnbripaddresstype': 'ipv4',
    'cospfshamlinksnbripaddress': '10.0.0.2',
    'cospfshamlinkslocalipaddrtype': 'ipv4',
    'cospfshamlinkslocalipaddrress': '10.0.0.1',
    'cospfshamlinkslocalipadaddr': '10.0.0.1',

    # ── SNMP / Entity ──
    'entphysicalindex': 1,
    'entphysicaldescr': 'Cisco C9300-48P switch',
    'entphysicalcontainedin': 0,
    'entlogicalindex': 1,
    'entphysicalclass': 'chassis',
    'entphysicalname': 'Switch 1',
    'entstateadmin': 'unlocked',
    'entstateoper': 'enabled',
    'entstateusage': 'active',
    'entstatealarm': 'clear',
    'entstatestandby': 'cold-standby',

    # ── Config Management ──
    'ccmhistoryeventindex': 1,
    'ccmhistoryeventcommandsource': 'commandLine',
    'ccmhistoryeventconfigsource': 'running',
    'ccmhistoryeventconfigdestination': 'startup',
    'ccmhistoryrunninglastchanged': 123456,
    'ccmhistoryeventterminaltype': 'virtual',
    'ccmctidrequestid': 1,

    # ── Syslog ──
    'cloghistindex': 1,
    'cloghistfacility': 'SYS',
    'cloghistseverity': 'warning',
    'cloghistmsgname': 'CONFIG_I',
    'cloghistmsgtext': 'Configured from console by admin on vty0',
    'cloghisttimestamp': 123456789,

    # ── IF-MIB ──
    'ifadminstatus': 'up',
    'ifoperstatus': 'up',

    # ── HSRP ──
    'cstandbystate': 'active',
    'cstandbystateex': 'active',

    # ── IPSec / IKE ──
    'cikepeerlocalvalue': '10.0.0.1',
    'cikepeerremotevalue': '10.0.0.2',
    'cikepeerlocaladdr': '10.0.0.1',
    'cikepeerremoteaddr': '10.0.0.2',
    'cikepeerlocaltype': 'ipAddrPeer',
    'cikepeerremotetype': 'ipAddrPeer',
    'cikepeeractivetime': 3600,
    'cikenegslifailreason': 'none',
    'cikenegsp2lifailreason': 'none',
    'cipsectunactivetime': 3600,
    'cipsecspisvalue': 256,
    'cipsecspidvalue': 257,
    'cipsecspiprotocol': 'esp',
    'cipsecspiindirection': 'inbound',
    'cipsecspistatus': 'active',
    'cipstaticcrptomapsetname': 'VPN-MAP',
    'cipstaticcrptomapsetsize': 5,
    'cipstaticcrptomapseqnum': 10,
    'cipsecfailreason': 'none',
    'cipsectunlifetimeremaining': 3200,
    'cipsectunlifesize': 4608000,
    'cipsecspisize': 256,
    'cipsecfailpktsrcaddr': '10.0.0.1',
    'cipsecfailpktdstaddr': '10.0.0.2',
    'cipsstaticcrptomapsetname': 'VPN-MAP',
    'cipsstaticcrptomapsetsize': 5,

    # ── MPLS ──
    'mplsldpsessionstate': 'operational',
    'mplsldpsessionpeeraddr': '10.0.0.2',
    'mplsldpsessionstatediscontinuitytime': 0,
    'mplslspid': 'LSP-R1-to-R2',
    'mplstunnelname': 'TE-Tunnel1',
    'mplstunnelindex': 1,
    'mplstunneladminstatus': 'up',
    'mplstunneloperstatus': 'up',
    'mplstunnelrole': 'head',
    'mplsinoutifindex': 1,

    # ── VTP ──
    'vtpvlaneditoperation': 'copy',
    'vtpvlaneditbufferowner': 'admin@10.1.1.1',
    'vtpvlaneditconfigrevnumber': 5,
    'managementdomainname': 'CAMPUS',
    'vtpnotificationsemissons': 10,

    # ── StackWise ──
    'cswswitchnumcurrent': 1,
    'cswmaxswitchnum': 9,
    'cswswitchstate': 'ready',
    'cswswitchmacaddress': '00:1a:2b:3c:4d:5e',
    'cswringredundant': True,
    'cswstackportstatus': 'up',
    'cswstackportoperstatusstacking': True,

    # ── Ether CFM ──
    'cethercfmeventsvlan': 100,
    'cethercfmeventdomainindex': 1,
    'cethercfmeventserviceindex': 1,
    'cethercfmeventlclmpid': 1,
    'cethercfmeventlclmepid': 1,

    # ── Environment Monitoring ──
    'ciscoenvmonvoltagestatusindex': 1,
    'ciscoenvmonvoltagestatusdescr': 'PS1 Vout',
    'ciscoenvmonvoltagestatusvalue': 12000,
    'ciscoenvmonvoltagestate': 'normal',
    'ciscoenvmontemperaturestatusindex': 1,
    'ciscoenvmontemperaturestatusdescr': 'CPU Die Temperature',
    'ciscoenvmontemperaturestatusvalue': 45,
    'ciscoenvmontemperaturestate': 'normal',
    'ciscoenvmonfanstatusindex': 1,
    'ciscoenvmonfanstatusdescr': 'Fan Tray 1',
    'ciscoenvmonfanstate': 'normal',
    'ciscoenvmonsupplystatusindex': 1,
    'ciscoenvmonsupplystatusdescr': 'Power Supply 1',
    'ciscoenvmonsupplystate': 'normal',

    # ── Flash ──
    'ciscoflashdevicename': 'flash:',
    'ciscoflashdeviceindex': 1,
    'ciscoflashpartitionname': 'flash:',
    'ciscoflashpartitionindex': 1,
    'ciscoflashcopycompleted': True,
    'ciscoflashcopycompletiontime': '2026-02-10T10:30:00Z',
    'ciscoflashmiscopsource': 'flash:running-config',
    'ciscoflashmiscopdest': 'flash:startup-config',
    'ciscoflashmiscopcompletiontime': '2026-02-10T10:30:00Z',
    'ciscoflashdeviceremoved': False,
    'ciscoflashdeviceinserted': True,

    # ── RTTMON / IP SLA ──
    'rttmonctrladmintag': 'SLA-WAN-1',
    'rttmonctrladminindex': 1,
    'rttmonlatesthttpopersense': 'ok',
    'rttmonlatestjitteropercompletiontime': 50,
    'rttmonlatesticmpjitteropersense': 'ok',
    'rttmonctrloperstate': 'active',
    'rttmonctrloperdiagtext': 'OK',
    'rttmonreactvar': 'rtt',
    'rttmonreactthresholdtype': 'xof',
    'rttmonreactvalue': 100,
    'rttmonreactoccurred': True,

    # ── License ──
    'clmgmtfeaturename': 'network-advantage',
    'clmgmtlicensestoreused': 'primaryStore',
    'clmgmtlicensestorename': 'Primary License Storage',
    'clmgmtlicensefeaturename': 'network-advantage',
    'clmgmtlicensecomments': 'Permanent license',
    'clmgmtlicenseindex': 1,
    'clmgmtlicenseexpirydate': '2026-12-31T23:59:59Z',
    'clmgmtlicenseactionindex': 1,
    'clmgmtlicenseactionstate': 'completed',

    # ── Entity FRU ──
    'cefcphysicalstatus': 'ok',
    'cefcmoduleadminstatus': 'enabled',
    'cefcoperstatus': 'ok',
    'cefcfrupower': 400,
    'cefcfrucurrent': 2500,
    'cefctotalavailablesystempower': 1200,
    'cefcfrufanspeed': 5000,

    # ── Entity QFP ──
    'ceqfpsystemstate': 'active',
    'ceqfpnumberinuse': 1,
    'ceqfptotalcreated': 100,
    'ceqfpmemoryresthreshold': 80,

    # ── Entity Sensor ──
    'entphysicalindex': 1,
    'entsensorvalue': 45,
    'entsensorstatus': 'ok',

    # ── DISMAN ──
    'mtehotconditionname': 'cpu-high',
    'mtehottargetname': 'cpmCPUTotalMonIntervalValue',
    'mtehotcontextname': 'default',
    'mtehotobjectname': 'cpmCPUTotal5minRev',
    'mtehottrigger': 'cpu-threshold',

    # ── STP ──
    'stppxlnconsstancyupdate': 1,
    'stpextportindex': 1,
    'stpextportstate': 'forwarding',

    # ── NTP ──
    'cntppeerdispersion': 25,
    'cntppeerpollinterval': 64,
    'cntppeerstratum': 2,
    'cntppeerhostaddress': '10.0.0.1',
    'cntppeerremoteaddress': '10.0.0.2',

    # ── RF (Redundancy Framework) ──
    'crfstatuspeerunitstate': 'standbyHot',
    'crfstatuspeerstatechangereason': 'initialization',
    'crfstatusfailovertime': '2026-02-10T10:00:00Z',

    # ── SONET ──
    'csau4tug3': 1,
    'csatalarmtype': 'los',
    'csatstatuson': True,

    # ── Process MIB ──
    'cpmcputotalindex': 1,
    'cpmcputhresholdclass': 'total',
    'cpmcpurisingthresholdvalue': 90,
    'cpmcpufallingthresholdvalue': 80,
    'cpmcputotalmonintervalvalue': 85,
    'cpmcpuinterruptmonintervalvalue': 5,
    'cpmprocesspid': 128,
    'cpmprocextutil5secrev': 25,
    'cpmprocesstimecreated': 100,

    # ── IP URPF ──
    'cipurpfifdrops': 100,
    'cipurpfifdroprate': 10,

    # ── CEF ──
    'cefswitchingpath': 'ipv4',
    'cefinconsistencytype': 'missing-adjacency',
    'cefinconsistencyprevstate': 'consistent',
    'cefinconsistencynewstate': 'inconsistent',
    'cefresourcefailuretype': 'memory',

    # ── BFD ──
    'ciscobfdsessindex': 1,
    'ciscobfdsessinterface': 'GigabitEthernet1/0/1',
    'ciscobfdsessstate': 'up',
    'ciscobfdsessapplicationid': 1,
    'ciscobfdsessdiag': 'noDiagnostic',

    # ── PIM ──
    'pimintfindex': 1,
    'cpimrpaddresstype': 'ipv4',
    'cpimrpmappingchangetype': 'newMapping',

    # ── Subscriber Session ──
    'csubsessiontype': 'pppSubscriber',
    'csubsessionipaddressassignment': 'dhcp',
    'csubsessionstate': 'up',

    # ── TAP ──
    'ctap2mediationcontentid': 1001,
    'ctap2mediastreamindex': 1,
    'ctap2mediainterceptid': 100,

    # ── Data Collection ──
    'cdcvfileindex': 1,
    'cdcvfilename': 'show_tech_output.gz',
    'cdcvfilecollectionperiod': 3600,
    'cdcvfileretentionperiod': 86400,

    # ── Firewall ──
    'cufwalerttype': 'deny',
    'cufwpolicytargettype': 'interface',

    # ── VPDN ──
    'cvpdnsessionindex': 1,
    'cvpdntunneltype': 'l2tp',

    # ── Power over Ethernet ──
    'pethpsegroupindex': 1,
    'pethpseportdetectionstatus': 'deliveringPower',
    'pethpseportpowerclassifications': 'class3',
    'cpeextpseportpolicingcapable': True,
    'pethmaingroupindex': 1,

    # ── Frame Relay ──
    'frdlcmifindex': 1,
    'frcircuitifindex': 1,
    'frcircuitdlci': 100,
    'frcircuitstate': 'active',

    # ── Config Copy ──
    'cccopyindex': 1,
    'cccopystate': 'successful',
    'cccopyfailcause': 'none',

    # ── LLDP ──
    'lldpremchassisidsubtype': 'macAddress',
    'lldpremchassisid': '00:1a:2b:3c:4d:5e',
    'lldpremportidsubtype': 'interfaceName',
    'lldpremportid': 'Gi1/0/1',
    'lldpremsysname': 'neighbor-switch-01',

    # ── ISIS ──
    'ciiisadjareaaddress': '49.0001',
    'ciisisadjstate': 'up',
    'ciisisadjipaddress': '10.0.0.2',
    'ciiisadjlspid': '0001.0001.0001.00-00',
    'ciicircuittype': 'level1',

    # ── PW (Pseudowire) ──
    'vc-peer-address': '10.0.0.2',
    'vc-id': 100,
    'vc-list': [{'vc-peer-address': '10.0.0.2', 'vc-id': 100}],

    # ── EIGRP ──
    'ceigr-peer-address': '10.0.0.2',
    'ceigr-as': 100,

    # ── Bulk File ──
    'cbfstatusfileindex': 1,
    'cbfstatusfilestate': 'running',

    # ── NBAR ──
    'nbarstatsprotocolname': 'http',
    'nbarstatsbyterate': 1000000,

    # ── Net Sync ──
    'cnstsselectedinputtype': 'e1',
    'cnstsselectedinputname': 'T1 0/0/0',

    # ── DOT3 OAM ──
    'dot3oampeerindex': 1,
    'dot3oamloopbackstatus': 'noLoopback',

    # ── Image License ──
    'cilmimglicenseimagelevel': 'ipservicesk9',

    # ── RSVP ──
    'rsvpsenderadspecpath': 1,
    'rsvpsendertspecburst': 1000,
    'rsvpsenderinterval': 100,

    # ── RMON ──
    'rmonalarmindex': 1,
    'rmonalarmvariable': 'ifInOctets.1',
    'rmonalarmsamplinginterval': 300,
    'rmonalarmvalue': 1000000,

    # ── SNMPv2 ──
    'snmptrapcommunity': 'public',
    'snmptrapenterprise': '1.3.6.1.4.1.9',

    # ── DS1/DS3 ──
    'dsx1lineindex': 1,
    'dsx1linestatus': 'noAlarm',
    'dsx3lineindex': 1,
    'dsx3linestatus': 'noAlarm',

    # ── ATM PVC ──
    'ifindex': 1,
    'atmvclvpi': 0,
    'atmvclvci': 100,
    'catmstatusupvclrangestartindex': 1,
    'catmstatusupvclrangeendindex': 10,
    'catmpvclfailurevreason': 'none',
    'catmpvclstatuschangestart': 0,
    'catmpvclstatuschangeend': 10,

    # ── IP Local Pool ──
    'ciplocalpoolfreeaddrs': 50,
    'ciplocalpoolgroupcontainedin': 1,
    'ciplocalpoolname': 'VPN-POOL-1',

    # ── MSDP ──
    'msdppeerfsmestablishedtransitions': 5,
    'msdppeerremoteaddress': '10.0.0.2',

    # ── IPMROUTE ──
    'ipmrteroutegroup': '239.1.1.1',
    'ipmrteroutesource': '10.0.0.1',

    # ── Bridge Domain ──
    'bd-id': 100,
    'bd-status': 'up',

    # ── Kicker ──
    'kicker-name': 'config-change-kicker',
    'kicker-id': 'kicker-001',

    # ── Smart License ──
    'feature-name': 'network-advantage',
}

# ──────────────────────────────────────────────────────────────
# Pattern-based fallback matching  
# ──────────────────────────────────────────────────────────────
PATTERN_EXAMPLES = [
    # Address patterns
    (r'addr|address', '10.0.0.1'),
    (r'ipaddr', '10.0.0.1'),
    (r'mac', '00:1a:2b:3c:4d:5e'),
    # Status/State
    (r'state|status', 'active'),
    (r'oper', 'up'),
    (r'admin', 'enabled'),
    # Names/Descriptions
    (r'name$', 'router-01'),
    (r'descr', 'System component'),
    (r'text', 'Informational message text'),
    (r'comment', 'Configured by admin'),
    # Indices
    (r'index$', 1),
    (r'^id$', 10001),
    # Intervals/Time
    (r'time$|timestamp', 3600),
    (r'interval', 300),
    (r'period', 3600),
    # Counters
    (r'count|num|total', 5),
    (r'rate$', 100),
    (r'value$', 1000),
    (r'size$', 256),
    (r'level$', 'normal'),
    (r'type$', 'standard'),
    (r'class$', 'default'),
    # Reason/Error
    (r'reason$', 'configuration-applied'),
    (r'error$', '0x00 0x00'),
    (r'fail', 'none'),
    (r'cause$', 'none'),
    # VLAN
    (r'vlan|svlan', 100),
    (r'vpi', 0),
    (r'vci', 100),
    # Direction
    (r'direction', 'inbound'),
    (r'protocol', 'ip'),
    # Identifiers
    (r'tag$', 'SLA-Monitor-1'),
    (r'owner$', 'admin'),
    (r'source', 'running'),
    (r'dest|destination', 'startup'),
    (r'set$', 'policy-set-1'),
    (r'seq', 10),
]


def get_realistic_value(leaf_name, current_value):
    """Get a realistic example value for a leaf name."""
    if current_value not in GENERIC_VALUES:
        return current_value  # Already realistic
    
    # Exact match (case-insensitive)
    key = leaf_name.lower().replace('_', '-')
    if key in LEAF_EXAMPLES:
        return LEAF_EXAMPLES[key]
    
    # Remove common prefixes for MIB columns
    # e.g., ciscoEnvMonVoltageStatusDescr -> voltagestatusdescr
    short = key
    for prefix in ('cisco', 'cef', 'cpm', 'cip', 'clm', 'csw', 'cnt', 'crf',
                    'csa', 'cug', 'ceth', 'cvp', 'peth', 'cpe', 'cbf', 
                    'nbar', 'cnst', 'dot3', 'cilm', 'cbgp', 'mpls',
                    'rttmon', 'csubsession', 'ctap2', 'cdc', 'cufw',
                    'rsvp', 'rmon', 'snmp', 'dsx', 'atm', 'cat', 'fr'):
        if short.startswith(prefix) and len(short) > len(prefix):
            short = short[len(prefix):]
            if short in LEAF_EXAMPLES:
                return LEAF_EXAMPLES[short]
    
    # Pattern-based matching
    for pattern, value in PATTERN_EXAMPLES:
        if re.search(pattern, key, re.IGNORECASE):
            return value
    
    # Last resort: derive from current leaf name
    # For enum-like types, make a readable value
    parts = leaf_name.replace('_', '-').split('-')
    if len(parts) >= 2:
        return '-'.join(parts[-2:]).lower()
    
    return leaf_name.lower()


def fix_examples_recursive(obj, depth=0):
    """Recursively fix generic values in an example object."""
    fixes = 0
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, str) and val in GENERIC_VALUES:
                new_val = get_realistic_value(key, val)
                if new_val != val:
                    obj[key] = new_val
                    fixes += 1
            elif isinstance(val, dict):
                fixes += fix_examples_recursive(val, depth + 1)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        fixes += fix_examples_recursive(item, depth + 1)
    return fixes


def main():
    mode = 'DRY-RUN' if DRY_RUN else 'APPLYING'
    print(f'=== Fix Generic Example Values ({mode}) ===\n')
    
    files = sorted(f for f in os.listdir(EVENTS_DIR)
                   if f.endswith('.json') and f != 'manifest.json')
    
    total_fixes = 0
    files_fixed = 0
    remaining_generic = 0
    
    for fn in files:
        spec_path = os.path.join(EVENTS_DIR, fn)
        with open(spec_path, encoding='utf-8') as fh:
            spec = json.load(fh)
        
        file_fixes = 0
        schemas = spec.get('components', {}).get('schemas', {})
        
        for name, schema in schemas.items():
            if 'example' in schema:
                file_fixes += fix_examples_recursive(schema['example'])
        
        # Also fix inline examples in paths
        for path_key, path_obj in spec.get('paths', {}).items():
            for method_key, op in path_obj.items():
                if not isinstance(op, dict):
                    continue
                for status, resp in op.get('responses', {}).items():
                    if isinstance(resp, dict):
                        content = resp.get('content', {})
                        for ct, ct_val in content.items():
                            if isinstance(ct_val, dict) and 'example' in ct_val:
                                file_fixes += fix_examples_recursive(ct_val['example'])
                # Fix request body examples too
                if 'requestBody' in op:
                    rb = op['requestBody']
                    if isinstance(rb, dict) and 'content' in rb:
                        for ct, ct_val in rb['content'].items():
                            if isinstance(ct_val, dict) and 'example' in ct_val:
                                file_fixes += fix_examples_recursive(ct_val['example'])
        
        if file_fixes > 0:
            files_fixed += 1
            total_fixes += file_fixes
            print(f'  FIX  {fn} => {file_fixes} values replaced')
            
            if not DRY_RUN:
                with open(spec_path, 'w', encoding='utf-8') as fh:
                    json.dump(spec, fh, indent=2, ensure_ascii=False)
                    fh.write('\n')
        
        # Count remaining generics
        for name, schema in schemas.items():
            if 'example' in schema:
                remaining_generic += _count_generic(schema['example'])
    
    print(f'\n=== Summary ===')
    print(f'Files fixed:       {files_fixed}/{len(files)}')
    print(f'Values replaced:   {total_fixes}')
    print(f'Remaining generic: {remaining_generic}')


def _count_generic(obj):
    """Count remaining generic values."""
    count = 0
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v in GENERIC_VALUES:
                count += 1
            elif isinstance(v, (dict, list)):
                count += _count_generic(v)
    elif isinstance(obj, list):
        for item in obj:
            count += _count_generic(item)
    return count


if __name__ == '__main__':
    main()
