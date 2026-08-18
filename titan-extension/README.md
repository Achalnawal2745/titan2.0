<h1 align="center">
    ⚡ TITAN Browser Agent
</h1>

<p align="center">
  <strong>Autonomous AI Web Automation & Browser Intelligence Extension</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/TITAN-AI_Browser_Agent-blue?style=for-the-badge" alt="TITAN Badge" />
  <img src="https://img.shields.io/badge/Platform-Chrome_|_Edge-darkgreen?style=for-the-badge" alt="Platform Badge" />
  <img src="https://img.shields.io/badge/License-Apache_2.0-orange?style=for-the-badge" alt="License Badge" />
</p>

---

## 🌐 Overview

**TITAN Browser Extension** is an autonomous AI web automation agent that runs directly in your browser. Powered by multi-agent planning and multi-modal computer vision, TITAN navigates web pages, extracts data, fills forms, conducts deep research, and interacts with web applications on your behalf.

---

## 🔥 Key Features

- **Multi-Agent System**:
  - **Planner Agent**: Analyzes your goal, breaks it into atomic sub-tasks, and self-corrects upon obstacles.
  - **Navigator Agent**: Interacts with UI elements, inputs text, clicks buttons, scrolls, and navigates.
- **Interactive Side Panel**: Sleek, modern side-panel interface with real-time thought inspection and action logs.
- **Voice Input**: Speak your tasks directly into the extension using native browser speech recognition.
- **Flexible LLM Support**:
  - Gemini (2.5 Flash, 2.5 Pro)
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Anthropic (Claude 3.5 Sonnet)
  - Local Ollama & Custom OpenAI-Compatible APIs
- **100% Privacy & Local Control**: All credentials and session cookies remain securely in your local browser.

---

## 🚀 Installation & Setup

### 1. Build from Source
```bash
# Install dependencies
pnpm install

# Build extension
pnpm build
```

### 2. Load into Chrome / Edge
1. Open your browser and navigate to `chrome://extensions/` (or `edge://extensions/`).
2. Toggle **Developer mode** in the top right corner.
3. Click **Load unpacked**.
4. Select the `dist/` folder inside `titan-extension`.
5. Pin the **TITAN** icon to your toolbar.

---

## ⚙️ Configuration

1. Click the TITAN extension icon in your browser toolbar to open the side panel.
2. Click the **Settings** (gear) icon in the top header.
3. Enter your API key (e.g. Gemini, OpenAI, or Ollama endpoint).
4. Select your preferred Planner and Navigator models.
5. You're ready to automate any web task!

---

## 🛡️ License

This project is licensed under the Apache 2.0 License.
