# Desktop AI Assistant

A lightweight Windows desktop assistant with a transparent interactive pet UI, voice input, and OpenRouter-backed LLM routing.

## Features

- Transparent pet widget with no control-panel background.
- Double-click voice commands with smooth non-blocking animation.
- Event-based pet reactions for hover, listening, thinking, success, and errors.
- Application launcher, e.g. `open chrome`, `open vscode`.
- Workspace launcher from `config/workspaces.json`, e.g. `open dsa workspace`.
- File finder, e.g. `find resume`.
- File creation, e.g. `create notes.txt`.
- AI writing and document Q&A through OpenRouter, not Ollama.

## Setup

```powershell
cd assistant
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Set your OpenRouter key before starting the app:

```powershell
$env:OPENROUTER_API_KEY="your_key_here"
```

Optional model override:

```powershell
$env:OPENROUTER_MODEL="openai/gpt-4o-mini"
```

## Run

```powershell
python main.py
```

The pet appears near the bottom-right of the screen. Drag it to move it, or double-click the pet to speak.

## Packaged EXE

Build the Windows executable:

```powershell
.\build_exe.bat
```

Run the packaged app with one terminal command:

```powershell
.\run_pet.bat
```

The executable lives at:

```text
dist\DesktopPetAssistant\DesktopPetAssistant.exe
```

## Example Commands

- `open chrome`
- `open vscode and chrome`
- `open dsa workspace`
- `find project report`
- `create scratchpad.md`
- `write a README for my movie recommendation project to README.md`
- `summarize report.pdf`
- `analyze data.csv`

## Workspaces

Edit `config/workspaces.json`:

```json
{
  "dsa": {
    "apps": ["code", "chrome"],
    "urls": ["https://leetcode.com"]
  }
}
```

`open dsa workspace` launches the configured apps and URLs.
