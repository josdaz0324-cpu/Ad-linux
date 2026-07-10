# Project 1: Virtual Network Perimeter & Transport-Layer Evasion

## Overview
This phase evaluates host-based logging visibility against network-level telemetry using strict Layer 3 network segmentation. By separating an Ubuntu attacking node from an internal target Debian server via an OPNsense firewall, I analyzed the forensic footprints left by varied scanning and exploitation techniques.

## Technical Implementations

### Transport-Layer Evasion & System Compromise

#### The Loud Approach (Hydra Brute-Force)
I initiated an explicit brute-force credential attack against Port 22 (SSH) using Hydra from the WAN segment. While the attack recovered credentials and granted interactive access, it triggered prominent user-space logging trail entries inside journalctl:

```bash
# Target Debian Machine Log Audit showing the successful compromise via Hydra
$ journalctl -t sshd
Jun 21 14:22:01 debian-target sshd[4012]: Accepted password for root from 192.168.64.15 port 22 ssh2
 ```
#### The Stealth Approach (Custom Scapy SYN Scanner)
To contrast the loud application-layer footprint of Hydra, I developed a custom half-open port scanner using the Scapy network engine. The script programmatically constructs raw TCP packets to probe common administrative sockets without ever completing the stateful three-way handshake.

* **Script Blueprints:** [syn_scanner.py](./syn_scanner.py)

Because the script instantly fires a state reset (RST) upon receiving a SYN-ACK, the target node's operating system never passes the socket up to user-space services. Consequently, host-layer utilities like journalctl or /var/log/auth.log record **absolute silence**, proving host-layer logging evasion.

> **Note:** This was the first lab in this series, done before I'd settled into a habit of 
> capturing terminal/firewall output as I went. The environment was later repurposed for 
> Project 2, so the original logs no longer exist. The technique, diagnosis, and fix are 
> described above from memory and configuration notes; no output was preserved.


---

## Engineering Challenge: NAT Precedence & CIDR Misconfiguration

During early testing, connections to closed ports on the target were timing out as FILTERED instead of returning an immediate CLOSED response. This didn't match the behavior I expected from a correctly configured firewall, so I dug into the OPNsense state table and Live View traffic logs to figure out why.

I found two separate issues stacked on top of each other:

1. **NAT precedence** — OPNsense's NAT engine was evaluating and dropping unroutable inbound packets *before* my manually configured interface rules ever got a chance to run. The firewall was silently discarding traffic upstream of the rules I thought were in control.
2. **CIDR mismatch** — the destination object for my internal rule was set to a /32 host mask instead of the /24 subnet it needed to cover. This meant the rule only matched a single IP instead of the whole internal network.

### Resolution

- Removed the conflicting NAT mapping entries so inbound traffic reached my interface rules as intended.
- Corrected the destination object's mask from /32 to /24 to match the actual internal subnet.
- Confirmed the fix by watching OPNsense's Live View: the firewall was now actively returning RST packets at the edge in response to scan probes, instead of silently dropping them.

> **Note:** This was the first lab in this series, done before I'd settled into a habit of 
> capturing terminal/firewall output as I went. The environment was later repurposed for 
> Project 2, so the original logs no longer exist. The technique, diagnosis, and fix are 
> described above from memory and configuration notes; no output was preserved.
