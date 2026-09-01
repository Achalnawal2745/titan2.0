# ⚡ TITAN 2.0
### Next-Generation Multimodal AI Assistant, Document Intelligence & System Automation Engine

[![Version](https://img.shields.io/badge/TITAN-2.0.0-00f0ff.svg?style=for-the-badge&logo=python)](https://github.com/Achalnawal2745/titan2.0.git)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-7000ff.svg?style=for-the-badge&logo=python)](https://python.org)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6%20Obsidian%20Glass-00ff9d.svg?style=for-the-badge)](https://riverbankcomputing.com)
[![Gemini Live](https://img.shields.io/badge/Voice-Gemini%20Live%20API-bc13fe.svg?style=for-the-badge&logo=google)](https://ai.google.dev)
[![NVIDIA Nemotron](https://img.shields.io/badge/Planner-NVIDIA%20Nemotron-3-super-120b-a12b-76b900.svg?style=for-the-badge&logo=nvidia)](https://www.nvidia.com/)

TITAN 2.0 is a real-time, multimodal personal AI assistant engineered for full system automation, visual awareness, biometric security, document intelligence, dynamic skill creation, and browser interaction.

**Architecture: Two Brains, One Voice**
- **Boss (Gemini Live)** — owns the microphone and speaker. Handles instant, one-shot requests (open apps, web search, system settings, quick answers). **Cannot** write files, run commands, or load skills.
- **Worker (NVIDIA Nemotron)** — spawned on demand for anything that creates a file, needs code, or requires skill instructions. Has **every** tool the boss has **plus** `write_file`, `run_command`, `load_skill`, `verify_task_result`, and can ask the user clarifying questions through the boss.

Powered by the **Google Gemini Live API** for low-latency WebSocket audio streaming and **NVIDIA Nemotron 3-Super** for multi-step planning and execution, TITAN operates as a persistent desktop command center capable of hearing, seeing, understanding, and controlling your PC.

---

## ✨ Key Features & Technical Capabilities

### 🎙️ Sub-50ms Real-Time Voice & Audio Streaming
* **Native Gemini Live WebSocket Loop**: Full-duplex conversational voice interface using `gemini-2.5-flash-native-audio-preview`.
* **VAD 2.0 Voice Activity Detection**: Energy-based RMS analysis (`_VAD_START_RMS = 580.0`, `_VAD_HOLD_RMS = 320.0`) with minimum voiced frames verification to filter out background noises and clicks.
* **GMM Speaker Verification**: Gaussian Mixture Model (`sklearn.mixture.GaussianMixture`) voice biometrics filter out unauthorized or background voices.
* **Instant Global `ESC` & Click-to-Interrupt**: 
  - **System-Wide `ESC` Key**: Uses a native Windows `GetAsyncKeyState` background hook — pressing `ESC` stops TITAN mid-speech from anywhere (even while in full-screen games or browser tabs).
  - **PortAudio Stream Abort**: Immediately terminates audio buffers with `<10 ms` latency and clears in-flight Gemini stream packets.
  - **Click-to-Stop Arc Reactor**: Clicking anywhere on the central animated HUD orb immediately cuts audio playback and resets state to `LISTENING`.

### 🧠 Skill Engine 2.0 (Isolated Venv Sandbox & Auto Self-Testing)
* **Autonomous Skill Inventing (`actions/skill_engine.py`)**: When asked to perform custom tasks without existing tools (e.g. crypto prices, network speed tests, PDF parsing), TITAN writes complete Python skills with automated `test()` functions.
* **Zero Host Environment Pollution (`skills/_sandbox/venv`)**: Custom pip dependencies (`requests`, `pandas`, `yfinance`, `beautifulsoup4`) are installed strictly inside an isolated sandbox virtual environment, keeping TITAN's primary Python packages clean.
* **Crash & Infinite-Loop Isolation**: Custom skills run in a separate runner process (`skills/_sandbox/runner.py`). A crash or freeze in custom code will never affect or crash TITAN.
* **Self-Healing Verification Loop**: If a unit test fails, TITAN inspects the traceback, autonomously edits the code, re-tests, and only executes upon 100% verification.

### 📋 TITAN Work Pad (Multi-Job Scratchpad & Interactive Checklist)
* **Persistent Task Notebook (`memory/work_pad.py`)**: Manages multiple concurrent active jobs (e.g. Capstone Report, Gold Price Skill, File Renaming).
* **Interactive Checklist States**:
  - `[ ] todo` — Queued step
  - `[>] doing` — Actively in-progress
  - `[x] done` — Completed step
  - `[!] blocked` — Paused / waiting for dependencies
* **Live UI Content Panel Mirroring**: Updates to the work pad are automatically rendered as live Markdown checklists in the on-screen Content Panel.

### 🕒 Real-Time System Clock (`get_clock`) & Universal Reminders
* **Live System Time Tool (`get_clock`)**: Injects live wall clock, day of the week, timezone offset, and ISO timestamp directly from your computer clock.
* **Multilingual Natural Reminder Engine (`actions/reminder.py`)**:
  - Supports English and Hindi phrasing (*"Remind me in 10 minutes"*, *"11:30 baje nahane ka reminder set karo"*).
  - Relative duration offsets (*"in 5 minutes"*, *"in 1 hour"*), 12-hour AM/PM times, and tomorrow scheduling.
  - **Dual Task Scheduler + Thread Timer Fallback**: Schedules persistent Windows Task Scheduler (`schtasks`) jobs with in-session thread timer fallbacks.
  - **Auditory & Visual Alerts**: Triggers notification chimes, system toasts, and native Windows `MessageBox` popup alerts.

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
├── main.py                   # Core loop — Gemini Live WebSocket session, VAD, boss↔worker dispatcher
├── ui.py                     # PyQt6 HUD — obsidian glass command center, live terminal console & security modals
├── doc_engine.py             # Docling & Unstructured document reader and formatted Word (.docx) writer
├── task_planner.py           # Multi-step autonomous document reasoning & Q&A pipeline
├── shadow_bridge.py          # Embedded Neural WebSocket Bridge (Port 8002) for Chrome Extension control
├── setup.py                  # Initial setup and wizard
├── run.bat                   # Windows launcher script with OpenBLAS memory environment constraints
│
├── actions/                  # Boss tools (instant, one-shot) + Worker-only implementations
│   ├── skill_engine.py       # Autonomous Skill Engine 2.0 (isolated venv sandbox, AST safety, self-testing)
│   ├── reminder.py           # Multilingual scheduled system notifications (schtasks + timer fallback)
│   ├── system_monitor.py     # Hardware telemetry (CPU/RAM/GPU/Temp) & voice status reporting
│   ├── ui_automation.py      # Windows Accessibility UIA background control (zero mouse hijacking)
│   ├── file_controller.py    # Local file system manager (worker-only write/move/delete)
│   ├── file_processor.py     # Local file processing engine (OCR, PDF, CSV/Excel stats, code review)
│   ├── shadow_link.py        # Chrome DOM navigation & auto-index element resolver
│   ├── voice_face_id.py      # GMM Speaker Voice Recognition & YuNet DNN Face ID Security
│   ├── web_search.py         # Grounded Google & DuckDuckGo parallel web search engine
│   ├── screen_processor.py   # Screen capture & webcam vision processing via Gemini Live
│   ├── background_monitor.py # Background topic watching & news monitoring
│   ├── proactive.py          # Proactive 2.0 context-aware check-in engine
│   ├── computer_settings.py  # Volume, brightness, Wi-Fi, window closing, lock screen
│   ├── computer_control.py   # Fallback mouse, hotkeys, and window management
│   ├── open_app.py           # Application launcher
│   ├── browser_control.py    # Native browser routing
│   ├── send_message.py       # Messaging integration
│   ├── weather_report.py     # Live weather telemetry
│   ├── flight_finder.py      # Flight search lookup
│   └── youtube_video.py      # YouTube search & playback control
│
├── core/                     # Shared runtime
│   ├── nvidia_brain.py       # NVIDIA Nemotron planner → tool loop (worker brain)
│   ├── task_workers.py       # Persistent background workers with plan/verify/ask gates
│   ├── skill_registry.py     # Progressive-disclosure SKILL.md loader (1481 skills indexed)
│   ├── tool_pipeline.py      # Guarded tool pipeline with spill budgets & loop hygiene
│   ├── error_guard.py        # Loop detection + auto-repair feedback
│   ├── spill.py              # Truncation with actionable "read with offset" guidance
│   ├── exec.py               # Command execution with sandboxed venv resolution
│   ├── prompt.txt            # Boss prompt (triage/relay/report only)
│   └── ...                   # fs_tools, agent_loop, todo_engine, goal_manager, etc.
│
├── skills/                   # 1481 SKILL.md packages (19 advertised, 1462 via search_skills)
│   ├── _sandbox/             # Isolated venv for AI-generated skills
│   ├── _meta/                # Skill unit-test logs & verification metadata
│   ├── pptx/                 # pptxgenjs v4 signatures, validate.py, OOXML references
│   ├── docx/, xlsx/, pdf/, canvas-design/, theme-factory/, ...
│   └── [1470+ more]
│
├── titan-extension/          # Embedded Chrome Extension source & DOM inspector
├── memory/
│   ├── work_pad.py           # Persistent multi-job checklist and notebook engine
│   ├── memory_manager.py     # Persistent long-term memory store
│   └── config_manager.py     # Central configuration manager
└── config/
    ├── titan_v3.ico          # Multi-resolution cropped emblem icon asset
    └── api_keys.json         # API keys, OS settings, assistant/user names
```

---

## 🛠️ Tool Registry — Boss vs Worker

**Boss tools** (Gemini Live — instant, speakable, no file creation):  
`get_clock`, `system_status`, `web_search`, `web_fetch`, `read_file`, `glob_search`, `grep_search`,  
`work_pad` (read), `reminder`, `schedule`, `send_message`, `youtube_video`,  
`open_app`, `computer_settings`, `computer_control`, `desktop_control`, `manage_monitor`,  
`screen_process`, `voice_face_id`, `save_memory`, `deep_think`, `browser_control`, `shadow_link`,  
`search_skills`, `start_task_worker`, `task_worker_status`, `send_task_worker_message`,  
`interrupt_task_worker`, `answer_worker_question`, `set_titan_microphone`, `shutdown_titan`

**Worker tools** (NVIDIA Nemotron — everything the boss has **plus** file creation, code, skills):  
*All boss tools* **plus** `load_skill`, `write_file`, `str_replace_editor`, `run_command`, `python_eval`,  
`code_helper`, `dev_agent`, `file_processor`, `file_controller` (write/move/delete), `game_updater`,  
`task_set_plan`, `verify_task_result`, `enter_plan_mode`, `exit_plan_mode`, `set_goal`, `complete_goal`, `ask_user_question`

| Tool | Owner | Scope |
|---|---|---|
| `get_clock` | Boss | Live wall clock, weekday, timezone, ISO timestamp |
| `system_status` | Boss | CPU, RAM, GPU, temperature, uptime |
| `web_search` / `web_fetch` | Boss | Grounded search + clean page fetch |
| `read_file` / `glob_search` / `grep_search` | Boss | Read-only file ops; Desktop/Downloads path expansion |
| `open_app` / `computer_settings` / `computer_control` | Boss | Instant app launch, volume, brightness, Wi-Fi, lock |
| `browser_control` / `shadow_link` | Boss | Open URL, click DOM element — not scraping projects |
| `start_task_worker` | Boss | Hand off any multi-step / file-creating task |
| `task_worker_status` / `send_task_worker_message` / `interrupt_task_worker` | Boss | Watch / steer / stop a running worker |
| `answer_worker_question` | Boss | Relay user's answer back to a blocked worker |
| `load_skill` | Worker | Pulls full SKILL.md (22 KB for pptx) — **never on boss** |
| `write_file` / `str_replace_editor` / `run_command` / `python_eval` | Worker | Authoring & execution — scripts go to `scratch/` |
| `code_helper` / `dev_agent` / `file_processor` | Worker | Code gen, dev tasks, heavy file ops |
| `task_set_plan` / `verify_task_result` | Worker | Plan (up to 12 steps) + structural quality gate |
| `ask_user_question` | Worker | Blocks worker; boss speaks question, relays answer |

---

## 🔄 How a Request Flows

1. **You speak** → Gemini Live transcribes → Boss receives text.
2. **Boss triages** (instant, no tools):
   - One-shot, speakable answer? → Boss answers directly (`web_search`, `open_app`, etc.).
   - Creates/edits a file, needs code, or multi-step? → Boss calls `start_task_worker` with the **complete** user request.
3. **Worker starts** (NVIDIA Nemotron):
   - Gets its own message history, full tool set, and the skill catalog index.
   - Calls `load_skill('pptx')` → receives **full 22 KB** of design rules, gotchas, validation steps.
   - Calls `task_set_plan` (up to 12 steps).
   - Writes generator script to `scratch/generate_<name>.js`, runs it via `run_command`.
   - If a command fails, reads the real error, fixes that line, retries.
   - Calls `verify_task_result` with output paths. Gate checks:
     - File exists and is not corrupt (OOXML ZIP valid)
     - Size ≥ minimum plausible bytes (pptx ≥ 12 KB, docx ≥ 8 KB)
     - ≥ 3 slides for presentations; required XML parts present
     - **Skill was actually loaded** — building a skill-backed format without `load_skill` rejects
4. **Worker finishes** → emits `completed` event.
5. **Boss relays** → speaks the worker's one-sentence report to you.

While the worker runs, you stay free to talk to the boss. "Is it done?" → boss calls `task_worker_status`. "Change the theme to dark" → boss calls `send_task_worker_message`. "Stop" → boss calls `interrupt_task_worker`.

## 🧪 Quality Gate — `verify_task_result`

The old gate only checked "file exists." The new gate rejects:

- Corrupt Office files (bad ZIP, invalid XML)
- Near-empty files (pptx < 12 KB, docx < 8 KB, xlsx < 4 KB)
- Decks with fewer than 3 slides
- Skill-backed formats built **without ever calling `load_skill`**
- Charts using corrupting patterns (`#` prefix, 8-digit alpha hex)

This is why the earlier "presentation.pptx" (2 slides) was rejected while "India_Presentation.pptx" passed.

---

## 🔒 Biometric Privacy & Security

### 1. Prerequisites
* **OS**: Windows 10 / 11 (recommended), macOS, or Linux
* **Python**: Python 3.11, 3.12, or 3.14
* **Hardware**: Microphone & Webcam (optional for Face ID)

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/Achalnawal2745/titan2.0.git
cd titan2.0

# Install dependencies
pip install -r requirements.txt
npm install  # inside titan-extension/ for Chrome extension

# Launch TITAN 2.0
python main.py
```
*or simply double-click **`TITAN AI Assistant.lnk`** on your Desktop.*

### 3. API Configuration
Copy the template configuration file:
```bash
cp config/api_keys.example.json config/api_keys.json
```
And add your API keys in `config/api_keys.json`:
```json
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "nvidia_api_key": "YOUR_NVIDIA_API_KEY",
  "assistant_name": "TITAN",
  "user_name": "Sir",
  "os_system": "windows"
}
```
**Note**: `full_brain_mode` is deprecated — the worker always uses NVIDIA Nemotron; the boss is always Gemini Live.

---

## 🔒 Biometric Privacy & Security
* **Local Biometric Stores**: Facial embeddings (`memory/owner_face.npy`) and GMM voice profiles (`memory/owner_voice_gmm.pkl`) are computed and stored 100% locally on your machine.
* **Master Security Gate**: When Master Security Lock is enabled, desktop interaction is strictly blocked until Face ID, Voice Verification, or PIN authentication passes.

---

## 🛡️ Reliability Fixes (2026-08)

- **read_file spill budgets**: `read_file` now gets 2000 lines / 120 KB before spilling (was 50/2.5 KB). A worker can now see its entire generator script at once, so `str_replace_editor` matches on real content instead of memory.
- **Loop-hygiene guard reset**: A successful `write_file` / `str_replace_editor` / `run_command` clears the failure signature history, so a legitimate retry after a fix isn't blocked.
- **HEAD/TAIL previews increased**: 60 head / 30 tail lines when spilling does occur, plus an explicit "read with offset_lines/max_lines" hint.
- **Skill truncation removed**: `load_skill` and `search_skills` have a 60 KB cap and never spill — the worker receives the full skill body every time.
- **Hop refunds for read-only calls**: `load_skill`, `read_file`, `grep_search`, `todo_read`, `get_clock` refund their hop (up to 8 refunds), so loading a 22 KB skill doesn't consume budget.

---

## 📄 License
Personal & Open Source Development. Built by **Achal Nawal**.
