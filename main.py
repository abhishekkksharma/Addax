from ui.widget import AssistantWidget
from commands.parser import parse_and_execute

def main():
    # Initialize the UI widget and pass the command parser as the callback
    widget = AssistantWidget(command_callback=parse_and_execute)
    
    # Run the application loop
    widget.run()

if __name__ == "__main__":
    main()
