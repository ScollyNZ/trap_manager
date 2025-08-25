import os, sys, socket, ipaddress, configparser, subprocess
from SCons.Script import DefaultEnvironment

# Try requests; fall back to curl if needed
try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False

env = DefaultEnvironment()
FIRMWARE = env.subst("$BUILD_DIR/${PROGNAME}.bin")
project_dir = env["PROJECT_DIR"]
ini_path = os.path.join(project_dir, "platformio.ini")

cfg = configparser.ConfigParser()
if not cfg.read(ini_path):
    raise FileNotFoundError(f"[CustomUploader] Cannot read {ini_path}")

section = f"env:{env['PIOENV']}"

def opt(name, default=None):
    return cfg.get(section, name, fallback=str(env.get(name.upper(), default)))

ESP_HOST     = opt("upload_port", "")
ESP_USER     = opt("upload_user", "")
ESP_PASS     = opt("upload_password", "")
ESP_SCHEME   = opt("upload_scheme", "http")
ESP_PATH     = opt("upload_path", "/update")
TIMEOUT_S    = int(opt("upload_timeout", "60"))
VERIFY_SSL   = opt("upload_verify_ssl", "true").lower() not in ("0","false","no")
# NEW: bind uploads to this local source IP (your Mac’s LAN IP), optional
HOST_IP      = opt("upload_host_ip", "")   # e.g. 192.168.1.100
CURL_PATH    = opt("curl_path", "curl")

def to_ipv4(host: str) -> str:
    # If already an IP, return it
    try:
        ip = ipaddress.ip_address(host)
        return host
    except ValueError:
        pass
    # Resolve hostname to IPv4
    infos = socket.getaddrinfo(host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
    return infos[0][4][0] if infos else host

def try_requests(url: str, firmware: str, auth_tuple, timeout: int) -> None:
    # Use a session that ignores env proxies
    s = requests.Session()
    s.trust_env = False
    s.proxies = {"http": None, "https": None}

    # If a source IP is provided, mount an adapter that binds source_address
    if HOST_IP:
        from urllib3 import PoolManager
        from requests.adapters import HTTPAdapter

        class SourceAddrAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs["source_address"] = (HOST_IP, 0)
                self.poolmanager = PoolManager(*args, **kwargs)

        s.mount("http://", SourceAddrAdapter())
        s.mount("https://", SourceAddrAdapter())

    with open(firmware, "rb") as f:
        files = {"firmware": (os.path.basename(firmware), f, "application/octet-stream")}
        r = s.post(url, files=files, auth=auth_tuple, timeout=timeout, verify=VERIFY_SSL)
    if not (200 <= r.status_code < 300):
        raise RuntimeError(f"HTTP {r.status_code} — {r.text.strip()}")

def try_curl(url: str, firmware: str, auth_tuple, timeout: int) -> None:
    cmd = [CURL_PATH, "--fail", "--show-error", "--progress-bar",
           "--max-time", str(timeout),
           "-F", f"\"firmware=@{firmware}\""]
    if auth_tuple and (auth_tuple[0] or auth_tuple[1]):
        cmd += ["-u", f"{auth_tuple[0]}:{auth_tuple[1]}"]
    # Bind to source IP if provided
    if HOST_IP:
        cmd += ["--interface", HOST_IP]
    cmd += [url]
    print("[CustomUploader] curl:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("curl uploader failed")

def before_upload(source, target, env):
    if not ESP_HOST:
        raise Exception("[CustomUploader] 'upload_port' (device IP/hostname) is not set")
    if not os.path.exists(FIRMWARE):
        raise FileNotFoundError(f"[CustomUploader] Firmware not found: {FIRMWARE}")

    host = to_ipv4(ESP_HOST)
    url  = f"{ESP_SCHEME}://{host}{ESP_PATH}"
    auth = (ESP_USER, ESP_PASS) if (ESP_USER or ESP_PASS) else None
    print(f"[CustomUploader] Uploading {FIRMWARE} → {url} (timeout={TIMEOUT_S}s)"
          + (f" via source {HOST_IP}" if HOST_IP else ""))

    # First try requests (if available), else directly curl
    if HAVE_REQUESTS:
        try:
            try_requests(url, FIRMWARE, auth, TIMEOUT_S)
            print("[CustomUploader] Upload OK (requests)")
            return
        except Exception as e:
            print(f"[CustomUploader] requests failed: {e} — falling back to curl...")
    # Fallback: curl (since you said curl works for you)
    try:
        try_curl(url, FIRMWARE, auth, TIMEOUT_S)
        print("[CustomUploader] Upload OK (curl)")
    except Exception as e:
        raise Exception(f"[CustomUploader] Upload failed (curl): {e}")

env.AddPreAction("upload", before_upload)
