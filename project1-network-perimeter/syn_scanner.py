#!/usr/bin/env python3
import random
import time
import sys
import logging
from dataclasses import dataclass, field
from typing import Optional
from scapy.all import IP, TCP, sr1, send, conf

# Suppress Scapy runtime logging noise
conf.verb = 0
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# =============================================================================
# HARDWARE CONFIGURATION & TELEMETRY TUNING
# =============================================================================
TARGET_PORTS: list[int] = [22, 80]
PROBE_TIMEOUT: int = 3

# Simulated WAN link jitter bounds to stress-test target state machines
JITTER_MIN: float = 15.0
JITTER_MAX: float = 45.0

# Real-world OS TCP window fingerprints (Linux, Windows, macOS, Embedded IoT)
OS_WINDOW_SIZES: list[int] = [8192, 16384, 29200, 64240, 65535]


@dataclass
class ProbeResult:
    """Encapsulates telemetry payload for an independent layer-4 probe."""
    target_ip: str
    dest_port: int
    src_port: int
    window_size: int
    state: str  # "open" | "closed" | "filtered"
    rtt_ms: Optional[float] = None


@dataclass
class ScanSummary:
    """Aggregates multi-endpoint network tracking metrics."""
    target_ip: str
    results: list[ProbeResult] = field(default_factory=list)

    @property
    def open_ports(self) -> list[int]:
        return [r.dest_port for r in self.results if r.state == "open"]

    @property
    def avg_rtt_ms(self) -> Optional[float]:
        rtts = [r.rtt_ms for r in self.results if r.rtt_ms is not None]
        return round(sum(rtts) / len(rtts), 3) if rtts else None


# =============================================================================
# PACKET ARCHITECTURE ENGINE
# =============================================================================
def get_ephemeral_port() -> int:
    """Returns a randomized port from the extended OS ephemeral range."""
    return random.randint(1024, 65535)


def get_fingerprint_window() -> int:
    """Samples an operating system window metric to test destination quirks."""
    return random.choice(OS_WINDOW_SIZES)


def execute_jitter_delay() -> float:
    """Calculates variable propagation paths to simulate non-sequential flows."""
    return random.uniform(JITTER_MIN, JITTER_MAX)


# =============================================================================
# CORE TELEMETRY ENGINE
# =============================================================================
def send_syn_probe(target_ip: str, dest_port: int) -> ProbeResult:
    """
    Constructs a raw Layer-3 IP packet containing a customized TCP SYN segment.
    Evaluates response telemetry and injects an immediate RST to clean state tables.
    """
    src_port = get_ephemeral_port()
    window = get_fingerprint_window()
    isn = random.randint(1000, 9000000)

    packet = (
        IP(dst=target_ip)
        / TCP(
            sport=src_port,
            dport=dest_port,
            flags="S",
            window=window,
            seq=isn,
        )
    )

    print(f"  [TX] ➔ port {dest_port:>5} | src_port={src_port} | window={window}")

    t_send = time.perf_counter()
    response = sr1(packet, timeout=PROBE_TIMEOUT, verbose=0)
    t_recv = time.perf_counter()

    rtt_ms: Optional[float] = None

    if response is None:
        state = "filtered"
    elif response.haslayer(TCP):
        rtt_ms = round((t_recv - t_send) * 1000, 3)
        tcp_flags = response[TCP].flags

        if tcp_flags == 0x12:  # SYN-ACK
            state = "open"
            rst = (
                IP(dst=target_ip)
                / TCP(
                    sport=src_port,
                    dport=dest_port,
                    flags="R",
                    seq=response[TCP].ack,
                )
            )
            send(rst, verbose=0)
        elif tcp_flags == 0x14:  # RST-ACK
            state = "closed"
        else:
            state = "filtered"
    else:
        state = "filtered"

    print(f"  [RX] 🠈 port {dest_port:>5} | state={state.upper():<8} | rtt={f'{rtt_ms} ms' if rtt_ms else 'N/A'}")

    return ProbeResult(
        target_ip=target_ip,
        dest_port=dest_port,
        src_port=src_port,
        window_size=window,
        state=state,
        rtt_ms=rtt_ms,
    )


# =============================================================================
# EXECUTION & LOG OUTPUT ORCHESTRATION
# =============================================================================
def run_scan(target_ip: str, ports: list[int]) -> ScanSummary:
    summary = ScanSummary(target_ip=target_ip)
    shuffled_ports = ports.copy()
    random.shuffle(shuffled_ports)

    print(f"\n{'='*60}")
    print(f"  TARGET IDENTITY   : {target_ip}")
    print(f"  PROBE ARRAY       : {shuffled_ports} (Shuffled Queue)")
    print(f"  LINK JITTER BOUNDS: {JITTER_MIN}–{JITTER_MAX} s")
    print(f"{'='*60}\n")

    for idx, port in enumerate(shuffled_ports):
        print(f"[Sequence {idx + 1}/{len(shuffled_ports)}]")
        result = send_syn_probe(target_ip, port)
        summary.results.append(result)

        if idx < len(shuffled_ports) - 1:
            delay = execute_jitter_delay()
            print(f"  [~] Injecting path jitter: {delay:.2f} s...\n")
            time.sleep(delay)

    return summary


def print_summary(summary: ScanSummary) -> None:
    STATE_ICON = {"open": "✓", "closed": "✗", "filtered": "?"}

    print(f"\n{'='*60}")
    print(f"  TELEMETRY REPORT — {summary.target_ip}")
    print(f"{'='*60}")
    print(f"  {'PORT':<8} {'STATE':<10} {'SRC PORT':<12} {'WINDOW':<10} {'RTT (ms)'}")
    print(f"  {'-'*55}")

    for r in sorted(summary.results, key=lambda x: x.dest_port):
        icon = STATE_ICON.get(r.state, "?")
        rtt = f"{r.rtt_ms}" if r.rtt_ms is not None else "—"
        print(f"  {icon} {r.dest_port:<7} {r.state.upper():<10} {r.src_port:<12} {r.window_size:<10} {rtt}")

    print(f"  {'-'*55}")
    print(f"  Identified Active Gateways : {summary.open_ports or 'None'}")
    print(f"  Calculated Mean Link RTT   : {summary.avg_rtt_ms or 'N/A'} ms")
    print(f"{'='*60}\n")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(1)
    run_scan(sys.argv[1], TARGET_PORTS)


if __name__ == "__main__":
    main()
