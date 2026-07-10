# Multi-Zone Perimeter Security and Cross-Platform Enterprise Identity Hardening

## Technical Specifications & Topology
* **Hypervisor Platform:** UTM / Apple Silicon Hypervisor Framework
* **Perimeter Security:** OPNsense Firewall (FreeBSD-based Appliance)
* **External Attack Vector Node:** Ubuntu Server LTS (192.168.64.X /24 Zone)
* **Internal Target Node:** Debian Server (192.168.100.X /24 Zone)
* **Central Identity Control Plane:** Windows Server Domain Controller (corp.local)
* **Integration Framework:** System Security Services Daemon (SSSD), Pluggable Authentication Modules (PAM) Stacking


## Project 1: Virtual Network Perimeter & Transport-Layer Evasion

### 1. Network Topology & Perimeter Routing
To bypass the unrealistic nature of flat virtual switches, I engineered a true multi-zone perimeter environment. I deployed an **OPNsense firewall** as a central virtual appliance to enforce strict Layer 3 network segmentation, isolating my Ubuntu attacking node on the external WAN segment from my target Debian server on a private internal LAN zone.

#### Infrastructure Blocker & Resolution
During early testing, incoming traffic to disabled ports timed out as FILTERED instead of instantly dropping as CLOSED. By analyzing the OPNsense state table and inspecting the Live View traffic log telemetry, I diagnosed a dual-fault infrastructure conflict:
1. **NAT Precedence:** The firewall's network address translation engine was dropping unroutable inbound packets prior to evaluating my manual interface rules.
2. **CIDR Mismatch:** I identified an accidental (/32) host mask allocation on the destination object instead of the required (/24) subnet boundaries.

**The Fix:** I stripped the conflicting NAT map entries, corrected the target mask to match the internal network architecture, and confirmed via firewall telemetry that OPNsense was actively shooting back `RST` packets to reject scanning probes at the edge.

### 2. Transport-Layer Evasion & System Compromise

#### Hydra Brute-Force & Access Exploitation
With the perimeter verified, I evaluated host-based logging limitations against network-level visibility. I initiated an explicit brute-force credential attack against Port 22 (SSH) using Hydra from my Ubuntu attacking node. 

**The Result:** My attack successfully cracked the target credentials. I used the recovered parameters to establish a live SSH session from the Ubuntu node, bypassing the network boundary and gaining **full interactive terminal access over the target Debian server**. However, because this completed a full TCP 3-way handshake (SYN → SYN-ACK → ACK), my inspection of the internal target's application logs confirmed a massive, noisy forensic trail:

```bash
# Target Debian Machine Log Audit showing the successful compromise via Hydra
$ journalctl -t sshd
Jun 21 14:22:01 debian-target sshd[4012]: Accepted password for root from 192.168.64.15 port 22 ssh2
```


To evaluate how an attacker could map out the same target layout without ringing user-space alarms, I authored a custom Python script using the Scapy library to execute a half-open TCP SYN scan. The script builds raw packets to send an isolated SYN flag, catches the target's SYN-ACK response to verify the port, and immediately drops an RST frame to break the socket before the final handshake stage. This process prevents the kernel from escalating the connection to application logging handlers—leaving journalctl blind to the reconnaissance phase. Proving the difference in user and network based detection and journaling, as the opnsense firewall did register the connection. 

## Project 2: Enterprise Escalation & Active Directory Federation
## Project 2 Overview
This project demonstrates the enterprise integration of heterogeneous Linux endpoints (**Ubuntu Desktop** and **Debian Server**) into a centralized Windows Active Directory forest (corp.local). The objective was to eliminate "fail-open" authentication bugs and enforce centralized, time-based administrative access controls (**Logon Hours**) managed at the Domain Controller level.

## Architecture & Data Flow
1. **Windows Domain Controller:** Holds the master user database and the 6:00 AM – 5:00 PM logon restrictions.
2. **SSSD (System Security Services Daemon):** Intercepts Linux login requests and passes them to AD via Kerberos/LDAP.
3. **PAM (Pluggable Authentication Modules):** Evaluates local OS rules and forces the system to comply with SSSD rejections.

---

## Technical Implementations

### 1. Active Directory Policy Configuration
The target administrative account (linux_admin_jose) was restricted within Active Directory Users and Computers (ADUC) to a strict operational window between **6:00 AM and 5:00 PM**.

### 2. Hardening SSSD (sssd.conf)
To ensure Group Policy Objects (GPOs) are strictly respected and to prevent offline bypasses, credential caching was completely disabled.

### 3. Hardening PAM Stacking (/etc/pam.d/common-account)
The Linux account verification framework was modified to ensure that if Active Directory denies access, the local OS cannot fall back to a "success" state.

---

## Verification & Forensic Proof

### Test Scenario: Live Access Window Verification (Successful Baseline)
When the domain user authenticates within permitted hours, the execution pipeline processes cleanly across both the local client log framework and the central Active Directory Domain Controller network tracking logs.

#### Debian Server Connection Pair:
Checking the local authentication log verifies the connection sequence, which explicitly registers on the Windows Domain Controller as a matching network logon event.
![Debian pam_unix Authentication Stream](1.png)  <img width="717" height="40" alt="1" src="https://github.com/user-attachments/assets/0b98d4f9-448b-45e4-814c-240eddb5f742" />

![Windows Security Audit - Event 4624 (3:26 PM)] <img width="643" height="477" alt="2" src="https://github.com/user-attachments/assets/3c7a12e9-ea4b-4246-b76a-a7d359f885b3" />


#### Ubuntu Desktop Connection Pair:
Similarly, verifying the interactive session initialization on the Ubuntu desktop maps perfectly to a successful cryptographic network verification on the Domain Controller.
![Ubuntu systemd-logind Session Init]
<img width="800" height="107" alt="3" src="https://github.com/user-attachments/assets/3eb87124-b545-410b-93fb-ed23eb624a5c" />


![Windows Security Audit - Event 4624 (4:43 PM)]

<img width="577" height="389" alt="4" src="https://github.com/user-attachments/assets/deb8a3f6-e2fe-404d-8ed5-18c01925254c" />


### Test Scenario: After-Hours SSH Administrative Access
* **Test Time:** Past 5:00 PM (Outside the permitted 6:00 AM – 5:00 PM window)
* **Action:** Attempting an interactive loopback SSH session as the domain administrator.

### Proof 1: Endpoint Session Lockout (User Experience)
When attempting to connect, the system correctly processes the credentials but throws a secure, masked access rejection.

<img width="660" height="156" alt="image" src="https://github.com/user-attachments/assets/ba815ad4-c903-4dcd-9199-22b28bdc4378" />

<img width="409" height="75" alt="image" src="https://github.com/user-attachments/assets/1c9cc702-270d-4680-93fb-fff87f965be0" />

### Proof 2: Linux Authentication Telemetry
Checking the local authentication infrastructure logs shows that PAM successfully handled the real-time SSSD rejection tracking code. The local SSSD caches handle the time regulation autonomously on the edge nodes, immediately blocking access after 5:00 PM.

#### Ubuntu Client Local PAM Block:
![Ubuntu pam_sss System Error Telemetry]

<img width="802" height="159" alt="5" src="https://github.com/user-attachments/assets/e60223b4-8b52-4dfe-b318-73cc23b9ff70" />

#### Debian Server Local PAM Block:
![Debian pam_sss Permission Denied Telemetry]
<img width="870" height="161" alt="6" src="https://github.com/user-attachments/assets/badaa4e7-6088-4739-b683-4a9e8f19f1d4" />


### Proof 3: Active Directory Policy Boundary & Edge Enforcement
Because the Linux machines resolve account parameters locally via SSSD, the logon hours restriction is enforced directly at the local gateway by the Linux PAM framework (pam_sss) rather than by the Windows AD. When an SSH attempt is made past 5:00 PM, the local system evaluates the cached account attributes, identifies the time restriction violation, and drops the connection instantly with a Permission denied error. Because the authentication attempt is intercepted and blocked internally by Linux, no authentication traffic reaches the Windows Domain Controller, keeping the server-side Event Viewer clear while successfully securing the endpoint.
