# ⚡ TITAN 2.0
### Next-Generation Autonomous AI Assistant & System Controller

TITAN 2.0 is a real-time, multimodal personal AI assistant engineered for full system automation, visual awareness, biometric security, document intelligence, and browser interaction. Powered by the Google Gemini Live API for low-latency audio streaming, TITAN operates as a persistent desktop presence capable of hearing, seeing, understanding, and controlling your PC.

---

## ✨ Key Features & Capabilities

### 🎙️ Real-Time Multimodal Voice & Audio
* **Native Audio Streaming**: Sub-50ms conversational speech loop via Gemini Live WebSocket API.
* **GMM Voice Biometrics**: Gaussian Mixture Model (`sklearn.mixture.GaussianMixture`) speaker verification filters unrecognized background voices.
* **Instant Interrupt**: Press `Esc` or click `Interrupt` to clear audio playback and send server-side turn cancellation instantly.

### 🖱️ Background UI Accessibility Automation
* **Zero Mouse Hijacking**: Uses Windows Accessibility API (`pywinauto` / UIAutomation) to click buttons, inspect trees, and paste text inside desktop apps without moving your physical mouse pointer.

### 📄 Document Intelligence & Autonomous Task Pipeline
* **Vision PDF & Document Parser**: Parses `.pdf`, `.docx`, `.pptx`, `.xlsx` using **Docling (Vision-based PDF parser)** & **Unstructured**.
* **Smart Word Report Generator**: Automatically answers questions inside documents, transforms formats, and exports styled `.docx` Word documents (`task_planner.py` & `doc_engine.py`).

### 🛡️ Biometric Security & Lock Screen
* **YuNet DNN Face ID**: Real-time facial embedding comparison using OpenCV YuNet DNN.
* **Interactive Modal Lock Screen**: ApplicationModal security overlay centered on screen — blocks unauthorized UI access.
* **Triple-Check Security**: Unlock via Face Scan, Voice Biometrics, or Passcode.

### 🌐 Shadow-Link Chrome Extension Integration
* **Neural Web Bridge**: Built-in WebSocket server (Port 8002) connecting TITAN to your live Chrome browser.
* **Auto-Index Element Clicking**: Inspects Chrome DOM tree and auto-resolves numeric `highlightIndex` for buttons, inputs, and email rows.
* **Full Browser Automation**: Navigate tabs, extract web content, fill forms, and control web apps by voice.

---

## 🗂️ Project Architecture

```text
titan2.0/
├── main.py                   # Core loop — Gemini Live session, tool dispatch & startup gate
├── ui.py                     # PyQt6 HUD — waveform display, log panel & futuristic command center UI
├── doc_engine.py             # Docling & Unstructured document reader and formatted Word (.docx) generator
├── task_planner.py           # Multi-step document reasoning & answer extraction pipeline
├── shadow_bridge.py          # Embedded Neural WebSocket Bridge (Port 8002) for Chrome Extension control
├── setup.py                  # Initial setup and wizard
├── actions/
│   ├── ui_automation.py      # Windows Accessibility UIA background control (zero mouse hijacking)
│   ├── shadow_link.py        # Chrome DOM navigation & auto-index element resolver
│   ├── voice_face_id.py      # GMM Speaker Voice Recognition & YuNet DNN Face ID Security
│   ├── web_search.py         # Grounded Google & DuckDuckGo parallel web search
│   ├── screen_processor.py   # Screen capture & webcam vision via Gemini Live
│   ├── background_monitor.py # Background topic watching & news check
│   ├── proactive.py          # Proactive 2.0 context-aware check-in engine
│   ├── reminder.py           # Scheduled system notifications
│   ├── system_monitor.py     # Hardware telemetry (CPU/RAM/GPU/Temp)
│   ├── computer_settings.py  # Volume, brightness, Wi-Fi, power control
│   ├── computer_control.py   # Mouse, keyboard shortcuts, window management
│   ├── open_app.py           # Application launcher
│   ├── browser_control.py    # Native browser routing
│   ├── file_processor.py     # Local document reading & summarization
│   ├── send_message.py       # Messaging integration
│   ├── weather_report.py     # Live weather telemetry
│   ├── flight_finder.py      # Flight search lookup
│   └── youtube_video.py      # YouTube search & playback control
├── titan-extension/          # Embedded Chrome Extension source & DOM inspector
├── memory/
│   ├── memory_manager.py     # Persistent memory manager
│   ├── security_config.json  # Master security lock configurations & enrollment flags
│   └── long_term.json        # Long-term persistent memory store
├── core/
│   └── prompt.txt            # System prompt & tool routing directives
└── config/
    └── api_keys.json         # API key, OS setting, assistant name, user name
```

---

## ⚡ Quick Start & Installation

```bash
# Clone the repository
git clone https://github.com/Achalnawal2745/titan2.0.git
cd titan2.0

# Install dependencies
pip install -r requirements.txt

# Launch TITAN 2.0
python main.py
```

---

## 📄 License
Personal & Open Source Development. Built by **Achal Nawal**.
