# Desktop AI Assistant

A lightweight, customizable AI assistant for Windows built with Python. It features a persistent, draggable UI at the bottom right of your screen and automates your daily workflow via simple text commands.

## Features

- **Application Launcher**: Open your favorite tools quickly (e.g., `open chrome`, `open vscode`).
- **Workspaces**: Launch an entire environment containing multiple apps and web pages at once with a single command (e.g., `open dsa workspace`).
- **File Finder**: Search your files across the system rapidly (e.g., `find resume`).
- **File Creation**: Quickly scaffold empty files (e.g., `create notes.txt`).
- **AI Integration (Optional)**: Automatically write drafts and content using a local LLM through Ollama (e.g., `write a python script for sorting`).

## Project Structure

```text
assistant/
├── main.py                     # Entry point for the application
├── requirements.txt            # Python dependencies
├── ui/
│   └── widget.py               # The floating CustomTkinter UI
├── commands/                   # Command logic and handlers
│   ├── parser.py               # Routes commands to correct modules
│   ├── launcher.py             # Opens desktop applications
│   ├── workspace.py            # Opens predefined workspaces
│   ├── search.py               # Searches for files on disk
│   └── ai_writer.py            # Interfaces with local Ollama models
└── config/
    └── workspaces.json         # Workspace configurations (JSON)
```

## Prerequisites

- Windows 11 (or 10)
- Python 3.11+
- [Ollama](https://ollama.com/) (Optional, for local AI writing features)

## Installation

1. Navigate to the project directory:
   ```bash
   cd assistant
   ```

2. Create a virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application by running:
   ```bash
   python main.py
   ```

2. The AI assistant widget will appear in the bottom right corner of your screen. You can drag it by clicking and holding the UI.

3. Type your commands in the text box and hit **Enter**.

### Example Commands

- **Open applications**:
  - `open chrome`
  - `open vscode and chrome`
- **Open a workspace** (as defined in `config/workspaces.json`):
  - `open dsa workspace`
  - `open development workspace`
- **Search for files**:
  - `find my_project_report`
- **Create a text file**:
  - `create scratchpad.md`
- **Generate text with AI**:
  - `write a README template`

## Configuring Workspaces

You can customize your environments by editing `config/workspaces.json`. 

```json
{
  "dsa": {
    "apps": ["code", "chrome"],
    "urls": ["https://leetcode.com"]
  }
}
```
In this example, typing `open dsa workspace` will launch VS Code, Chrome, and open LeetCode in your default browser.

## Customization and Expansion

The assistant uses a flexible **plugin system**. If you want to add new functionality (like controlling music or sending emails), simply:
1. Create a new handler in the `commands/` folder.
2. Hook it up in `commands/parser.py`.
