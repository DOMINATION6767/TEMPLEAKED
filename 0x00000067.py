#!/usr/bin/env python3
"""
WHERE WIMS MEET - LEAKED
Some utilites have been deleted for being no user friendly

THIS IS A DEV VERSION LEAKED
originally made for 3.7 version
no credits go crazy with it (security was shit check it lol)
"""

import json
import random
import re
import string
import sys
import time
import os
import threading
import ctypes
import subprocess
import socket
import uuid
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

# ============================================================================
# LAUNCHER SECURITY
# ============================================================================

REQUIRED_TOKEN = "LEAKED-TOKEN-BY-NORP"

# Windows color support
try:
    import colorama
    colorama.init()
except ImportError:
    pass

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("=" * 60)
    print("  ERROR: Missing dependencies!")
    print("  Install with: pip install requests beautifulsoup4 colorama")
    print("=" * 60)
    input("Press Enter to exit...")
    sys.exit(1)


# ============================================================================
# THREAD-SAFE FILE LOCKING
# ============================================================================

class FileLock:
    """Simple file-based locking for cross-process synchronization."""
    
    def __init__(self, lockfile: str):
        self.lockfile = Path(lockfile)
        self.lock = threading.Lock()
    
    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire the file lock."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                # Try to create lock file exclusively
                if not self.lockfile.exists():
                    self.lockfile.write_text(str(os.getpid()))
                    return True
                else:
                    # Check if the lock is stale (older than 30 seconds)
                    if time.time() - self.lockfile.stat().st_mtime > 30:
                        self.lockfile.unlink()
                        continue
            except:
                pass
            time.sleep(0.1)
        return False
    
    def release(self):
        """Release the file lock."""
        try:
            if self.lockfile.exists():
                self.lockfile.unlink()
        except:
            pass
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, *args):
        self.release()


# ============================================================================
# COLORS AND ASCII ART
# ============================================================================

class Colors:
    RED = '\033[38;2;255;50;50m'
    ORANGE = '\033[38;2;255;150;0m'
    YELLOW = '\033[38;2;255;255;0m'
    GREEN = '\033[38;2;0;255;100m'
    CYAN = '\033[38;2;0;255;255m'
    BLUE = '\033[38;2;100;150;255m'
    MAGENTA = '\033[38;2;255;100;255m'
    PINK = '\033[38;2;255;150;200m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

LETTER_COLORS = [Colors.RED, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.MAGENTA]

ASCII_ART = r"""
██╗    ██╗██╗███╗   ███╗███████╗    ██████╗ ███████╗
██║    ██║██║████╗ ████║██╔════╝    ██╔══██╗██╔════╝
██║ █╗ ██║██║██╔████╔██║███████╗    ██║  ██║█████╗  
██║███╗██║██║██║╚██╔╝██║╚════██║    ██║  ██║██╔══╝  
╚███╔███╔╝██║██║ ╚═╝ ██║███████║    ██████╔╝███████╗
 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝╚══════╝    ╚═════╝ ╚══════╝
                                                    
███╗   ██╗██╗ ██████╗███████╗                       
████╗  ██║██║██╔════╝██╔════╝                       
██╔██╗ ██║██║██║     █████╗                         
██║╚██╗██║██║██║     ██╔══╝                         
██║ ╚████║██║╚██████╗███████╗                       
╚═╝  ╚═══╝╚═╝ ╚═════╝╚══════╝                       
"""

PROXY_FILE = "proxies.txt"
BYPASS_DUMP_FILE = "bypass_dump.txt" # was used during test for a better bypass usage
BYPASS_MODULE_FILE = "bypass.py"

# Global bypass module reference (loaded at startup if bypass.py exists with code)
bypass_module = None


def print_rainbow_art():
    lines = ASCII_ART.strip().split('\n')
    for line in lines:
        colored_line = ""
        line_len = len(line)
        for i, char in enumerate(line):
            # Gradient across each line
            ratio = i / max(line_len - 1, 1)
            color_idx = int(ratio * (len(LETTER_COLORS) - 1))
            color = LETTER_COLORS[color_idx]
            colored_line += f"{color}{char}"
        print(f"{colored_line}{Colors.RESET}")


def get_terminal_size():
    try:
        columns, rows = os.get_terminal_size()
        return rows, columns
    except:
        return 30, 100


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


HEADER_HEIGHT = 18

def print_fixed_header():
    clear_screen()
    print_rainbow_art()
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}          WHERE WIMS MEET - wind always win {Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print()


def setup_split_screen():
    print_fixed_header()
    rows, _ = get_terminal_size()
    print(f'\033[{HEADER_HEIGHT + 1};{rows}r', end='')
    print(f'\033[{HEADER_HEIGHT + 1};1H', end='')


def reset_scroll_region():
    rows, _ = get_terminal_size()
    print(f'\033[1;{rows}r', end='')


# Thread-safe logging
log_lock = threading.Lock()
def log_message(text: str, color: str = Colors.WHITE, thread_id: str = ""):
    with log_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[T{thread_id}]" if thread_id else ""
        print(f"  {Colors.GRAY}[{timestamp}]{Colors.RESET} {Colors.BLUE}{prefix}{Colors.RESET} {color}{text}{Colors.RESET}")


def loading_bar(label: str, duration: float, color: str = Colors.CYAN):
    """Animated loading bar for the init sequence."""
    bar_len = 30
    print(f"  {color}{label}{Colors.RESET}", end="", flush=True)
    for i in range(bar_len + 1):
        filled = "█" * i
        empty = "░" * (bar_len - i)
        pct = int(i / bar_len * 100)
        print(f"\r  {color}{label} [{filled}{empty}] {pct}%{Colors.RESET}", end="", flush=True)
        time.sleep(duration / bar_len)
    print()


# ============================================================================
# RANDOMIZED USER AGENT GENERATOR
# ============================================================================

def generate_random_user_agent() -> str:
    """Generate a completely random but realistic User-Agent string."""
    chrome_versions = [f"{random.randint(110, 125)}.0.{random.randint(1000, 9999)}.{random.randint(0, 200)}" for _ in range(1)]
    firefox_versions = [f"{random.randint(100, 125)}.0"]
    edge_versions = [f"{random.randint(110, 125)}.0.{random.randint(1000, 2500)}.{random.randint(0, 99)}"]
    safari_versions = [f"{random.randint(15, 17)}.{random.randint(0, 4)}"]
    
    os_strings = [
        "Windows NT 10.0; Win64; x64",
        "Windows NT 11.0; Win64; x64",
        f"Macintosh; Intel Mac OS X 10_{random.randint(13, 15)}_{random.randint(1, 7)}",
        f"Macintosh; Intel Mac OS X 11_{random.randint(0, 6)}_{random.randint(0, 5)}",
        "X11; Linux x86_64",
        "X11; Ubuntu; Linux x86_64",
    ]
    
    os_str = random.choice(os_strings)
    
    templates = [
        # Chrome
        f"Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_versions[0]} Safari/537.36",
        # Firefox
        f"Mozilla/5.0 ({os_str}; rv:{firefox_versions[0]}) Gecko/20100101 Firefox/{firefox_versions[0]}",
        # Edge
        f"Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_versions[0]} Safari/537.36 Edg/{edge_versions[0]}",
        # Safari (only with Mac OS)
        f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{random.randint(13, 15)}_{random.randint(1, 7)}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_versions[0]} Safari/605.1.15",
    ]
    
    return random.choice(templates)


# ============================================================================
# PROXY HANDLER
# ============================================================================

class ProxyHandler:
    """Manages proxy loading and rotation from proxies.txt."""
    
    def __init__(self, proxy_file: str = PROXY_FILE):
        self.proxy_file = Path(proxy_file)
        self.proxies: list = []
        self.current_index = 0
    
    def ensure_file_exists(self):
        """Create proxy file if it doesn't exist."""
        if not self.proxy_file.exists():
            self.proxy_file.write_text(
                "# Proxy list - one per line\n"
                "# Format: http://ip:port or socks5://ip:port\n"
                "# Leave empty to run without proxies\n",
                encoding='utf-8'
            )
    
    def load_proxies(self) -> list:
        """Load proxies from file, return list of proxy strings."""
        self.ensure_file_exists()
        
        self.proxies = []
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.proxies.append(line)
        except:
            pass
        
        return self.proxies
    
    def get_random_proxy(self) -> Optional[dict]:
        """Get a random proxy dict for requests, or None if no proxies."""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        if not proxy.startswith(('http://', 'https://', 'socks')):
            proxy = f"http://{proxy}"
        return {'http': proxy, 'https': proxy}
    
    def has_proxies(self) -> bool:
        return len(self.proxies) > 0


# Global proxy handler
proxy_handler = ProxyHandler()


# ============================================================================
# Private Proxy Rotator
# ============================================================================
# class PrivateProxyRotator:
#     """Rotates through authenticated SOCKS5 proxies with health checks."""
#     PROXY_API_ENDPOINT = "https://api."
#     HEALTH_CHECK_INTERVAL = 45  # seconds
#
#     def __init__(self, api_key: str, region: str = "eu-west"):
#         self.api_key = api_key
#         self.region = region
#         self._pool = []
#         self._dead = set()
#         self._lock = threading.Lock()
#         self._running = False
#
#     def _fetch_pool(self):
#         headers = {"X-Api-Key": self.api_key, "X-Region": self.region}
#         resp = requests.get(self.PROXY_API_ENDPOINT, headers=headers, timeout=10)
#         data = resp.json()
#         self._pool = [p for p in data.get("proxies", []) if p["status"] == "alive"]
#
#     def _health_worker(self):
#         while self._running:
#             with self._lock:
#                 alive = []
#                 for p in self._pool:
#                     try:
#                         r = requests.get("https://check.infra.in",
#                                          proxies={"https": p["uri"]}, timeout=5)
#                         if r.status_code == 200:
#                             alive.append(p)
#                         else:
#                             self._dead.add(p["uri"])
#                     except:
#                         self._dead.add(p["uri"])
#                 self._pool = alive
#             time.sleep(self.HEALTH_CHECK_INTERVAL)
#
#     def start(self):
#         self._fetch_pool()
#         self._running = True
#         threading.Thread(target=self._health_worker, daemon=True).start()
#
#     def get_proxy(self) -> dict:
#         with self._lock:
#             if not self._pool:
#                 return None
#             p = random.choice(self._pool)
#             return {"http": p["uri"], "https": p["uri"]}
#
#     def stop(self):
#         self._running = False


# ============================================================================
# BYPASS LOADER
# ============================================================================

def generate_memory_dump() -> str:
    """Generate fake memory dump content with random addresses."""
    lines = []
    lines.append(f"╔══════════════════════════════════════════════════════╗")
    lines.append(f"║  BYPASS MEMORY DUMP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}        ║")
    lines.append(f"╚══════════════════════════════════════════════════════╝")
    lines.append("")
    
    # Generate random memory regions
    sections = ["ntdll.dll", "kernel32.dll", "wims_hook.dll", "user32.dll", "advapi32.dll", "ws2_32.dll"]
    base_addr = random.randint(0x7FF000000000, 0x7FFFFFFFFFFF)
    
    for section in sections:
        addr = hex(base_addr + random.randint(0x1000, 0xFFFFF))
        size = hex(random.randint(0x100, 0xFFFF))
        lines.append(f"[{addr}] {section} +{size}")
        
        # Random hex dump lines
        for _ in range(random.randint(2, 5)):
            offset = hex(random.randint(0x00, 0xFFF))
            hex_data = ' '.join(f"{random.randint(0, 255):02X}" for _ in range(16))
            ascii_repr = ''.join(chr(random.randint(33, 126)) for _ in range(16))
            lines.append(f"  {offset:>8}  {hex_data}  |{ascii_repr}|")
        lines.append("")
    
    lines.append(f"Session Token: {uuid.uuid4().hex.upper()}")
    lines.append(f"Hook Entry: {hex(random.randint(0x10000, 0xFFFFF))}")
    lines.append(f"Process ID: {random.randint(1000, 65535)}")
    lines.append(f"Thread Count: {random.randint(1, 16)}")
    lines.append("")
    lines.append("Request was deleted or is uncallable")
    
    return '\n'.join(lines)


def create_memory_dump():
    """Create bypass dump txt file with memory addresses."""
    bypass_path = Path(BYPASS_DUMP_FILE)
    content = generate_memory_dump()
    bypass_path.write_text(content, encoding='utf-8')


def check_bypass_module() -> str:
    """
    Check if bypass.py exists and contains actual Python functions.
    Returns:
      'active'  - bypass.py exists and contains 'def ' (real code)
      'unknown' - bypass.py exists but no functions found (can't verify)
      'none'    - bypass.py does not exist
    """
    bypass_path = Path(BYPASS_MODULE_FILE)
    
    if not bypass_path.exists():
        return 'none'
    
    try:
        content = bypass_path.read_text(encoding='utf-8')
        # Check if the file has actual Python function definitions
        if re.search(r'^def\s+\w+', content, re.MULTILINE):
            return 'active'
        else:
            return 'unknown'
    except:
        return 'unknown'


def try_import_bypass():
    """Try to dynamically import bypass.py if it has valid code."""
    global bypass_module
    bypass_path = Path(BYPASS_MODULE_FILE)
    
    if not bypass_path.exists():
        return False
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("bypass", str(bypass_path.resolve()))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            bypass_module = mod
            return True
    except Exception:
        pass
    
    return False


# ============================================================================
# VPN Tunnel Manager (required private-vpn binary) ask DOMI for it
# ============================================================================
# class VPNTunnel:
#     """Manages WireGuard tunnel for IP masking during registration."""
#     WG_CONFIG_DIR = os.path.expanduser("~/.fallssdd/wg-configs")
#     fallssdd_VPN_BIN = "954DH894f9Gjuikilo5454Ffe.exe"  # shipped with full build
#
#     def __init__(self, config_name: str = "default"):
#         self.config_path = os.path.join(self.WG_CONFIG_DIR, f"{config_name}.conf")
#         self.process = None
#         self.connected = False
#         self.assigned_ip = None
#
#     def connect(self) -> bool:
#         if not os.path.exists(self.config_path):
#             return False
#         try:
#             self.process = subprocess.Popen(
#                 [self.fallssdd_VPN_BIN, "--config", self.config_path, "--daemon"],
#                 stdout=subprocess.PIPE, stderr=subprocess.PIPE
#             )
#             time.sleep(2)
#             out = subprocess.check_output([self.fallssdd_VPN_BIN, "--status"], text=True)
#             if "connected" in out.lower():
#                 self.connected = True
#                 match = re.search(r'assigned_ip=(\S+)', out)
#                 if match:
#                     self.assigned_ip = match.group(1)
#                 return True
#         except:
#             pass
#         return False
#
#     def disconnect(self):
#         if self.process:
#             self.process.terminate()
#             self.process.wait(timeout=5)
#         self.connected = False
#         self.assigned_ip = None
#
#     def rotate_ip(self) -> str:
#         self.disconnect()
#         time.sleep(1)
#         self.connect()
#         return self.assigned_ip

# ============================================================================
# Debug Packet Logger (DO NOT USE I TEST THINGS BTW)
# ============================================================================
# class DebugPacketLogger:
#     """Logs all HTTP requests/responses for debugging registration flow."""
#     LOG_DIR = "./debug_logs"
#
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.log_file = os.path.join(self.LOG_DIR, f"session_{session_id}.log")
#         os.makedirs(self.LOG_DIR, exist_ok=True)
#         self.entries = []
#
#     def log_request(self, method: str, url: str, headers: dict, body=None):
#         entry = {
#             "timestamp": datetime.now().isoformat(),
#             "direction": "REQUEST",
#             "method": method,
#             "url": url,
#             "headers": dict(headers),
#             "body": body[:2000] if body else None
#         }
#         self.entries.append(entry)
#         self._flush()
#
#     def log_response(self, status: int, headers: dict, body: str, elapsed_ms: float):
#         entry = {
#             "timestamp": datetime.now().isoformat(),
#             "direction": "RESPONSE",
#             "status": status,
#             "headers": dict(headers),
#             "body_preview": body[:5000],
#             "elapsed_ms": round(elapsed_ms, 2)
#         }
#         self.entries.append(entry)
#         self._flush()
#
#     def _flush(self):
#         with open(self.log_file, 'w', encoding='utf-8') as f:
#             json.dump(self.entries, f, indent=2, ensure_ascii=False)
#
#     def get_summary(self) -> dict:
#         total = len(self.entries)
#         requests_count = sum(1 for e in self.entries if e["direction"] == "REQUEST")
#         errors = sum(1 for e in self.entries if e.get("status", 200) >= 400)
#         return {"total": total, "requests": requests_count, "errors": errors}


# ============================================================================
# SYSTEM INFO GATHERING
# ============================================================================

def get_bios_info() -> dict:
    """Gather BIOS / system information using WMI (Windows)."""
    info = {
        'hostname': socket.gethostname(),
        'os': f"{platform.system()} {platform.release()} (Build {platform.version()})",
        'architecture': platform.machine(),
        'processor': platform.processor() or 'Unknown',
        'bios_vendor': 'Unknown',
        'bios_version': 'Unknown',
        'serial_number': 'Unknown',
        'mac_address': ':'.join(f'{(uuid.getnode() >> i) & 0xff:02x}' for i in range(0, 48, 8)),
    }
    
    # Try to get BIOS info via WMIC (Windows only)
    if os.name == 'nt':
        try:
            result = subprocess.run(
                ['wmic', 'bios', 'get', 'Manufacturer,SMBIOSBIOSVersion,SerialNumber', '/format:list'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line.startswith('Manufacturer='):
                    info['bios_vendor'] = line.split('=', 1)[1].strip() or 'Unknown'
                elif line.startswith('SMBIOSBIOSVersion='):
                    info['bios_version'] = line.split('=', 1)[1].strip() or 'Unknown'
                elif line.startswith('SerialNumber='):
                    info['serial_number'] = line.split('=', 1)[1].strip() or 'Unknown'
        except:
            pass
    
    return info


def get_public_ip() -> str:
    """Fetch public IP address."""
    try:
        resp = requests.get('https://api.ipify.org?format=text', timeout=5)
        return resp.text.strip()
    except:
        try:
            resp = requests.get('https://checkip.amazonaws.com', timeout=5)
            return resp.text.strip()
        except:
            return 'Unable to determine'


# ============================================================================
# STARTUP LOADING SEQUENCE (~10 seconds)
# ============================================================================

def _ask_user_confirmation():
    """Show BIOS/IP info and ask the user to confirm before proceeding."""
    print(f"  {Colors.BOLD}{Colors.YELLOW}[ SECURITY CHECK ]{Colors.RESET}")
    print(f"  {Colors.CYAN}{'─' * 45}{Colors.RESET}")
    
    # Gather system info
    print(f"    {Colors.DIM}Gathering system information...{Colors.RESET}")
    time.sleep(0.5)
    
    bios_info = get_bios_info()
    public_ip = get_public_ip()
    
    print(f"    {Colors.WHITE}Hostname    : {Colors.CYAN}{bios_info['hostname']}{Colors.RESET}")
    print(f"    {Colors.WHITE}OS          : {Colors.CYAN}{bios_info['os']}{Colors.RESET}")
    print(f"    {Colors.WHITE}Arch        : {Colors.CYAN}{bios_info['architecture']}{Colors.RESET}")
    print(f"    {Colors.WHITE}Processor   : {Colors.CYAN}{bios_info['processor']}{Colors.RESET}")
    print(f"    {Colors.WHITE}BIOS Vendor : {Colors.CYAN}{bios_info['bios_vendor']}{Colors.RESET}")
    print(f"    {Colors.WHITE}BIOS Version: {Colors.CYAN}{bios_info['bios_version']}{Colors.RESET}")
    print(f"    {Colors.WHITE}Serial No.  : {Colors.CYAN}{bios_info['serial_number']}{Colors.RESET}")
    print(f"    {Colors.WHITE}MAC Address : {Colors.CYAN}{bios_info['mac_address']}{Colors.RESET}")
    print(f"    {Colors.WHITE}Public IP   : {Colors.CYAN}{public_ip}{Colors.RESET}")
    print(f"  {Colors.CYAN}{'─' * 45}{Colors.RESET}")
    print()
    
    while True:
        answer = input(f"  {Colors.BOLD}{Colors.YELLOW}Are you sure you want to use the tool? (yes/no): {Colors.RESET}").strip().lower()
        if answer in ('yes', 'y', 'oui'):
            print(f"\n  {Colors.GREEN}✓ Access granted.{Colors.RESET}")
            time.sleep(0.5)
            return True
        elif answer in ('no', 'n', 'non'):
            print(f"\n  {Colors.RED}✗ Access denied. Exiting.{Colors.RESET}")
            time.sleep(1)
            sys.exit(0)
        else:
            print(f"  {Colors.RED}  Please type 'yes' or 'no'.{Colors.RESET}")


def startup_sequence():
    """
    Full initialization sequence with loading animations (~10 seconds).
    Steps:
      1. Init libraries
      2. Look for proxy file (create if missing), report status
      3. Load bypass - create txt with memory addresses, say "Deleted by XAXA"
         Then check for bypass.py module
      4. Warn if no proxy or no bypass (status report)
      5. If no bypass or no proxy, ask confirmation with BIOS/IP info
    """
    clear_screen()
    print_rainbow_art()
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}          WHERE WIMS MEET - wind always win {Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 55}{Colors.RESET}")
    print()
    
    # ── STEP 1: Init Libraries (~3s) ──
    print(f"  {Colors.BOLD}{Colors.YELLOW}[ INIT ]{Colors.RESET} {Colors.WHITE}Loading libraries...{Colors.RESET}")
    time.sleep(0.3)
    
    libs = [
        ("requests", "2.31.0"),
        ("beautifulsoup4", "4.12.3"),
        ("colorama", "0.4.6"),
        ("threading", "stdlib"),
        ("socket", "stdlib"),
        ("ctypes", "stdlib"),
        ("platform", "stdlib"),
    ]
    
    for lib_name, lib_ver in libs:
        fake_addr = hex(random.randint(0x7FF000000000, 0x7FFFFFFFFFFF))
        print(f"    {Colors.DIM}{Colors.GRAY}├─ {lib_name} ({lib_ver}) @ {fake_addr}{Colors.RESET}")
        time.sleep(random.uniform(0.2, 0.5))
    
    print(f"  {Colors.GREEN}  ✓ Libraries initialized{Colors.RESET}")
    print()
    time.sleep(0.3)
    
    # ── STEP 2: Proxy File (~2s) ──
    print(f"  {Colors.BOLD}{Colors.YELLOW}[ PROXY ]{Colors.RESET} {Colors.WHITE}Looking for proxy file...{Colors.RESET}")
    time.sleep(0.5)
    
    proxies = proxy_handler.load_proxies()
    has_proxy = proxy_handler.has_proxies()
    
    if has_proxy:
        print(f"  {Colors.GREEN}  ✓ Proxy loaded ({len(proxies)} proxies found){Colors.RESET}")
    else:
        # File created if missing, but it's empty — say nothing, move on
        pass
    
    print()
    time.sleep(0.5)
    
    # ── STEP 3: Load Bypass (~2.5s) ──
    print(f"  {Colors.BOLD}{Colors.YELLOW}[ BYPASS ]{Colors.RESET} {Colors.WHITE}Loading bypass...{Colors.RESET}")
    time.sleep(0.4)
    
    loading_bar("  Dumping memory", 1.5, Colors.MAGENTA)
    
    # Create the memory dump txt file
    create_memory_dump()
    
    # Show some fake addresses scrolling
    for _ in range(3):
        addr = hex(random.randint(0x10000, 0xFFFFF))
        print(f"    {Colors.DIM}{Colors.GRAY}├─ hook @ {addr}{Colors.RESET}")
        time.sleep(0.15)
    
    print(f"  {Colors.RED}  ✗ This was deleted or is uncallable{Colors.RESET}")
    time.sleep(0.3)
    
    # Check for actual bypass.py module
    bypass_state = check_bypass_module()  # 'active', 'unknown', or 'none'
    bypass_imported = False
    
    if bypass_state == 'active':
        print(f"    {Colors.DIM}{Colors.GRAY}├─ Importing bypass module...{Colors.RESET}")
        time.sleep(0.3)
        bypass_imported = try_import_bypass()
    
    print()
    time.sleep(0.3)
    
    # ── STEP 4: Status Warning ──
    print(f"  {Colors.BOLD}{Colors.YELLOW}[ STATUS ]{Colors.RESET}")
    print(f"  {Colors.CYAN}{'─' * 45}{Colors.RESET}")
    
    # Proxy status line
    if has_proxy:
        proxy_status = f"{Colors.GREEN}✓ ACTIVE ({len(proxies)} loaded){Colors.RESET}"
    else:
        proxy_status = f"{Colors.RED}✗ NO PROXY{Colors.RESET}"
    
    # Bypass status line
    if bypass_state == 'active' and bypass_imported:
        bypass_status = f"{Colors.GREEN}✓ LOADED{Colors.RESET}"
    elif bypass_state == 'active':
        bypass_status = f"{Colors.YELLOW}? FOUND (import failed){Colors.RESET}"
    elif bypass_state == 'unknown':
        bypass_status = f"{Colors.YELLOW}? UNKNOWN / MAYBE{Colors.RESET}"
    else:
        bypass_status = f"{Colors.RED}✗ NOT FOUND{Colors.RESET}"
    
    print(f"    Proxy  : {proxy_status}")
    print(f"    Bypass : {bypass_status}")
    print(f"  {Colors.CYAN}{'─' * 45}{Colors.RESET}")
    
    # Warnings
    needs_confirmation = False
    
    if not has_proxy and bypass_state == 'none':
        print(f"\n  {Colors.RED}{Colors.BOLD}⚠  WARNING: No proxy AND no bypass detected!{Colors.RESET}")
        print(f"  {Colors.RED}     Running unprotected. Proceed with caution.{Colors.RESET}")
        needs_confirmation = True
    elif not has_proxy:
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠  WARNING: No proxy detected!{Colors.RESET}")
        print(f"  {Colors.YELLOW}     Your IP is exposed. Add proxies to {PROXY_FILE}{Colors.RESET}")
        needs_confirmation = True
    elif bypass_state == 'none':
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠  WARNING: No bypass found!{Colors.RESET}")
        print(f"  {Colors.YELLOW}     bypass.py not detected.{Colors.RESET}")
        needs_confirmation = True
    elif bypass_state == 'unknown':
        print(f"\n  {Colors.YELLOW}{Colors.BOLD}⚠  WARNING: Bypass file found but no code detected.{Colors.RESET}")
        print(f"  {Colors.YELLOW}     Cannot verify bypass.py contents.{Colors.RESET}")
    
    print()
    time.sleep(0.5)
    
    # ── STEP 5: Ask confirmation if needed ──
    if needs_confirmation:
        _ask_user_confirmation()
    else:
        print(f"  {Colors.GREEN}✓ All checks passed. Access granted.{Colors.RESET}")
        time.sleep(0.5)
    
    print()
    time.sleep(0.3)


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    "base_url": "https://wims.univ-cotedazur.fr/wims/wims.cgi",
    "class_id": "8600283",  # Default class ID
    "class_password": "Gauss2025",
    "output_file": "comptes.json",
    "delay_min": 5,
    "delay_max": 15,
    "rate_limit_wait": 120,
    "max_retries": 3,
    "timeout": 30,
    "email_probability": 0.3,
}


# ============================================================================
# DATA GENERATION
# ============================================================================

FIRST_NAMES = [
    "Lucas", "Gabriel", "Louis", "Raphaël", "Jules", "Adam", "Arthur", "Hugo",
    "Nathan", "Théo", "Tom", "Noah", "Ethan", "Paul", "Sacha", "Léon",
    "Maël", "Gabin", "Mohamed", "Axel", "Mathis", "Maxime", "Alexandre", "Antoine",
    "Clément", "Romain", "Nicolas", "Pierre", "Thomas", "Victor", "Julien", "Baptiste",
    "Enzo", "Nolan", "Samuel", "Léo", "Mathéo", "Timéo", "Evan", "Liam",
    "Aaron", "Eden", "Yanis", "Eliott", "Rayan", "Malo", "Noé", "Robin",
    "Adrien", "Martin", "Simon", "Valentin", "Quentin", "Benjamin", "Maxence", "Bastien",
    "Dylan", "Kylian", "Loïc", "Florian", "Alexis", "Corentin", "Mathieu", "Rémi",
    "Guillaume", "Jérémie", "Kevin", "Olivier", "Damien", "Fabien", "Sébastien", "Laurent",
    "Vincent", "François", "Christophe", "Philippe", "Stéphane", "Patrick", "Marc", "David",
    "Emma", "Jade", "Louise", "Alice", "Chloé", "Léa", "Manon", "Inès",
    "Camille", "Lina", "Zoé", "Léonie", "Anna", "Rose", "Eva", "Julia",
    "Lou", "Nina", "Sarah", "Mia", "Lola", "Lucie", "Clara", "Margot",
    "Marie", "Jeanne", "Charlotte", "Romane", "Juliette", "Agathe", "Elena", "Victoire",
    "Célia", "Anaïs", "Océane", "Mathilde", "Pauline", "Laura", "Émilie", "Julie",
    "Sophie", "Caroline", "Aurélie", "Mélanie", "Marine", "Elodie", "Laetitia", "Sandra",
    "Ambre", "Clémence", "Elisa", "Maëlys", "Capucine", "Margaux", "Nour", "Lena",
]

LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
    "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
    "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "Andre", "Lefevre",
    "Mercier", "Dupont", "Lambert", "Bonnet", "Francois", "Martinez", "Legrand", "Garnier",
    "Faure", "Rousseau", "Blanc", "Guerin", "Muller", "Henry", "Roussel", "Nicolas",
    "Perrin", "Morin", "Mathieu", "Clement", "Gauthier", "Dumont", "Lopez", "Fontaine",
    "Chevalier", "Robin", "Masson", "Sanchez", "Gerard", "Nguyen", "Boyer", "Denis",
    "Lemaire", "Duval", "Joly", "Gautier", "Roger", "Roche", "Roy", "Noel",
    "Meyer", "Lucas", "Meunier", "Jean", "Perez", "Marchand", "Dufour", "Blanchard",
    "Marie", "Barbier", "Brun", "Dumas", "Brunet", "Schmitt", "Leroux", "Colin",
    "Fernandez", "Pierre", "Renaud", "Arnaud", "Rolland", "Caron", "Aubert", "Giraud",
    "Leclerc", "Vidal", "Bourgeois", "Renard", "Lacroix", "Olivier", "Philippe", "Picard",
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.fr", "outlook.com", "hotmail.fr", "orange.fr", "free.fr"]


def generate_random_string(length: int, chars: str = string.ascii_lowercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(length))


def generate_login(first_name: str, last_name: str, existing_logins: set) -> str:
    import unicodedata
    def normalize(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    
    base = (normalize(first_name[:3]) + normalize(last_name[:3])).lower()
    base = re.sub(r'[^a-z0-9]', '', base)
    
    for _ in range(100):
        suffix = generate_random_string(random.randint(4, 6), string.digits)
        login = f"{base}{suffix}"
        if len(login) >= 4 and len(login) <= 16 and login not in existing_logins:
            return login
    
    return generate_random_string(random.randint(8, 12))


def generate_password() -> str:
    return generate_random_string(random.randint(8, 12), string.ascii_letters + string.digits)


def generate_email(first_name: str, last_name: str) -> str:
    import unicodedata
    def normalize(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    domain = random.choice(EMAIL_DOMAINS)
    suffix = generate_random_string(4, string.digits)
    return f"{normalize(first_name).lower()}.{normalize(last_name).lower()}{suffix}@{domain}"


# ============================================================================
# ACCOUNT DATA - THREAD-SAFE
# ============================================================================

@dataclass
class Account:
    created_at: str
    last_name: str
    first_name: str
    login: str
    password: str
    email: str
    class_id: str


class ThreadSafeAccountLogger:
    """Thread-safe account logger with file locking."""
    
    def __init__(self, output_file: str):
        self.output_file = Path(output_file)
        self.lock_file = self.output_file.with_suffix('.lock')
        self.file_lock = FileLock(str(self.lock_file))
        self.thread_lock = threading.Lock()
        self.accounts: list = []
        self.local_logins: set = set()
        self._load_existing()
    
    def _load_existing(self):
        with self.file_lock:
            if self.output_file.exists():
                try:
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        self.accounts = json.load(f)
                except (json.JSONDecodeError, IOError):
                    self.accounts = []
    
    def get_existing_logins(self) -> set:
        with self.thread_lock:
            # Reload from file to get latest
            if self.output_file.exists():
                try:
                    with open(self.output_file, 'r', encoding='utf-8') as f:
                        file_accounts = json.load(f)
                        file_logins = {acc.get('login', '') for acc in file_accounts}
                except:
                    file_logins = set()
            else:
                file_logins = set()
            return file_logins | self.local_logins
    
    def reserve_login(self, login: str):
        """Reserve a login to prevent duplicates."""
        with self.thread_lock:
            self.local_logins.add(login)
    
    def add_account(self, account: Account):
        """Add account with file locking for safety."""
        with self.thread_lock:
            # Acquire file lock for cross-process safety
            with self.file_lock:
                # Reload file to get latest
                if self.output_file.exists():
                    try:
                        with open(self.output_file, 'r', encoding='utf-8') as f:
                            self.accounts = json.load(f)
                    except:
                        pass
                
                # Add new account
                self.accounts.append(asdict(account))
                
                # Write back
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    json.dump(self.accounts, f, indent=2, ensure_ascii=False)


# ============================================================================
# WIMS REGISTRATOR
# ============================================================================

class RateLimitError(Exception):
    pass


class RegistrationError(Exception):
    pass


class WIMSRegistrator:
    RATE_LIMIT_PATTERNS = [
        "too many requests", "rate limit", "try again later", "temporarily blocked",
        "trop de requêtes", "réessayez plus tard", "accès refusé", "access denied", "blocked",
        "server busy", "serveur occupé"
    ]
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        # Use a fully randomized user agent each time
        self.user_agent = generate_random_user_agent()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        })
        
        # Apply proxy if available
        proxy = proxy_handler.get_random_proxy()
        if proxy:
            self.session.proxies.update(proxy)

    def _get_start_url(self) -> str:
        """Construct the start URL dynamically from class ID."""
        base = self.config['base_url']
        cls_id = self.config.get('class_id', '8600283')
        return f"{base}?module=adm/class/classes&lang=fr&type=authparticipant&class={cls_id}&subclass=yes"
    
    def _check_rate_limit(self, response) -> bool:
        if response.status_code == 450:
            return True  # Treat 450 Blocked as rate limit
        
        content_lower = response.text.lower()
        if "quota" in content_lower or "please wait" in content_lower:
            return True
            
        for pattern in self.RATE_LIMIT_PATTERNS:
            if pattern in content_lower:
                return True
        return response.status_code in [429, 503, 403]
    
    def _random_delay(self):
        """Short delay between steps to mimic human behavior."""
        time.sleep(random.uniform(0.5, 2.0))
    
    def _get(self, url: str):
        self._random_delay()
        response = self.session.get(url, timeout=self.config['timeout'])
        if self._check_rate_limit(response):
            raise RateLimitError(f"Rate limit detected (HTTP {response.status_code})")
        return response
    
    def _post(self, url: str, data: dict):
        self._random_delay()
        response = self.session.post(url, data=data, timeout=self.config['timeout'])
        if self._check_rate_limit(response):
            raise RateLimitError(f"Rate limit detected (HTTP {response.status_code})")
        return response
    
    def _extract_session_base(self, html: str) -> Optional[str]:
        match = re.search(r'session=([A-Z0-9]+)', html)
        return match.group(1) if match else None
    
    def _extract_register_url(self, html: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', class_='wims_button'):
            if "S'inscrire" in a.get_text() or "reguser" in a.get('href', ''):
                return a.get('href')
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'reguser' in href and 'class=' in href:
                return href
        return None
    
    def register_account(self, first_name: str, last_name: str, login: str, 
                         password: str, email: str = "") -> bool:
        base_url = self.config['base_url']
        class_password = self.config['class_password']
        
        # Run bypass module if it was loaded
        if bypass_module is not None and hasattr(bypass_module, 'bypass'):
            try:
                bypass_module.bypass(self.session)
            except Exception:
                pass  # Bypass is optional, don't fail if it errors
        
        response = self._get(self._get_start_url())
        if response.status_code != 200:
            raise RegistrationError(f"HTTP {response.status_code}")
        
        session_base = self._extract_session_base(response.text)
        if not session_base:
            raise RegistrationError("No session ID")
        
        register_url = self._extract_register_url(response.text)
        if not register_url:
            raise RegistrationError("No register button")
        
        response = self._get(register_url)
        new_session = self._extract_session_base(response.text)
        if new_session:
            session_base = new_session
        
        data = {
            'session': session_base, 'lang': 'fr', 'cmd': 'reply',
            'module': 'adm/class/reguser', 'step': '1', 'classpass': class_password,
        }
        response = self._post(base_url, data)
        if "incorrect" in response.text.lower():
            raise RegistrationError("Wrong password")
        
        data = {
            'session': session_base, 'lang': 'fr', 'cmd': 'reply',
            'module': 'adm/class/reguser', 'step': '2',
            'lastn': last_name, 'firstn': first_name,
            'login': login, 'pass': password, 'email': email, 'agreecgu': 'yes',
        }
        response = self._post(base_url, data)
        if "existe déjà" in response.text or "already exists" in response.text.lower():
            raise RegistrationError(f"Login exists: {login}")
        
        data = {
            'session': session_base, 'lang': 'fr', 'cmd': 'reply',
            'module': 'adm/class/reguser', 'step': '3', 'pass2': password,
        }
        self._post(base_url, data)
        
        return True
    
    def close(self):
        self.session.close()


# ============================================================================
# Session Fingerprint Spoofer (randomize TLS/JA3)
# ============================================================================
# class FingerprintSpoofer:
#     """Spoofs TLS fingerprint and browser characteristics per session."""
#     JA3_HASHES = [
#         "771,4865-4866-4867-49195-49199,0-23-65281-10-11-35-16-5-13-18-51-45-43",
#         "771,4865-4867-4866-49196-49200,0-23-65281-10-11-35-16-5-13-18-51-45-43-21",
#         "771,4865-4866-4867-49195-49199-52393,0-23-65281-10-11-35-16-5-34-51-43-13",
#     ]
#
#     CANVAS_HASHES = [
#         "a3f8c2e1", "b7d4f9a0", "c1e5b3d8", "d9a2c7f4", "e6f1d0b5",
#         "f4c8a3e2", "0b7d5f9a", "1c6e4b3d", "2d9a8c7f", "3e1f0d5b",
#     ]
#
#     WEBGL_RENDERERS = [
#         "ANGLE (NVIDIA GeForce GTX 1060)",
#         "ANGLE (Intel HD Graphics 630)",
#         "ANGLE (AMD Radeon RX 580)",
#         "ANGLE (NVIDIA GeForce RTX 3060)",
#         "ANGLE (Intel UHD Graphics 620)",
#     ]
#
#     def __init__(self):
#         self.ja3 = random.choice(self.JA3_HASHES)
#         self.canvas_hash = random.choice(self.CANVAS_HASHES)
#         self.webgl_renderer = random.choice(self.WEBGL_RENDERERS)
#         self.screen_res = random.choice([(1920, 1080), (2560, 1440), (1366, 768), (3840, 2160)])
#         self.timezone_offset = random.choice([-60, 0, 60, 120, -300, -420])
#         self.language = random.choice(["fr-FR", "en-US", "en-GB", "de-DE", "es-ES"])
#
#     def apply_to_session(self, session: requests.Session):
#         session.headers.update({
#             "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
#             "Accept-Language": f"{self.language},{self.language.split('-')[0]};q=0.9,en;q=0.7",
#             "Sec-CH-UA-Platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
#         })
#
#     def get_fingerprint_dict(self) -> dict:
#         return {
#             "ja3": self.ja3, "canvas": self.canvas_hash,
#             "webgl": self.webgl_renderer, "screen": self.screen_res,
#             "tz_offset": self.timezone_offset, "lang": self.language
#         }

# ============================================================================
# Request Interceptor / Rate Limit Evasion
# ============================================================================
# class RequestInterceptor:
#     """Intercepts outgoing requests to apply evasion techniques."""
#
#     def __init__(self, vpn_tunnel=None, fingerprint_spoofer=None):
#         self.vpn = vpn_tunnel
#         self.spoofer = fingerprint_spoofer
#         self.request_count = 0
#         self.rotate_every = random.randint(3, 7)  # rotate IP every N requests
#
#     def pre_request(self, session: requests.Session):
#         self.request_count += 1
#         if self.spoofer:
#             self.spoofer.apply_to_session(session)
#         if self.vpn and self.vpn.connected and self.request_count % self.rotate_every == 0:
#             new_ip = self.vpn.rotate_ip()
#             if new_ip:
#                 log_message(f"IP rotated -> {new_ip}", Colors.CYAN)
#
#     def post_request(self, response, session: requests.Session):
#         if response.status_code in [429, 503]:
#             backoff = random.uniform(30, 90)
#             log_message(f"Interceptor: backing off {backoff:.0f}s", Colors.YELLOW)
#             time.sleep(backoff)
#             if self.vpn and self.vpn.connected:
#                 self.vpn.rotate_ip()
#             return True  # signal retry
#         return False


# ============================================================================
# NORMAL MODE
# ============================================================================

def create_accounts_loop(config: dict, count: int = 0, loop: bool = False):
    """Create accounts with auto-retry on rate limit."""
    logger = ThreadSafeAccountLogger(config['output_file'])
    created_count = 0
    target_count = float('inf') if loop else count
    
    setup_split_screen()
    
    log_message(f"📁 Output: {config['output_file']}", Colors.CYAN)
    log_message(f"⏱️  Delay: {config['delay_min']}-{config['delay_max']}s", Colors.CYAN)
    log_message(f"📊 Existing accounts: {len(logger.accounts)}", Colors.CYAN)
    
    if proxy_handler.has_proxies():
        log_message(f"🔒 Proxy: ACTIVE ({len(proxy_handler.proxies)} loaded)", Colors.GREEN)
    else:
        log_message(f"🔓 Proxy: NONE (direct connection)", Colors.YELLOW)
    
    if loop:
        log_message(f"🔄 Mode: INFINITE LOOP (Ctrl+C to stop)", Colors.GREEN)
    else:
        log_message(f"🎯 Target: {count} accounts", Colors.GREEN)
    
    log_message("─" * 70, Colors.GRAY)
    
    try:
        while created_count < target_count:
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            login = generate_login(first_name, last_name, logger.get_existing_logins())
            password = generate_password()
            
            email = ""
            if random.random() < config.get('email_probability', 0.3):
                email = generate_email(first_name, last_name)
            
            log_message(f"Creating: {first_name} {last_name} ({login})", Colors.WHITE)
            
            registrator = WIMSRegistrator(config)
            try:
                registrator.register_account(first_name, last_name, login, password, email)
                
                account = Account(
                    created_at=datetime.now().isoformat(),
                    last_name=last_name,
                    first_name=first_name,
                    login=login,
                    password=password,
                    email=email,
                    class_id=config.get('class_id', "8600283")
                )
                logger.add_account(account)
                created_count += 1
                
                log_message(f"✅ SUCCESS! {login} | {password}", Colors.GREEN)
                
            except RateLimitError:
                log_message(f"🚫 RATE LIMITED!", Colors.RED)
                
                if loop:
                    wait_time = config.get('rate_limit_wait', 120)
                    log_message(f"⏳ Waiting {wait_time}s...", Colors.YELLOW)
                    
                    for remaining in range(wait_time, 0, -10):
                        time.sleep(min(10, remaining))
                    
                    log_message(f"🔄 Resuming...", Colors.GREEN)
                    continue
                else:
                    break
                
            except RegistrationError as e:
                log_message(f"❌ Error: {e}", Colors.RED)
                
            except requests.RequestException as e:
                log_message(f"🌐 Network error: {e}", Colors.RED)
            
            finally:
                registrator.close()
            
            if created_count < target_count:
                delay = random.uniform(config['delay_min'], config['delay_max'])
                time.sleep(delay)
    
    except KeyboardInterrupt:
        log_message("🛑 Stopped by user (Ctrl+C)", Colors.YELLOW)
    
    finally:
        reset_scroll_region()
    
    log_message("─" * 70, Colors.GRAY)
    log_message(f"📊 Session created: {created_count}", Colors.GREEN)
    log_message(f"📁 Total in file: {len(logger.accounts)}", Colors.GREEN)
    input(f"\n  {Colors.CYAN}Press Enter to continue...{Colors.RESET}")


# ============================================================================
# INTERACTIVE MENU
# ============================================================================

def print_menu():
    print(f"\n  {Colors.BOLD}MAIN MENU:{Colors.RESET}")
    print(f"  {Colors.CYAN}─────────────────────────────────────{Colors.RESET}")
    print(f"  {Colors.GREEN}[1]{Colors.RESET} Create ONE account")
    print(f"  {Colors.GREEN}[2]{Colors.RESET} Create MULTIPLE accounts")
    print(f"  {Colors.GREEN}[3]{Colors.RESET} Infinite loop")
    print(f"  {Colors.CYAN}[4]{Colors.RESET} View created accounts")
    print(f"  {Colors.CYAN}[5]{Colors.RESET} Settings")
    print(f"  {Colors.RED}[0]{Colors.RESET} Exit")
    print()


def get_input(prompt: str, default: str = "") -> str:
    if default:
        result = input(f"  {prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"  {prompt}: ").strip()


def view_accounts(config: dict):
    print_fixed_header()
    output_file = Path(config['output_file'])
    
    if not output_file.exists():
        print(f"  {Colors.YELLOW}No accounts file found.{Colors.RESET}")
        input(f"\n  {Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return
    
    with open(output_file, 'r', encoding='utf-8') as f:
        accounts = json.load(f)
    
    if not accounts:
        print(f"  {Colors.YELLOW}No accounts created yet.{Colors.RESET}")
        input(f"\n  {Colors.CYAN}Press Enter to continue...{Colors.RESET}")
        return
    
    print(f"  {Colors.BOLD}CREATED ACCOUNTS ({len(accounts)} total):{Colors.RESET}")
    print(f"  {Colors.CYAN}{'─' * 70}{Colors.RESET}")
    print(f"  {Colors.BOLD}{'#':<4} {'Name':<22} {'Login':<14} {'Password':<12} {'Date':<12}{Colors.RESET}")
    print(f"  {Colors.CYAN}{'─' * 70}{Colors.RESET}")
    
    for i, acc in enumerate(accounts[-15:], 1):
        name = f"{acc.get('first_name', '')} {acc.get('last_name', '')}"[:21]
        date = acc.get('created_at', '')[:10]
        print(f"  {i:<4} {name:<22} {acc.get('login', ''):<14} {acc.get('password', ''):<12} {date}")
    
    if len(accounts) > 15:
        print(f"\n  {Colors.YELLOW}... and {len(accounts) - 15} more (showing last 15){Colors.RESET}")
    
    input(f"\n  {Colors.CYAN}Press Enter to continue...{Colors.RESET}")


def settings_menu(config: dict) -> dict:
    while True:
        print_fixed_header()
        print(f"  {Colors.BOLD}SETTINGS:{Colors.RESET}")
        print(f"  {Colors.CYAN}─────────────────────────────────{Colors.RESET}")
        print(f"  {Colors.GREEN}[1]{Colors.RESET} Delay: {config['delay_min']}-{config['delay_max']} seconds")
        print(f"  {Colors.GREEN}[2]{Colors.RESET} Rate limit wait: {config['rate_limit_wait']} seconds")
        print(f"  {Colors.GREEN}[3]{Colors.RESET} Email probability: {int(config['email_probability'] * 100)}%")
        print(f"  {Colors.GREEN}[4]{Colors.RESET} Output file: {config['output_file']}")
        print(f"  {Colors.GREEN}[5]{Colors.RESET} Class password: {config['class_password']}")
        print(f"  {Colors.GREEN}[6]{Colors.RESET} Class ID: {config.get('class_id', '8600283')}")
        print(f"  {Colors.RED}[0]{Colors.RESET} Back to main menu")
        
        print()
        choice = get_input("Select option", "0")
        
        if choice == "0":
            break
        elif choice == "1":
            try:
                min_d = int(get_input("Min delay (sec)", str(config['delay_min'])))
                max_d = int(get_input("Max delay (sec)", str(config['delay_max'])))
                if min_d > 0 and max_d >= min_d:
                    config['delay_min'] = min_d
                    config['delay_max'] = max_d
                    print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            except ValueError:
                print(f"  {Colors.RED}❌ Invalid!{Colors.RESET}")
            time.sleep(1)
        elif choice == "2":
            try:
                wait = int(get_input("Rate limit wait (sec)", str(config['rate_limit_wait'])))
                if wait >= 30:
                    config['rate_limit_wait'] = wait
                    print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            except ValueError:
                print(f"  {Colors.RED}❌ Invalid!{Colors.RESET}")
            time.sleep(1)
        elif choice == "3":
            try:
                prob = int(get_input("Email probability (0-100)", str(int(config['email_probability'] * 100))))
                if 0 <= prob <= 100:
                    config['email_probability'] = prob / 100
                    print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            except ValueError:
                print(f"  {Colors.RED}❌ Invalid!{Colors.RESET}")
            time.sleep(1)
        elif choice == "4":
            filename = get_input("Output file", config['output_file'])
            if filename:
                config['output_file'] = filename
                print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            time.sleep(1)
        elif choice == "5":
            pwd = get_input("Class password", config['class_password'])
            if pwd:
                config['class_password'] = pwd
                print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            time.sleep(1)
        elif choice == "6":
            cls = get_input("Class ID", config.get('class_id', '8600283'))
            if cls and cls.isdigit():
                config['class_id'] = cls
                print(f"  {Colors.GREEN}✅ Updated!{Colors.RESET}")
            else:
                print(f"  {Colors.RED}❌ Invalid Class ID!{Colors.RESET}")
            time.sleep(1)
    
    return config


def interactive_mode():
    config = DEFAULT_CONFIG.copy()
    
    while True:
        print_fixed_header()
        print_menu()
        
        choice = get_input("Select option", "1")
        
        if choice == "0":
            print(f"\n  {Colors.CYAN}Goodbye! 👋{Colors.RESET}")
            time.sleep(1)
            break
        elif choice == "1":
            create_accounts_loop(config, count=1)
        elif choice == "2":
            try:
                count = int(get_input("How many accounts?", "5"))
                if count > 0:
                    create_accounts_loop(config, count=count)
            except ValueError:
                print(f"  {Colors.RED}❌ Invalid number!{Colors.RESET}")
                time.sleep(1)
        elif choice == "3":
            create_accounts_loop(config, count=0, loop=True)
        elif choice == "4":
            view_accounts(config)
        elif choice == "5":
            config = settings_menu(config)


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="WHERE WIMS MEET - wind always win")
    parser.add_argument('--launcher-auth', type=str, help='Security token', default=None)
    parser.add_argument('--count', '-n', type=int, default=1)
    parser.add_argument('--loop', action='store_true')
    parser.add_argument('--delay-min', type=int, default=5)
    parser.add_argument('--delay-max', type=int, default=15)
    parser.add_argument('--output', '-o', type=str, default="comptes.json")
    parser.add_argument('--interactive', '-i', action='store_true')
    
    args, unknown = parser.parse_known_args()
    
    # Security check - validate launcher token ALWAYS
    if args.launcher_auth != REQUIRED_TOKEN:
        print("ACCESS DENIED: Please run from main version")
        try:
            ctypes.windll.user32.MessageBoxW(0, "Access Denied!\n\nPlease launch this application from main version", "FORWARD Security", 0x10)
        except:
            pass
        sys.exit(1)
    
    # SECURITY SYSTEM
    # async(unknown) # dangerous check... deleted.

    # Run the startup loading sequence (~10 seconds)
    startup_sequence()
    
    # If no other args or interactive flag, run interactive mode
    if args.interactive or (not args.loop and args.count == 1):
        interactive_mode()
        return
    
    config = DEFAULT_CONFIG.copy()
    config['delay_min'] = args.delay_min
    config['delay_max'] = args.delay_max
    config['output_file'] = args.output
    
    create_accounts_loop(config, count=args.count, loop=args.loop)


if __name__ == "__main__":
    main()
