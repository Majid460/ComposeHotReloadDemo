#!/usr/bin/env python3
"""
Minimal MCP (Model Context Protocol) stdio client for Compose Hot Reload's
hotMcpServer gradle task.

Why this exists: this script is being run by an AI agent (Claude) that is
NOT the Claude Code CLI reading .mcp.json at startup -- it's driving this
project from a separate harness that can't dynamically attach a new MCP
server mid-session. So instead of relying on built-in MCP client wiring,
this script IS the MCP client: it launches the real
`./gradlew --no-daemon --quiet --console=plain hotMcpServer` process,
performs the real MCP initialize handshake, and relays tool calls dropped
into mcp_queue/ as JSON files, writing responses back as JSON files
(decoding any base64 image content into article-assets/*.png).

This is genuine protocol-level interaction with the real server, just
driven by a hand-rolled client instead of a framework's built-in one.
"""
import base64
import json
import os
import subprocess
import sys
import threading
import time

PROJ_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_DIR = os.path.join(PROJ_DIR, "mcp_queue")
ASSETS_DIR = os.path.join(PROJ_DIR, "article-assets")
LOG_PATH = os.path.join(PROJ_DIR, "mcp_daemon.log")
STDERR_LOG = os.path.join(PROJ_DIR, "hotmcp_stderr.log")

os.makedirs(QUEUE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

logf = open(LOG_PATH, "a", buffering=1)


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    logf.write(line + "\n")


log("=== mcp_daemon starting ===")
log(f"cwd={PROJ_DIR}")

stderr_file = open(STDERR_LOG, "ab", buffering=0)

proc = subprocess.Popen(
    ["./gradlew", "--no-daemon", "--quiet", "--console=plain", "hotMcpServer"],
    cwd=PROJ_DIR,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=stderr_file,
    bufsize=0,
)

pending = {}
pending_lock = threading.Lock()
stray_lines = []


def reader_thread():
    while True:
        raw = proc.stdout.readline()
        if not raw:
            log("hotMcpServer stdout closed (process likely exited)")
            return
        try:
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
        except Exception as e:
            log(f"decode error: {e}")
            continue
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            # This is exactly the known stray-stdout-line failure mode
            # (e.g. kotlin-logging init banner). Log it, don't crash.
            log(f"STRAY NON-JSON STDOUT LINE (skipped): {line!r}")
            stray_lines.append(line)
            continue
        msg_id = msg.get("id")
        if msg_id is not None:
            with pending_lock:
                pending[str(msg_id)] = msg
        else:
            log(f"NOTIFICATION from server: {json.dumps(msg)[:500]}")


t = threading.Thread(target=reader_thread, daemon=True)
t.start()


def send(msg):
    data = (json.dumps(msg) + "\n").encode("utf-8")
    proc.stdin.write(data)
    proc.stdin.flush()


def wait_for(id_str, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with pending_lock:
            if id_str in pending:
                return pending.pop(id_str)
        time.sleep(0.1)
    return None


# --- MCP initialize handshake ---
log("Sending initialize request...")
send({
    "jsonrpc": "2.0",
    "id": "init-1",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "proandroiddev-manual-mcp-client", "version": "0.1.0"},
    },
})
init_resp = wait_for("init-1", timeout=120)
log(f"initialize response: {json.dumps(init_resp)[:1000]}")

send({"jsonrpc": "2.0", "method": "notifications/initialized"})
log("Sent notifications/initialized")

# --- list tools once at startup, save to file for inspection ---
send({"jsonrpc": "2.0", "id": "list-tools-1", "method": "tools/list"})
tools_resp = wait_for("list-tools-1", timeout=60)
with open(os.path.join(PROJ_DIR, "mcp_tools_list.json"), "w") as f:
    json.dump(tools_resp, f, indent=2)
log(f"tools/list saved to mcp_tools_list.json. Stray lines so far: {len(stray_lines)}")

with open(os.path.join(PROJ_DIR, "mcp_stray_lines.json"), "w") as f:
    json.dump(stray_lines, f, indent=2)

log("=== daemon ready, watching mcp_queue/ for cmd_*.json ===")

# --- main queue loop ---
call_counter = 0
while True:
    if proc.poll() is not None:
        log(f"hotMcpServer process exited with code {proc.returncode}; stopping daemon")
        break
    try:
        names = sorted(
            n for n in os.listdir(QUEUE_DIR)
            if n.startswith("cmd_") and n.endswith(".json")
        )
    except FileNotFoundError:
        names = []
    for name in names:
        path = os.path.join(QUEUE_DIR, name)
        call_id = name[len("cmd_"):-len(".json")]
        try:
            with open(path) as f:
                cmd = json.load(f)
        except Exception as e:
            log(f"failed to read {name}: {e}")
            os.rename(path, path + ".badread")
            continue

        tool = cmd.get("tool")
        arguments = cmd.get("arguments", {})
        rpc_id = f"call-{call_id}"
        log(f"-> tools/call {tool} args={arguments} (id={rpc_id})")
        send({
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        })
        resp = wait_for(rpc_id, timeout=90)
        result_path = os.path.join(QUEUE_DIR, f"result_{call_id}.json")

        saved_images = []
        if resp is not None:
            try:
                content = resp.get("result", {}).get("content", [])
                for i, block in enumerate(content):
                    if block.get("type") == "image" and block.get("data"):
                        img_bytes = base64.b64decode(block["data"])
                        img_name = f"{tool}_{call_id}_{i}.png"
                        img_path = os.path.join(ASSETS_DIR, img_name)
                        with open(img_path, "wb") as imgf:
                            imgf.write(img_bytes)
                        saved_images.append(img_name)
                        log(f"   saved image -> article-assets/{img_name} ({len(img_bytes)} bytes)")
            except Exception as e:
                log(f"   (no image content or error extracting: {e})")

        with open(result_path, "w") as f:
            json.dump({"response": resp, "saved_images": saved_images}, f, indent=2)

        os.remove(path)
        log(f"<- wrote {os.path.basename(result_path)} (timed_out={resp is None})")

    time.sleep(0.3)
