import customtkinter as ctk

class AssistantWidget(ctk.CTk):
    def __init__(self, command_callback):
        super().__init__()
        
        self.command_callback = command_callback

        # Window configuration
        self.title("Assistant")
        self.geometry("350x150")
        
        # Make it float at the bottom right
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = screen_width - 370
        y = screen_height - 220
        self.geometry(f"+{x}+{y}")
        
        # Properties
        self.attributes("-topmost", True)  # Always on top
        self.overrideredirect(True)       # Borderless (no title bar)
        
        # Styling
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Frame
        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Draggable binding
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<B1-Motion>", self.do_move)
        
        # Label
        self.title_label = ctk.CTkLabel(self.frame, text="AI Assistant", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=(10, 5))
        
        # Input Field
        self.entry = ctk.CTkEntry(self.frame, placeholder_text="> type command...", width=300)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus()
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.frame, text="Status: Ready", font=("Arial", 10), text_color="gray")
        self.status_label.pack(pady=(0, 10))

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_enter(self, event):
        command = self.entry.get()
        if command:
            self.status_label.configure(text="Processing...")
            self.update()
            
            # Execute the command via callback
            result = self.command_callback(command)
            
            self.status_label.configure(text=f"Status: {result}")
            self.entry.delete(0, 'end')

    def run(self):
        self.mainloop()
