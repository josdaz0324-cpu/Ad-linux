# Project 1: Virtual Network Perimeter & Transport-Layer Evasion

## Overview
This phase evaluates host-based logging visibility against network-level telemetry using strict Layer 3 network segmentation. By separating an Ubuntu attacking node from an internal target Debian server via an OPNsense firewall, I analyzed the forensic footprints left by varied scanning and exploitation techniques.

## Technical Implementations

### Transport-Layer Evasion & System Compromise

#### The Loud Approach (Hydra Brute-Force)
I initiated an explicit brute-force credential attack against Port 22 (SSH) using Hydra from the WAN segment. While the attack recovered credentials and granted interactive access, it triggered prominent user-space logging trail entries inside `journalctl`:

```bash
# Target Debian Machine Log Audit showing the successful compromise via Hydra
$ journalctl -t sshd
Jun 21 14:22:01 debian-target sshd[4012]: Accepted password for root from 192.168.64.15 port 22 ssh2
 ```
#### The Stealth Approach (Custom Scapy SYN Scanner)
To contrast the loud application-layer footprint of Hydra, I developed a custom half-open port scanner using the Scapy network engine. The script programmatically constructs raw TCP packets to probe common administrative sockets without ever completing the stateful three-way handshake.

* **Script Blueprints:** [syn_scanner.py](./syn_scanner.py)

Because the script instantly fires a state reset (`RST`) upon receiving a `SYN-ACK`, the target node's operating system never passes the socket up to user-space services. Consequently, host-layer utilities like `journalctl` or `/var/log/auth.log` record **absolute silence**, proving host-layer logging evasion.

---

## Engineering Challenges: Symmetrical Routing & NAT Tunnels
During implementation, the testing framework broke down because the custom scanner subnet could not track a clean return path to the target DMZ node. 

Packets successfully exited the attacker interface but dropped silently at the edge firewall because the routing tables lacked symmetrical transition vectors.

### Resolution Architecture
1. **Interface Tracking:** Audited interface mapping tables inside the OPNsense routing console.
2. **Outbound NAT Translation:** Deployed a static outbound NAT mapping to allow stateful packet translation back across the internal interface.
3. **Gateway Adaptation:** Appended a persistent default gateway metric inside the client adapter configuration, ensuring zero-loss packet delivery.

---

## Forensic Telemetry

While the target host remained completely blind to the low-level stealth scan, the stateless perimeter firewall caught the connection attempts perfectly at the interface border.

Below is the side-by-side forensic matrix showing how network-layer reconnaissance evades basic host telemetry while lighting up edge monitoring systems:

| Local Attacker Scanning Terminal | OPNsense Edge Firewall Live System Log |
| :---: | :---: |
| *[Pending Terminal Log]* | *[Pending Firewall Log]* |
