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
