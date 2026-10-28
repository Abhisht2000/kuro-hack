"""A small desktop counter with an optional vertical mouse mover.

Install the dependency first:
    python3 -m pip install -r requirements.txt
Run with:
    python3 autocounter.py
"""

from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import pyautogui


class AutoCounterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Auto Counter & Mouse Mover")
        self.resizable(False, False)
        self.configure(padx=28, pady=24)

        self.running = False
        self.stop_event = threading.Event()
        self.counter = 0
        self.direction = 1
        self.count_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="Ready")
        self.move_mouse_var = tk.BooleanVar(value=True)
        self.interval_var = tk.StringVar(value="0.10")
        self.distance_var = tk.StringVar(value="20")

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        ttk.Label(self, text="COUNT", font=("Helvetica", 11, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 4)
        )
        ttk.Label(self, textvariable=self.count_var, font=("Helvetica", 42, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(0, 20)
        )

        ttk.Checkbutton(self, text="Move mouse up and down", variable=self.move_mouse_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )
        ttk.Label(self, text="Interval (seconds)").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.interval_var, width=10).grid(row=3, column=1, sticky="e", pady=4)
        ttk.Label(self, text="Mouse distance (pixels)").grid(row=4, column=0, sticky="w", pady=4)
        ttk.Entry(self, textvariable=self.distance_var, width=10).grid(row=4, column=1, sticky="e", pady=4)

        self.start_button = ttk.Button(self, text="Start", command=self.start)
        self.start_button.grid(row=5, column=0, sticky="ew", pady=(20, 8), padx=(0, 4))
        self.stop_button = ttk.Button(self, text="Stop", command=self.stop, state="disabled")
        self.stop_button.grid(row=5, column=1, sticky="ew", pady=(20, 8), padx=(4, 0))
        ttk.Button(self, text="Reset count", command=self.reset).grid(
            row=6, column=0, columnspan=2, sticky="ew"
        )
        ttk.Label(self, textvariable=self.status_var, foreground="#555").grid(
            row=7, column=0, columnspan=2, pady=(16, 0)
        )
        ttk.Label(
            self,
            text="Move the cursor to a screen corner to trigger PyAutoGUI's emergency stop.",
            foreground="#777",
            wraplength=340,
            justify="center",
        ).grid(row=8, column=0, columnspan=2, pady=(8, 0))

    def start(self) -> None:
        try:
            interval = float(self.interval_var.get())
            distance = int(self.distance_var.get())
            if interval <= 0 or distance < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Use a positive interval and a non-negative pixel distance.")
            return

        self.running = True
        self.stop_event.clear()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Running — press Stop when you're done")
        threading.Thread(target=self._run, args=(interval, distance), daemon=True).start()

    def _run(self, interval: float, distance: int) -> None:
        try:
            while not self.stop_event.is_set():
                self.counter += 1
                self.after(0, self.count_var.set, str(self.counter))
                if self.move_mouse_var.get() and distance:
                    x, y = pyautogui.position()
                    height = pyautogui.size().height
                    target_y = max(0, min(height - 1, y + self.direction * distance))
                    pyautogui.moveTo(x, target_y, duration=min(interval * 0.6, 0.2))
                    self.direction *= -1
                self.stop_event.wait(interval)
        except pyautogui.FailSafeException:
            self.after(0, self.status_var.set, "Emergency stop activated.")
        except Exception as error:
            self.after(0, messagebox.showerror, "Stopped", str(error))
        finally:
            self.after(0, self._set_stopped)

    def stop(self) -> None:
        self.stop_event.set()
        self.status_var.set("Stopping…")

    def _set_stopped(self) -> None:
        self.running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        if self.status_var.get() == "Stopping…":
            self.status_var.set("Stopped")

    def reset(self) -> None:
        if not self.running:
            self.counter = 0
            self.count_var.set("0")

    def on_close(self) -> None:
        self.stop_event.set()
        self.destroy()


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    AutoCounterApp().mainloop()
