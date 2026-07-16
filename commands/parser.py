from .launcher import launch_app
from .workspace import open_workspace
from .search import find_file
from .ai_writer import write_file_ai

def parse_and_execute(command: str) -> str:
    """
    Parse the incoming text command and route it to the appropriate handler.
    """
    cmd = command.strip().lower()
    
    if not cmd:
        return "Empty command."

    # Plugin / Action routing
    if cmd.startswith("open"):
        if "workspace" in cmd:
            return open_workspace(cmd)
        else:
            return launch_app(cmd)
            
    elif cmd.startswith("find"):
        return find_file(cmd)
        
    elif cmd.startswith("write"):
        return write_file_ai(cmd)
        
    elif cmd.startswith("create"):
        # Simple file creation
        filename = cmd.replace("create ", "").strip()
        try:
            with open(filename, "w") as f:
                f.write("")
            return f"Created file: {filename}"
        except Exception as e:
            return f"Error creating file: {e}"
            
    else:
        return f"Command not recognized: {command}\nTry 'open', 'find', 'write', or 'create'."
