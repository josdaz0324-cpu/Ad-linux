# Cross-Platform Identity Hardening: Active Directory & Linux PAM Integration

## Project Overview
This project demonstrates the enterprise integration of heterogeneous Linux endpoints (**Ubuntu Desktop** and **Debian Server**) into a centralized Windows Active Directory forest (`corp.local`). The objective was to eliminate "fail-open" authentication bugs and enforce centralized, time-based administrative access controls (**Logon Hours**) managed at the Domain Controller level.

## Architecture & Data Flow
1. **Windows Domain Controller:** Holds the master user database and the 6:00 AM – 5:00 PM logon restrictions.
2. **SSSD (System Security Services Daemon):** Intercepts Linux login requests and passes them to AD via Kerberos/LDAP.
3. **PAM (Pluggable Authentication Modules):** Evaluates local OS rules and forces the system to comply with SSSD rejections.

---

## Technical Implementations

### 1. Active Directory Policy Configuration
The target administrative account (`linux_admin_jose`) was restricted within Active Directory Users and Computers (ADUC) to a strict operational window between **6:00 AM and 5:00 PM**.

### 2. Hardening SSSD (`sssd.conf`)
To ensure Group Policy Objects (GPOs) are strictly respected and to prevent offline bypasses, credential caching was completely disabled.

### 3. Hardening PAM Stacking (`/etc/pam.d/common-account`)
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
Because the Linux machines resolve account parameters locally via SSSD, the logon hours restriction is enforced directly at the local gateway by the Linux PAM framework (`pam_sss`) rather than by the Wndows AD. When an SSH attempt is made past 5:00 PM, the local system evaluates the cached account attributes, identifies the time restriction violation, and drops the connection instantly with a `Permission denied` error. Because the authentication attempt is intercepted and blocked internally by Linux, no authentication traffic reaches the Windows Domain Controller, keeping the server-side Event Viewer clear while successfully securing the endpoint.
