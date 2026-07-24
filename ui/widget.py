import math
import os
import queue
import threading
import tkinter as tk

from PIL import Image, ImageTk


class AssistantWidget(tk.Tk):
    """
    Transparent desktop pet inspired by editor pets.
    Double-click to speak, drag to move, and animate only around user actions.
    """

    PET_SIZE = 96
    WINDOW_W = 260
    WINDOW_H = 190
    TRANSPARENT = "#010101"
    PET_CENTER_X = 130
    PET_CENTER_Y = 125

    def __init__(self, command_callback):
        super().__init__()

        self.command_callback = command_callback
        self.title("Desktop Pet")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-transparentcolor", self.TRANSPARENT)
        self.configure(bg=self.TRANSPARENT)

        self._drag_x = 0
        self._drag_y = 0
        self._busy = False
        self._dragging = False
        self._motion_job = None
        self._busy_job = None
        self._bubble_job = None
        self._result_queue = queue.Queue()

        self._frames = {}
        self._static_frame = None
        self.pet_id = None
        self.shadow_id = None
        self.bubble_id = None
        self.text_id = None

        self._place_window()
        self._build_canvas()
        self._load_pet_frames()
        self._draw_pet(self._static_frame)
        self._bind_interactions()

        self.after(100, self._drain_results)
        self.after(700, lambda: self._show_bubble("Double-click me", auto_hide=2200))

    def _place_window(self):
        self.update_idletasks()
        x = self.winfo_screenwidth() - self.WINDOW_W - 24
        y = self.winfo_screenheight() - self.WINDOW_H - 70
        self.geometry(f"{self.WINDOW_W}x{self.WINDOW_H}+{x}+{y}")

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self,
            width=self.WINDOW_W,
            height=self.WINDOW_H,
            bg=self.TRANSPARENT,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_interactions(self):
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", lambda _event: self._start_voice())
        self.canvas.bind("<Enter>", lambda _event: self._play_motion("greet"))
        self.canvas.bind("<Leave>", lambda _event: self._hide_bubble(delay=900))
        self.canvas.bind("<Button-3>", lambda _event: self._show_bubble("Double-click to speak"))

    def _load_pet_frames(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        png_path = os.path.join(base_dir, "pet.gif")

        if os.path.exists(png_path):
            source = Image.open(png_path).convert("RGBA")
        else:
            source = self._fallback_pet_image()

        source.thumbnail((self.PET_SIZE, self.PET_SIZE), Image.LANCZOS)
        self._static_frame = ImageTk.PhotoImage(source)
        self._frames = {
            "greet": self._make_motion_frames(source, count=12, bounce=4, tilt=5, squash=0.025),
            "listen": self._make_motion_frames(source, count=18, bounce=6, tilt=3, squash=0.035),
            "think": self._make_motion_frames(source, count=20, bounce=3, tilt=7, squash=0.02),
            "success": self._make_motion_frames(source, count=14, bounce=8, tilt=4, squash=0.045),
            "error": self._make_motion_frames(source, count=10, bounce=1, tilt=10, squash=0.01),
        }

    def _fallback_pet_image(self):
        image = Image.new("RGBA", (self.PET_SIZE, self.PET_SIZE), (0, 0, 0, 0))
        import PIL.ImageDraw as ImageDraw

        draw = ImageDraw.Draw(image)
        cx = self.PET_SIZE // 2
        cy = self.PET_SIZE // 2
        draw.ellipse((cx - 34, cy - 31, cx + 34, cy + 34), fill="#ffd86b", outline="#f3a928", width=3)
        draw.ellipse((cx - 13, cy - 10, cx - 6, cy - 3), fill="#2f241c")
        draw.ellipse((cx + 6, cy - 10, cx + 13, cy - 3), fill="#2f241c")
        draw.polygon((cx - 7, cy + 7, cx + 7, cy + 7, cx, cy + 15), fill="#ff8a3d")
        return image

    def _make_motion_frames(self, source, *, count, bounce, tilt, squash):
        frames = []
        for index in range(count):
            t = index / max(count - 1, 1)
            wave = math.sin(t * math.pi)
            wobble = math.sin(t * math.pi * 2)
            scale_x = 1.0 + squash * wave
            scale_y = 1.0 - squash * wave
            width = max(1, int(source.width * scale_x))
            height = max(1, int(source.height * scale_y))
            sprite = source.resize((width, height), Image.LANCZOS)
            sprite = sprite.rotate(tilt * wobble, resample=Image.BICUBIC, expand=True)

            canvas = Image.new("RGBA", (self.PET_SIZE + 28, self.PET_SIZE + 28), (0, 0, 0, 0))
            x = (canvas.width - sprite.width) // 2
            y = (canvas.height - sprite.height) // 2 - int(bounce * wave)
            canvas.paste(sprite, (x, y), sprite)
            frames.append(ImageTk.PhotoImage(canvas))
        return frames

    def _draw_pet(self, frame):
        if self.shadow_id is None:
            self.shadow_id = self.canvas.create_oval(90, 158, 170, 171, fill="#000000", outline="", stipple="gray50")
        if self.pet_id is None:
            self.pet_id = self.canvas.create_image(self.PET_CENTER_X, self.PET_CENTER_Y, image=frame)
        else:
            self.canvas.itemconfig(self.pet_id, image=frame)

    def _play_motion(self, name, *, loop=False, on_done=None):
        if self._motion_job:
            self.after_cancel(self._motion_job)
            self._motion_job = None

        frames = self._frames.get(name) or []
        if not frames:
            if on_done:
                on_done()
            return

        def step(index=0):
            self._draw_pet(frames[index])
            next_index = index + 1
            if next_index < len(frames):
                self._motion_job = self.after(33, lambda: step(next_index))
            elif loop:
                self._motion_job = self.after(33, lambda: step(0))
            else:
                self._draw_pet(self._static_frame)
                self._motion_job = None
                if on_done:
                    on_done()

        step()

    def _start_busy_motion(self, name):
        self._stop_busy_motion()

        def pulse():
            if not self._busy:
                self._draw_pet(self._static_frame)
                return
            self._play_motion(name, on_done=pulse)

        pulse()

    def _stop_busy_motion(self):
        if self._busy_job:
            self.after_cancel(self._busy_job)
            self._busy_job = None

    def _show_bubble(self, text, *, auto_hide=None):
        self._cancel_bubble_timer()
        display = text if len(text) <= 120 else text[:117] + "..."
        lines = self._wrap_text(display, limit=38)
        height = 28 + (len(lines) - 1) * 15
        y2 = 18 + height

        if self.bubble_id is None:
            self.bubble_id = self._rounded_rect(22, 12, 238, y2, radius=13, fill="#fff8dc", outline="#e7d7a8")
            self.text_id = self.canvas.create_text(
                130,
                25,
                text="\n".join(lines),
                fill="#362717",
                font=("Segoe UI", 9),
                width=190,
                justify="center",
                anchor="n",
            )
        else:
            self._update_rounded_rect(self.bubble_id, 22, 12, 238, y2, radius=13)
            self.canvas.itemconfig(self.text_id, text="\n".join(lines))
            self.canvas.itemconfig(self.bubble_id, state=tk.NORMAL)
            self.canvas.itemconfig(self.text_id, state=tk.NORMAL)

        self.canvas.tag_raise(self.bubble_id)
        self.canvas.tag_raise(self.text_id)

        if auto_hide:
            self._bubble_job = self.after(auto_hide, self._hide_bubble)

    def _hide_bubble(self, delay=0):
        self._cancel_bubble_timer()
        if delay:
            self._bubble_job = self.after(delay, self._hide_bubble)
            return
        if self.bubble_id is not None:
            self.canvas.itemconfig(self.bubble_id, state=tk.HIDDEN)
            self.canvas.itemconfig(self.text_id, state=tk.HIDDEN)

    def _cancel_bubble_timer(self):
        if self._bubble_job:
            self.after_cancel(self._bubble_job)
            self._bubble_job = None

    def _wrap_text(self, text, *, limit):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > limit and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
        return lines or [""]

    def _rounded_rect(self, x1, y1, x2, y2, *, radius, **kwargs):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def _update_rounded_rect(self, item_id, x1, y1, x2, y2, *, radius):
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
            x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2,
            x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1,
        ]
        self.canvas.coords(item_id, *points)

    def _start_voice(self):
        if self._busy or self._dragging:
            return
        self._busy = True
        self._show_bubble("Listening...")
        self._start_busy_motion("listen")
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def _voice_worker(self):
        from ui.voice import listen_and_transcribe

        command = listen_and_transcribe()
        if not command:
            self._result_queue.put(("done", "I did not hear that.", "error"))
            return
        self._result_queue.put(("message", f"Heard: {command}", "think"))
        self._execute_command(command)

    def _execute_command(self, command: str):
        try:
            result = self.command_callback(command)
        except Exception as exc:
            result = f"Command failed: {exc}"
        self._result_queue.put(("done", result, "success"))

    def _drain_results(self):
        try:
            while True:
                kind, message, state = self._result_queue.get_nowait()
                if kind == "message":
                    self._show_bubble(message)
                    self._start_busy_motion(state)
                else:
                    self._busy = False
                    self._show_bubble(message, auto_hide=4200)
                    self._play_motion(state)
        except queue.Empty:
            pass
        self.after(100, self._drain_results)

    def _on_press(self, event):
        self._dragging = False
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _on_drag(self, event):
        self._dragging = True
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _on_release(self, _event):
        if self._dragging:
            self._play_motion("greet")
        self.after(120, lambda: setattr(self, "_dragging", False))

    def run(self):
        self.mainloop()
