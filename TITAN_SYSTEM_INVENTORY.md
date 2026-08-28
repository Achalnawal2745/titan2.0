# 🌌 TITAN Mark-L — Complete System Architecture & File Inventory

This document is the **authoritative, 100% comprehensive encyclopedia** of every directory, file, module, function, and tool in **TITAN Mark-L**.

---

## 📑 Master Table of Contents
1. [🏗️ High-Level System Architecture](#1-high-level-system-architecture)
2. [📁 Root Level Files](#2-root-level-files)
3. [🧠 `core/` — Agent Core, Harness & Execution Loop](#3-core--agent-core-harness--execution-loop)
4. [⚡ `actions/` — Hardware, OS, Media & Desktop Tools](#4-actions--hardware-os-media--desktop-tools)
5. [🔌 `plugins/` — Live Voice Extensible Plugins](#5-plugins--live-voice-extensible-plugins)
6. [💾 `memory/` — Long-Term Memory, Security & Persistence](#6-memory--long-term-memory-security--persistence)
7. [⚙️ `config/` — API Keys & System Configuration](#7-config--api-keys--system-configuration)
8. [🖥️ `dashboard/` — Web UI & Local Host Interface](#8-dashboard--web-ui--local-host-interface)
9. [🌐 `titan-extension/` — Chrome Extension & Neural Bridge](#9-titan-extension--chrome-extension--neural-bridge)
10. [📚 `skills/` — 1,481+ On-Demand Skill Library](#10-skills--1481-on-demand-skill-library)
11. [🛠️ Complete 51 Tool Reference Map](#11-complete-51-tool-reference-map)

---

## 1. 🏗️ High-Level System Architecture

```mermaid
graph TD
    User([🎙️ Voice / Mic Input]) --> Main[main.py: TitanLive Engine]
    Main <--> UI[ui.py: PyQt6 Cyberpunk HUD]
    Main <--> Bridge[shadow_bridge.py: WebSocket Neural Bridge]
    Bridge <--> Chrome[titan-extension: Chrome Browser]

    subgraph DeepSeek Harness Core [core/]
        AgentLoop[agent_loop.py]
        PromptBuilder[prompt_builder.py]
        ToolPipeline[tool_pipeline.py]
        SpillEngine[spill.py]
        ErrorGuard[error_guard.py]
        Subagents[subagent_engine.py]
        Todo[todo_engine.py]
        Goals[goal_manager.py]
        Scheduler[scheduler.py]
        FSTools[fs_tools.py]
        CodeRun[code_runner.py]
        WebTools[web_tools.py]
        Exec[exec.py]
    end

    subgraph Desktop & System Actions [actions/]
        OSControl[computer_control.py & desktop.py]
        FileOps[file_processor.py & file_controller.py]
        Media[screen_processor.py & youtube_video.py]
        Security[voice_face_id.py]
        Web[web_search.py]
    end

    subgraph Extensibility & Memory [plugins/ & memory/]
        Plugins[plugin_loader.py -> plugins/*.py]
        Skills[skill_registry.py -> skills/**/SKILL.md]
        Mem[memory_manager.py & work_pad.py]
    end

    Main --> DeepSeek Harness Core
    Main --> Desktop & System Actions
    Main --> Extensibility & Memory
```

---

## 2. 📁 Root Level Files

| File | Primary Role | Key Classes & Functions |
| :--- | :--- | :--- |
| **`main.py`** | Central process entry point, Gemini Live duplex audio engine, tool dispatcher, and event loop. | `TitanLive` class, `_execute_tool()`, `TOOL_DECLARATIONS` (51 tools), `main()`. |
| **`ui.py`** | Cyberpunk-themed PyQt6 GUI dashboard, sound synthesis, live transcript logging, and visualizer. | `TitanUI` class, `write_log()`, `set_status()`, sound effects, plugin manager modal. |
| **`shadow_bridge.py`** | Async WebSocket server (Port `8002`) connecting TITAN to the Chrome Extension. | `start_server()`, WebSocket message dispatcher, Chrome command router. |
| **`task_control.py`** | Cooperative emergency cancel system for long-running jobs (PPT, DOCX, scripts). | `request_cancel()`, `clear_cancel()`, `is_cancelled()`, `set_ui_hooks()`. |
| **`run.bat`** | Windows startup batch script that activates virtualenv and launches TITAN. | Environment initialization & process launcher. |
| **`requirements.txt`** | Python dependencies (PyQt6, google-genai, opencv, beautifulsoup4, etc.). | Pinned package requirements. |
| **`setup.py`** | Package setup configuration for TITAN installation. | Python package metadata. |
| **`package.json`** | Node.js metadata for office generators and scripts. | Node script configurations. |
| **`readme.md`** | High-level project documentation and user guide. | Project overview. |

---

## 3. 🧠 `core/` — Agent Core, Harness & Execution Loop

The `core/` directory houses the **DeepSeek Harness architecture** adapted for live voice and Windows OS control:

| File | Purpose | Key Exports & Functions |
| :--- | :--- | :--- |
| **`agent.py`** | Lifecycle state machine for autonomous agents (IDLE, THINKING, EXECUTING, RECOVERING). | `Agent`, `AgentState`, `AgentLifecycle`. |
| **`agent_loop.py`** | Multi-turn step execution machine with recursion caps and turn budgets. | `AgentLoop`, `TurnContext`, `execute_turn()`. |
| **`code_runner.py`** | Isolated Python code execution runtime with output capture and timeout protection. | `run_python_code()`, `PYTHON_EVAL_DECLARATION`. |
| **`error_guard.py`** | Autonomous error classifier, loop hygiene, and recovery strategy generator. | `classify_error()`, `get_recovery_hint()`, `sanitize_error()`. |
| **`exec.py`** | The **ONLY** subprocess execution engine in TITAN. Handles Windows `.cmd`/`.exe` auto-resolution, UTF-8 encoding pinning, and tree-kill on timeouts. | `run_command()`, `run_python_file()`, `_resolve_python()`, `RUN_COMMAND_DECLARATION`. |
| **`fs_tools.py`** | Precision file reading, writing, surgical string replacements, and regex/glob searching. | `read_file()`, `write_file()`, `str_replace_editor()`, `grep_search()`, `glob_search()`, `FS_TOOLS_DECLARATIONS`. |
| **`goal_manager.py`** | Multi-round persistent goal tracker surviving restarts (`memory/goals.json`). | `GoalManager`, `set_goal()`, `complete_goal()`, `GOAL_TOOLS_DECLARATIONS`. |
| **`installer.py`** | Package dependency installer for missing Python and Node modules on the fly. | `ensure_package()`, `install_pip()`, `install_npm()`. |
| **`interaction.py`** | Interactive decision prompts, user multiple-choice questions, and plan approval modal. | `InteractionEngine`, `ask_user()`, `ASK_USER_DECLARATION`. |
| **`jobs.py`** | Background job registry for heavy non-blocking tasks. | `JobRegistry`, `job_list()`, `job_output()`, `job_kill()`, `JOB_TOOLS_DECLARATIONS`. |
| **`llm.py`** | Provider-neutral LLM client interface for fallback models. | `LlmProvider`, `complete()`, `stream()`. |
| **`llm_client.py`** | Gemini Live & Gemini Flash API low-level transport wrapper. | `GeminiClient`, `create_session()`, audio framing. |
| **`plan_mode.py`** | Architectural plan mode gating write actions until the user approves. | `PlanMode`, `enter_plan_mode()`, `exit_plan_mode()`, `PLAN_MODE_DECLARATIONS`. |
| **`plugin_loader.py`** | Scans and validates `plugins/*.py` with collision detection and enable/disable toggles. | `discover_plugins()`, `PluginRegistry`, `PluginRecord`. |
| **`prompt.txt`** | Master System Prompt defining TITAN's persona, protocols, and tool invocation rules. | Plain-text master prompt. |
| **`prompt_builder.py`** | Dynamic prompt assembler injecting time, active goals, open checklist, and system state. | `build_system_prompt()`, context injection. |
| **`scheduler.py`** | Async one-shot timers and recurring cron jobs for proactive reminders. | `Scheduler`, `schedule()`, `SCHEDULE_DECLARATION`. |
| **`scope.py`** | Scope-based resource isolation for subagents and background sessions. | `ScopeContext`, `enter_scope()`, `exit_scope()`. |
| **`session_log.py`** | Immutable JSONL session logger recording events, steps, and tool calls. | `SessionLogger`, `log_event()`, `get_history()`. |
| **`skill_registry.py`** | On-demand skill indexing and parser for 1,481+ `SKILL.md` playbooks. | `SkillRegistry`, `load_skill()`, `discover_skills()`, `LOAD_SKILL_DECLARATION`. |
| **`spill.py`** | Spill-to-disk engine preventing oversized tool outputs (>15KB) from overflowing the context window. | `maybe_spill_output()`, `SpillStore`. |
| **`stt.py`** | Speech-to-Text fallback and microphone audio intake. | `AudioRecorder`, `transcribe_stream()`. |
| **`subagent_engine.py`** | Spawns, monitors, steers, and stops dedicated worker subagents (`researcher`, `coder`, etc.). | `SubagentEngine`, `invoke_subagent()`, `list_agents()`, `send_message()`, `interrupt()`, `SUBAGENT_TOOLS_DECLARATIONS`. |
| **`todo_engine.py`** | Live Todo Checklist Engine with real-time markdown checklist updates. | `TodoEngine`, `todo_write()`, `todo_read()`, `TODO_WRITE_DECLARATION`, `TODO_READ_DECLARATION`. |
| **`tool_pipeline.py`** | 4-Stage tool execution pipeline: `PreExecute` → `Execute` → `PostExecute` → `ErrorRecovery`. | `ToolPipeline`, `execute_pipeline()`. |
| **`tts.py`** | Text-to-Speech audio synthesizer for voice responses. | `speak()`, audio queue manager. |
| **`web_tools.py`** | HTML-to-Markdown scraper that fetches web page URLs and strips scripts/styles/ads. | `web_fetch()`, `WEB_FETCH_DECLARATION`. |
| **`workflow_engine.py`** | Background autonomous workflow driver (Ralph Loop pattern) for long tasks. | `WorkflowEngine`, `start_workflow()`, `WORKFLOW_DECLARATION`. |

---

## 4. ⚡ `actions/` — Hardware, OS, Media & Desktop Tools

The `actions/` directory contains all direct OS, hardware, and desktop integrations:

| File | Functionality | Key Tools / Functions |
| :--- | :--- | :--- |
| **`background_monitor.py`** | Background process monitoring and alert triggers. | `manage_monitor()`. |
| **`browser_control.py`** | Chrome browser automation via WebSocket (click, type, navigate, scrape, scroll). | `browser_control()`, `BROWSER_CONTROL_DECLARATION`. |
| **`calorie_counter.py`** | Food and nutrition analysis via vision or text description. | `calorie_counter()`, `CALORIE_COUNTER_DECLARATION`. |
| **`code_helper.py`** | End-to-end code generation and full-stack project building. | `code_helper()`, `CODE_HELPER_DECLARATION`. |
| **`computer_control.py`** | Windows volume, mute, screen brightness, and WiFi toggling. | `computer_control()`, `COMPUTER_CONTROL_DECLARATION`. |
| **`computer_settings.py`** | Opens Windows control panels, settings pages, and system dialogs. | `computer_settings()`, `COMPUTER_SETTINGS_DECLARATION`. |
| **`desktop.py`** | Desktop icon management, folder creation, and file arrangement. | `desktop_control()`, `DESKTOP_CONTROL_DECLARATION`. |
| **`dev_agent.py`** | Development environment orchestrator (git status, linting, test runners). | `dev_agent()`, `DEV_AGENT_DECLARATION`. |
| **`file_controller.py`** | Advanced Windows file management (move, copy, rename, recycle bin via `send2trash`). | `file_controller()`, `FILE_CONTROLLER_DECLARATION`. |
| **`file_processor.py`** | Generation of PPTX presentations, DOCX reports, and PDF documents. | `file_processor()`, `FILE_PROCESSOR_DECLARATION`. |
| **`flight_finder.py`** | Real-time flight search across airlines, schedules, and live fares. | `flight_finder()`, `FLIGHT_FINDER_DECLARATION`. |
| **`game_updater.py`** | Autonomous game creation and asset generation engine. | `game_updater()`, `GAME_UPDATER_DECLARATION`. |
| **`open_app.py`** | Launches installed Windows applications by name or executable path. | `open_app()`, `OPEN_APP_DECLARATION`. |
| **`proactive.py`** | Proactive user check-ins and contextual suggestions based on time/status. | `proactive_check()`. |
| **`pushup_counter.py`** | Computer vision workout tracker using OpenCV pose estimation. | `pushup_counter()`, `PUSHUP_COUNTER_DECLARATION`. |
| **`reminder.py`** | Schedules audio and visual reminders. | `reminder()`, `REMINDER_DECLARATION`. |
| **`screen_processor.py`** | Captures desktop screenshots and performs Gemini vision analysis. | `screen_process()`, `SCREEN_PROCESS_DECLARATION`. |
| **`send_message.py`** | Sends automated WhatsApp and Telegram messages. | `send_message()`, `SEND_MESSAGE_DECLARATION`. |
| **`shadow_link.py`** | Connects live browser DOM to TITAN's neural reasoning engine. | `shadow_link()`, `SHADOW_LINK_DECLARATION`. |
| **`system_monitor.py`** | Real-time CPU, RAM, GPU, temperature, and battery telemetry. | `system_status()`, `SYSTEM_STATUS_DECLARATION`. |
| **`ui_automation.py`** | PyAutoGUI based mouse click, drag, scroll, and keyboard typing. | `ui_automation()`, `UI_AUTOMATION_DECLARATION`. |
| **`upload_video.py`** | Automated video uploading to YouTube with title/description tags. | `upload_video()`, `UPLOAD_VIDEO_DECLARATION`. |
| **`voice_face_id.py`** | Biometric security: YuNet face recognition + GMM voice verification. | `voice_face_id()`, `close_camera()`, `VOICE_FACE_ID_DECLARATION`. |
| **`weather_report.py`** | Fetches live weather conditions, forecasts, and temperature for any city. | `weather_action()`, `WEATHER_REPORT_DECLARATION`. |
| **`web_search.py`** | Multi-engine web search (Gemini Live Search + DuckDuckGo fallback). | `web_search()`, `WEB_SEARCH_DECLARATION`. |
| **`youtube_video.py`** | Searches and controls YouTube playback in browser. | `youtube_video()`, `YOUTUBE_VIDEO_DECLARATION`. |

---

## 5. 🔌 `plugins/` — Live Voice Extensible Plugins

Drop-in plugins automatically discovered on startup by `core/plugin_loader.py`:

| Plugin File | Capability Provided |
| :--- | :--- |
| **`_template.py`** | Standard template for authoring new drop-in plugins. |
| **`artifacts_builder.py`** | Builds interactive HTML/JS artifacts and dynamic web visualizations. |
| **`canvas_designer.py`** | Canvas-based graphic design and layout generator. |
| **`excel_engine.py`** | Openpyxl based Excel spreadsheet creation, formula insertion, and styling. |
| **`file_organizer.py`** | Smart file classification and sorting for messy Downloads/Desktop folders. |
| **`git_tools.py`** | Git version control commands (branch, commit, push, diff, merge). |
| **`meeting_insights.py`** | Summarizes meeting transcripts and generates action item tables. |
| **`research_synthesizer.py`**| Deep multi-source web research synthesizer with citations. |
| **`resume_builder.py`** | Generates professional tailored resumes in Markdown and DOCX. |
| **`theme_factory.py`** | Custom cyberpunk color palette and UI theme switcher for `ui.py`. |

---

## 6. 💾 `memory/` — Long-Term Memory, Security & Persistence

| File / Folder | Purpose |
| :--- | :--- |
| **`memory_manager.py`** | Manages persistent user preferences, facts, and conversation context across sessions. |
| **`config_manager.py`** | Reads and writes plugin toggles (`get_plugin_enabled()`, `set_plugin_enabled()`). |
| **`work_pad.py`** | Multi-page scratchpad notebook for intermediate research thoughts (`work_pad` tool). |
| **`long_term.json`** | Persistent storage of user profile, remembered facts, and habits. |
| **`goals.json`** | Durable JSON store for active and completed multi-round goals. |
| **`todo_state.json`** | Durable JSON store for the active checklist. |
| **`session_events/`** | Directory containing raw immutable JSONL session event logs. |
| **`face_detection_yunet.onnx`** | Neural ONNX model for high-speed face detection. |
| **`face_recognition_sface.onnx`**| Neural ONNX model for 128-d face embedding matching. |
| **`owner_face.npy`** | Biometric numpy embedding of the authenticated owner's face. |
| **`owner_voice_gmm.pkl`** | Biometric Gaussian Mixture Model of the owner's voice pitch/timbre. |
| **`security_config.json`** | Security policies for voice biometric lockout and confirmation gates. |

---

## 7. ⚙️ `config/` — API Keys & System Configuration

| File | Content & Purpose |
| :--- | :--- |
| **`api_keys.json`** | Stores Gemini API keys, search tokens, and third-party credentials. |

---

## 8. 🖥️ `dashboard/` — Web UI & Local Host Interface

Local web dashboard interface running on port `8000`/`8001`:
* Web UI frontend assets (HTML, CSS, JS)
* Live session activity viewer
* Real-time tool execution graphs

---

## 9. 🌐 `titan-extension/` — Chrome Extension & Neural Bridge

The browser extension connecting Chrome tabs to TITAN:
* **`manifest.json`**: Chrome MV3 Extension manifest.
* **`src/background/`**: Background service worker maintaining WebSocket connection to `shadow_bridge.py` (Port 8002).
* **`src/content/`**: Content scripts injecting DOM hooks for clicking, typing, scrolling, and page extraction.

---

## 10. 📚 `skills/` — 1,481+ On-Demand Skill Library

Houses structured domain knowledge in `SKILL.md` packages:
* **Top-Level Priority Skills:**
  * `skills/pptx/SKILL.md` (PowerPoint presentation generation)
  * `skills/docx/SKILL.md` (Word document generation)
  * `skills/xlsx/SKILL.md` (Spreadsheet creation)
  * `skills/pdf/SKILL.md` (PDF report creation)
  * `skills/claude-api/` (API integration patterns)
* **Playbooks & Extended Skills:** 1,480+ specialized skills in research, patent analysis, compliance, data analysis, and software engineering.

---

## 11. 🛠️ Complete 51 Tool Reference Map

| # | Tool Name | Category | Primary Function |
|---|:---|:---|:---|
| 1 | **`run_command`** | Execution | Runs PowerShell/Bash subprocess with Windows auto-resolution & UTF-8 pinning. |
| 2 | **`deep_think`** | Core | Enables high-depth reasoning mode for difficult problems. |
| 3 | **`shutdown_titan`** | Core | Gracefully exits TITAN and closes all background threads. |
| 4 | **`get_clock`** | Core | Returns live local date, time, weekday, and timezone right now. |
| 5 | **`system_status`** | Core | Live CPU, RAM, GPU, temperature, and battery telemetry. |
| 6 | **`todo_read`** | Planning | Reads the current active multi-step checklist. |
| 7 | **`todo_write`** | Planning | Creates or updates checklist items with status (pending/in_progress/completed). |
| 8 | **`set_goal`** | Planning | Sets a persistent goal that drives multi-round execution. |
| 9 | **`complete_goal`** | Planning | Marks an active goal as completed. |
| 10 | **`schedule`** | Planning | Sets a one-shot countdown timer or recurring cron schedule. |
| 11 | **`ask_user_question`**| Interaction | Prompts user with interactive multiple-choice options. |
| 12 | **`enter_plan_mode`** | Planning | Enters plan-first mode to prepare an architecture document. |
| 13 | **`exit_plan_mode`** | Planning | Exits plan mode after receiving user approval. |
| 14 | **`workflow_start`** | Planning | Starts a multi-step background worker loop. |
| 15 | **`reminder`** | Tasks | Sets visual and voice reminders. |
| 16 | **`work_pad`** | Memory | Manages multi-page persistent scratchpad notes. |
| 17 | **`invoke_subagent`** | Subagents | Spawns a dedicated child worker subagent (e.g. coder, researcher). |
| 18 | **`list_subagents`** | Subagents | Lists all active and recent subagents. |
| 19 | **`send_subagent_message`** | Subagents | Sends steering instructions to a running subagent. |
| 20 | **`interrupt_subagent`** | Subagents | Immediately aborts a running subagent. |
| 21 | **`job_list`** | Jobs | Lists all running and recent background jobs. |
| 22 | **`job_output`** | Jobs | Reads incremental output from a background job. |
| 23 | **`job_kill`** | Jobs | Kills a long-running background task. |
| 24 | **`read_file`** | File Ops | Reads file content with line numbers and windowing. |
| 25 | **`write_file`** | File Ops | Writes or overwrites a file on disk atomically. |
| 26 | **`str_replace_editor`** | File Ops | Surgically replaces a unique substring without corrupting files. |
| 27 | **`grep_search`** | Code Intel | Fast regex or literal search across workspace files. |
| 28 | **`glob_search`** | Code Intel | Finds files matching wildcard patterns (e.g. `*.py`, `*.json`). |
| 29 | **`python_eval`** | Runtime | Executes raw Python code in an isolated subprocess with output capture. |
| 30 | **`code_helper`** | Code Intel | Builds full-stack applications, websites, and scripts. |
| 31 | **`dev_agent`** | Code Intel | Development environment manager (Git, test suites, linter). |
| 32 | **`load_skill`** | Extensibility | Loads on-demand `SKILL.md` instructions and scripts. |
| 33 | **`web_search`** | Web | Live web search via Gemini Live Search or DuckDuckGo. |
| 34 | **`web_fetch`** | Web | Fetches any URL and extracts clean, readable Markdown. |
| 35 | **`open_app`** | OS Control | Launches any Windows application by name or path. |
| 36 | **`computer_control`** | OS Control | Controls volume, mute, brightness, and WiFi. |
| 37 | **`computer_settings`** | OS Control | Opens Windows Settings panels and system dialogues. |
| 38 | **`desktop_control`** | OS Control | Manages desktop files, icons, and folders. |
| 39 | **`file_controller`** | OS Control | Moves, copies, renames, and safely recycles files. |
| 40 | **`file_processor`** | Office Ops | Generates PPTX presentations, DOCX reports, and PDFs. |
| 41 | **`ui_automation`** | OS Control | PyAutoGUI mouse clicks, drags, scrolling, and keystrokes. |
| 42 | **`manage_monitor`** | OS Control | Monitors background processes and triggers alert notifications. |
| 43 | **`browser_control`** | Browser | Chrome browser automation (click, type, navigate, scrape). |
| 44 | **`shadow_link`** | Browser | Connects live browser DOM to the neural reasoning pipeline. |
| 45 | **`send_message`** | Social | Sends automated WhatsApp and Telegram messages. |
| 46 | **`youtube_video`** | Media | Searches and plays YouTube videos in browser. |
| 47 | **`game_updater`** | Specialized | Autonomous game creation and asset update engine. |
| 48 | **`flight_finder`** | Specialized | Live flight search, airline pricing, and schedule finder. |
| 49 | **`screen_process`** | Vision | Takes screenshot and analyzes desktop state with Gemini Vision. |
| 50 | **`weather_report`** | Information | Live weather conditions, forecasts, and temperatures. |
| 51 | **`voice_face_id`** | Security | Biometric face recognition (YuNet/SFace) & voice timbre verification. |

---

*Generated by TITAN Mark-L Autonomous System Architect.*
