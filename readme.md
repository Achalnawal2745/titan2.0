# ⚡ TITAN 2.0
### Next-Generation Multimodal AI Assistant, Document Intelligence & System Automation Engine

[![Version](https://img.shields.io/badge/TITAN-2.0.0-00f0ff.svg?style=for-the-badge&logo=python)](https://github.com/Achalnawal2745/titan2.0.git)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-7000ff.svg?style=for-the-badge&logo=python)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6%20Obsidian%20Glass-00ff9d.svg?style=for-the-badge)](https://riverbankcomputing.com)
[![Gemini Live](https://img.shields.io/badge/AI%20Core-Gemini%20Live%20API-bc13fe.svg?style=for-the-badge&logo=google)](https://ai.google.dev)

TITAN 2.0 is a real-time, multimodal personal AI assistant engineered for full system automation, visual awareness, biometric security, document intelligence, and browser interaction. Powered by the **Google Gemini Live API** for low-latency WebSocket audio streaming, TITAN operates as a persistent desktop command center capable of hearing, seeing, understanding, and controlling your PC.

---

## ✨ Key Features & Technical Capabilities

### 🎙️ Sub-50ms Real-Time Voice & Audio Streaming
* **Native Gemini Live WebSocket Loop**: Full-duplex conversational voice interface using `gemini-2.5-flash`.
* **GMM Speaker Verification**: Gaussian Mixture Model (`sklearn.mixture.GaussianMixture`) voice biometrics filter out background voices.
* **Instant Hardware Interrupt**: Press `Esc` or click `Interrupt` to instantly purge audio buffers and issue server-side turn cancellation.

### 🖱️ Background Windows UI Automation (Zero Mouse Hijacking)
* **Accessibility UIA Integration (`actions/ui_automation.py`)**: Uses Windows Accessibility API (`pywinauto` / UIAutomation) to inspect app DOM trees, click buttons, paste text, and extract control text.
* **Non-Disruptive Desktop Control**: Programmatically interacts with applications (Notepad, Calculator, Word, Settings) **without moving or stealing your physical mouse pointer**.

### 📄 Document Intelligence & Autonomous Task Pipeline
* **Vision PDF & Document Parser (`doc_engine.py`)**: Uses **Docling (Vision-based PDF parser)** & **Unstructured** to parse tables, multi-column layouts, and scanned documents.
* **Smart Word Report Generator (`task_planner.py`)**: Reads documents, extracts & answers questions, rewrites text, and generates formatted Microsoft Word `.docx` documents with styled headers, bullet lists, and Q&A blocks.

### 🌐 Shadow-Link Chrome Extension Integration
* **Neural Web Bridge (`shadow_bridge.py`)**: Embedded WebSocket server (Port 8002) connecting TITAN directly to your live Chrome browser.
* **Auto-Index DOM Clicker**: Inspects live web DOM trees, extracts numeric `highlightIndex` flags, and clicks elements or fills forms by voice command.

### 🛡️ Biometric Security & Centered Modal Lock Screen
* **YuNet DNN Face ID**: Real-time facial embedding verification using OpenCV YuNet Deep Neural Network.
* **ApplicationModal Security Gate**: Centered glass security overlay that blocks unauthorized UI access on startup or lock toggle.
* **Triple Verification**: Unlock via Face Recognition, Voice Biometrics, or Passcode PIN.

### 🧩 Autonomous Skill Engine & Dynamic Plugin Lifecycle
* **Self-Generated Python Skills (`actions/skill_engine.py`)**: TITAN can write, sandbox test, execute, edit, and delete custom Python skills dynamically on demand.
* **AST Static Security Analyzer**: Inspects code syntax trees to block destructive operating system commands (`rmdir /s /q`, disk wipers, malicious scripts) before execution.
* **Subprocess Sandbox Verification**: Executes newly generated skills in an isolated subprocess with a strict 10-second timeout.
* **Persistent Skill Storage (`skills/`)**: Skills are permanently saved as `.py` files and automatically reloaded into memory on startup.

### 💻 Live Desktop Terminal & Real-Time Debug Console
* **Dedicated Terminal Overlay (`ui.py`)**: Click **`💻 TERMINAL`** in the header to open a floating cyberpunk live console.
* **Full Stdout/Stderr Redirection**: Captures 100% of background `print()` statements, LLM payloads, audio stream events, and exception tracebacks from the moment TITAN boots.
* **Stream Isolation**: Keeps the right sidebar **Activity Stream** clean and user-friendly while sending deep raw logs to the Terminal.
* **Console Controls**: Live keyword search/filter, Auto-Scroll toggle, Clear Console, and Copy All.

### 📊 Real-Time System Telemetry & Hardware Monitor
* **Dynamic Hardware Telemetry (`actions/system_monitor.py`)**: Real-time monitoring for CPU, RAM, Network speeds, GPU load, and CPU temperature.
* **Dynamic Thermal Load Estimation**: Ensures active °C temperatures and GPU metrics are always reported accurately on Windows even without admin permissions.

---

## 🗂️ Project Directory Architecture

```text
titan2.0/
├── main.py                   # Core loop — Gemini Live WebSocket session, tool dispatcher & startup gate
├── ui.py                     # PyQt6 HUD — obsidian glass command center, live terminal console & security modals
├── doc_engine.py             # Docling & Unstructured document reader and formatted Word (.docx) writer
├── task_planner.py           # Multi-step autonomous document reasoning & Q&A pipeline
├── shadow_bridge.py          # Embedded Neural WebSocket Bridge (Port 8002) for Chrome Extension control
├── setup.py                  # Initial setup and wizard
├── run.bat                   # Windows launcher script with OpenBLAS memory environment constraints
│
├── actions/
│   ├── skill_engine.py       # Autonomous Skill Engine (create, edit, delete, AST safety, sandbox test)
│   ├── system_monitor.py     # Hardware telemetry (CPU/RAM/GPU/Temp) & voice status reporting
│   ├── ui_automation.py      # Windows Accessibility UIA background control (zero mouse hijacking)
│   ├── file_controller.py    # Local file system manager with safe .docx Word generator routing
│   ├── file_processor.py     # Local file processing engine (OCR, PDF, CSV/Excel stats, code review)
│   ├── shadow_link.py        # Chrome DOM navigation & auto-index element resolver
│   ├── voice_face_id.py      # GMM Speaker Voice Recognition & YuNet DNN Face ID Security
│   ├── web_search.py         # Grounded Google & DuckDuckGo parallel web search engine
│   ├── screen_processor.py   # Screen capture & webcam vision processing via Gemini Live
│   ├── background_monitor.py # Background topic watching & news monitoring
│   ├── proactive.py          # Proactive 2.0 context-aware check-in engine
│   ├── reminder.py           # Scheduled system notifications
│   ├── computer_settings.py  # Volume, brightness, Wi-Fi, power control
│   ├── computer_control.py   # Fallback mouse, hotkeys, and window management
│   ├── open_app.py           # Application launcher
│   ├── browser_control.py    # Native browser routing
│   ├── send_message.py       # Messaging integration
│   ├── weather_report.py     # Live weather telemetry
│   ├── flight_finder.py      # Flight search lookup
│   └── youtube_video.py      # YouTube search & playback control
│
├── skills/                   # Persistent user & AI-generated custom Python skill modules
├── titan-extension/          # Embedded Chrome Extension source & DOM inspector
├── memory/
│   ├── memory_manager.py     # Persistent memory manager
│   ├── security_config.json  # Master security lock configurations & enrollment flags
│   └── long_term.json        # Long-term persistent memory store
├── core/
│   └── prompt.txt            # System prompt & tool routing directives
└── config/
    ├── titan_v3.ico          # Multi-resolution cropped emblem icon asset
    └── api_keys.json         # API key, OS settings, assistant name, user name
```

---

## 🛠️ Tool Registry & Function Calling Reference

| Tool Name | Action / Scope | Description |
|---|---|---|
| `skill_engine` | `create_skill` \| `edit_skill` \| `get_code` \| `delete_skill` \| `list_skills` \| `execute_skill` | Autonomous Skill Lifecycle Engine with AST security verification and sandbox testing. |
| `system_status` | *None* | Real-time CPU, RAM, GPU, CPU temperature, uptime, and process telemetry. |
| `ui_automation` | `click` \| `type` \| `get_text` \| `dump_tree` | **Primary** Windows desktop app interaction via UIAutomation without stealing mouse pointer. |
| `smart_task` | `answer_questions_in_doc` \| `summarize_document` \| `rewrite_document` \| `generate_document` | Autonomous multi-step document reasoning & styled Word `.docx` report writer. |
| `shadow_link` | `get_url` \| `click` \| `type` \| `scroll` \| `extract` | Primary Chrome web browser DOM interaction tool via WebSocket bridge. |
| `file_processor` | `summarize` \| `ocr` \| `analyze` \| `to_word` \| `stats` | Processes uploaded files (PDFs, Word docs, CSV/Excel, images, code files). |
| `file_controller` | `read` \| `write` \| `move` \| `copy` \| `find` \| `delete` | General file manager. Automatically routes `.docx` writes through `doc_engine`. |
| `voice_face_id` | `enroll_face` \| `enroll_voice` \| `status` \| `toggle` | Enrolls biometric templates and toggles Master Security Lock states. |
| `screen_process` | `screen` \| `camera` | Captures current screen or webcam feed for Gemini Live visual reasoning. |
| `computer_settings` | `volume` \| `brightness` \| `wifi` \| `power` | System settings controller. |
| `computer_control` | `hotkey` \| `scroll` \| `move` | Fallback raw mouse and hotkey manager. |

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
* **OS**: Windows 10 / 11 (recommended), macOS, or Linux
* **Python**: Python 3.11 or 3.12
* **Hardware**: Microphone & Webcam (optional for Face ID)

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/Achalnawal2745/titan2.0.git
cd titan2.0

# Install dependencies
pip install -r requirements.txt

# Launch TITAN 2.0
python main.py
```
*or simply double-click **`TITAN AI Assistant.lnk`** on your Desktop.*

### 3. API Configuration
Add your Gemini API key in `config/api_keys.json`:
```json
{
  "api_key": "YOUR_GEMINI_API_KEY",
  "assistant_name": "TITAN",
  "user_name": "Achal"
}
```

---

## 🔒 Biometric Privacy & Security
* **Local Biometric Stores**: Facial embeddings (`memory/owner_face.npy`) and GMM voice profiles (`memory/owner_voice_gmm.pkl`) are computed and stored 100% locally on your machine.
* **Master Security Gate**: When Master Security Lock is enabled, desktop interaction is strictly blocked until Face ID, Voice Verification, or PIN authentication passes.

---

## 📄 License
Personal & Open Source Development. Built by **Achal Nawal**.
