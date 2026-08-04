# Corporate Infrastructure Security Lab & Defensive Engineering Portfolio

## Overview
This repository contains actionable defense blueprints, infrastructure configurations, and forensic telemetry demonstrating defensive engineering across enterprise identity planes and network perimeters.

The lab is structured into isolated operational modules to demonstrate cross-platform integration, centralized access controls, and custom network-layer monitoring tools.

---

## Repository Architecture

### [Project 1: Advanced Network Surveillance & Layer 4 Perimeter Defense](./project1-network-perimeter/)
* **Focus:** Low-level network telemetry, custom Python scanning infrastructure, and host-log evasion.
* **Core Artifacts:** Custom Scapy stealth scanning script, live OPNsense firewall log telemetry.
* **Objective:** Developing tactical scripts to audit internal perimeter tracking while capturing real-time stateless connection alerts at the network edge.

### [Project 2: Enterprise Escalation & Active Directory Federation](./project2-ad-linux-integration/)
* **Focus:** Centralized identity management, cross-platform policy enforcement, and authentication security.
* **Core Artifacts:** Hardened System Security Services Daemon configuration (`sssd.conf`), Pluggable Authentication Modules framework (`pam.d/common-account`), side-by-side client/DC forensic logs.
* **Objective:** Integrating heterogeneous Linux endpoints (Ubuntu & Debian) into a central Windows Server Domain Controller to enforce granular, real-time administrative access windows (**Logon Hours**) with mandatory after-hours lockout policies.

### [Project 3: Centralized SIEM & Telemetry Pipeline Deployment](./project3-siem-telemetry/)
* **Focus:** Containerized SIEM orchestration, centralized Fleet Agent governance, and cross-platform log aggregation.
* **Core Artifacts:** Dockerized Elasticsearch & Kibana environment, Fleet Server deployment scripts, active `elastic-agent` policy integrations.
* **Objective:** Building an enterprise log collection pipeline to capture real-time security events, resolve self-signed TLS certificate constraints across isolated network nodes, and centralize security telemetry into Kibana.

---

## Technology Stack & Tooling
* **Identity & Directory Services:** Active Directory Domain Services (AD DS), Kerberos, LDAP
* **SIEM & Log Aggregation:** Elastic Stack (Elasticsearch 8.12, Kibana), Elastic Agent, Fleet Server
* **Linux Security Modules:** PAM (Pluggable Authentication Modules), SSSD (System Security Services Daemon)
* **Network & Firewalls:** OPNsense, TCP/IP Stateless Filtering, Scapy (Python Network Engine)
* **Virtualization & Containers:** Docker Engine, Docker Bridge Networking
* **Operating Systems:** Windows Server 2022, Debian Linux, Ubuntu Linux
* **Forensics & Auditing:** Kibana Discover (`logs-*`), Linux Syslog (`/var/log/auth.log`), Windows Security Event Viewer (Event ID 4624 / Failure Audits)

---

## Guide
1. Navigate into individual project directories to review raw infrastructure configuration assets and scripts.
2. Read the dedicated markdown guides inside each folder for deep-dive technical explanations, operational breakdowns, and side-by-side forensic telemetry screenshots proving successful policy execution.
