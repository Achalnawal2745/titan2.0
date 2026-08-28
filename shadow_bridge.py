import asyncio
import json
import websockets
import os
import uuid
from datetime import datetime
import sys
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="ignore")
except Exception:
    pass

import logging
logging.getLogger("websockets").setLevel(logging.CRITICAL)
logging.getLogger("websockets.server").setLevel(logging.CRITICAL)

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class _F:
        BLACK = WHITE = CYAN = GREEN = RED = YELLOW = MAGENTA = ""
    class _S:
        BRIGHT = RESET_ALL = ""
    Fore = _F()
    Style = _S()

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_DIR = os.path.join(BASE_DIR, "shadow_vault")
BRIDGE_PORT = 8002

class ShadowBridge:
    """
    ShadowBridge: The Neural Link between ShadowOS PC and Browser Extension.
    Clean, robust, and bi-directional.
    """
    def __init__(self):
        self.connected_extension = None
        self.pending_commands = {}
        self._ensure_vault_exists()

    def _ensure_vault_exists(self):
        if not os.path.exists(VAULT_DIR):
            os.makedirs(VAULT_DIR)

    def log(self, category, message, color=Fore.WHITE):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.BLACK}{Style.BRIGHT}[{timestamp}]{Style.RESET_ALL} {color}[{category}]{Style.RESET_ALL} {message}")

    def save_finding(self, data, prefix="finding"):
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(VAULT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return filepath

    async def handle_connection(self, websocket):
        path = "/"
        if hasattr(websocket, "request") and websocket.request:
            path = websocket.request.path
        elif hasattr(websocket, "path"):
            path = websocket.path
            
        # Extract path without query parameters if present
        if "?" in path:
            path = path.split("?")[0]
            
        self.log("BRIDGE", f"Connection attempt on path: {path}", Fore.CYAN)
        if path == "/client":
            self.log("BRIDGE", "Connection established with Controller Client (TITAN)", Fore.GREEN)
            try:
                async for message in websocket:
                    try:
                        payload = json.loads(message)
                        message_id = payload.get("id") or str(uuid.uuid4())
                        payload["id"] = message_id
                        
                        if self.connected_extension:
                            loop = asyncio.get_running_loop()
                            self.pending_commands[message_id] = loop.create_future()
                            
                            # Forward command to extension
                            await self.connected_extension.send(json.dumps(payload))
                            
                            try:
                                # Wait for response from extension
                                response = await asyncio.wait_for(self.pending_commands[message_id], timeout=60.0)
                                await websocket.send(json.dumps(response))
                            except asyncio.TimeoutError:
                                self.log("ERROR", f"Command timeout: {message_id}", Fore.RED)
                                if message_id in self.pending_commands:
                                    del self.pending_commands[message_id]
                                await websocket.send(json.dumps({
                                    "id": message_id,
                                    "state": "ERROR",
                                    "msg": "Command timed out waiting for extension response"
                                }))
                            except Exception as fut_err:
                                await websocket.send(json.dumps({
                                    "id": message_id,
                                    "state": "ERROR",
                                    "msg": f"Command error: {fut_err}"
                                }))
                        else:
                            await websocket.send(json.dumps({
                                "id": message_id,
                                "state": "ERROR",
                                "msg": "No extension connected. Please open Chrome with the Titan extension enabled."
                            }))
                    except json.JSONDecodeError:
                        self.log("ERROR", f"Invalid JSON from client: {message}", Fore.RED)
            except websockets.exceptions.ConnectionClosed:
                self.log("BRIDGE", "Controller Client disconnected", Fore.YELLOW)
        else:
            self.log("BRIDGE", "Connection established with Chrome Extension", Fore.GREEN)
            self.connected_extension = websocket
            try:
                async for message in websocket:
                    try:
                        payload = json.loads(message)
                        if payload.get("type") == "ping":
                            continue
                        message_id = payload.get("id")
                        if message_id and message_id in self.pending_commands:
                            # Resolve the future with the result
                            if not self.pending_commands[message_id].done():
                                self.pending_commands[message_id].set_result(payload)
                        else:
                            self._process_payload(payload)
                    except json.JSONDecodeError:
                        self.log("ERROR", f"Invalid JSON from extension: {message}", Fore.RED)
            except websockets.exceptions.ConnectionClosed:
                self.log("BRIDGE", "Extension disconnected", Fore.RED)
                self.connected_extension = None
                # Fail all pending futures
                for fut in list(self.pending_commands.values()):
                    if not fut.done():
                        fut.set_exception(Exception("Extension disconnected"))
                self.pending_commands.clear()

    def _process_payload(self, payload):
        state = payload.get("state", "UPDATE")
        msg = payload.get("msg", "")
        
        if state == "COMPLETE":
            self.log("SUCCESS", f"Task Finalized: {msg}", Fore.GREEN)
            result_path = self.save_finding(payload.get("result", {}), "task_result")
            self.log("VAULT", f"Stored result at {result_path}", Fore.BLUE)
            if hasattr(os, "startfile"):
                os.startfile(os.path.abspath(VAULT_DIR))
            
        elif state == "EXTRACT":
            self.log("DATA", "Extracted information received", Fore.YELLOW)
            path = self.save_finding(payload.get("data", {}), "extracted")
            self.log("VAULT", f"Captured data in {path}", Fore.BLUE)
            
        else:
            self.log("AGENT", msg, Fore.CYAN)

    async def send_command(self, task):
        if not self.connected_extension:
            self.log("BRIDGE", "No extension connected. Launch Chrome with Shadow-Link!", Fore.RED)
            return
        
        command = {
            "id": str(uuid.uuid4()),
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
        await self.connected_extension.send(json.dumps(command))
        self.log("BRIDGE", f"Command transmitted: {task}", Fore.MAGENTA)

    async def start(self):
        self.log("SYSTEM", f"Shadow Neural Bridge active on port {BRIDGE_PORT}", Fore.GREEN)
        async with websockets.serve(self.handle_connection, "localhost", BRIDGE_PORT):
            await asyncio.Future()  # Run forever

if __name__ == "__main__":
    bridge = ShadowBridge()
    try:
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}System Shutting Down...")
