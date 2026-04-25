import tkinter as tk
from tkinter import scrolledtext, messagebox

from shared_buffer import SharedBuffer
from producer import Producer
from consumer import Consumer
from logger_util import logger


class ThreadSyncVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Thread Synchronization Visualizer")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        self.buffer = None
        self.producers = []
        self.consumers = []
        self.total_produced = 0
        self.total_consumed = 0

        # Main container
        main_frame = tk.Frame(root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(main_frame, text="Producer-Consumer Thread Synchronization Visualizer",
                               font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=(0,10))

        # Configuration Section
        config_frame = tk.LabelFrame(main_frame, text="Configuration", font=("Arial", 12, "bold"),
                                     bg='#f0f0f0', fg='#333', padx=10, pady=10)
        config_frame.pack(fill=tk.X, pady=(0,10))

        self.control_frame = tk.Frame(config_frame, bg='#f0f0f0')
        self.control_frame.pack()

        tk.Label(self.control_frame, text="Producers:", bg='#f0f0f0').grid(row=0, column=0, padx=4, sticky='e')
        self.producer_spin = tk.Spinbox(self.control_frame, from_=1, to=10, width=5)
        self.producer_spin.grid(row=0, column=1, padx=4)
        self.producer_spin.delete(0, tk.END)
        self.producer_spin.insert(0, "2")

        tk.Label(self.control_frame, text="Consumers:", bg='#f0f0f0').grid(row=0, column=2, padx=4, sticky='e')
        self.consumer_spin = tk.Spinbox(self.control_frame, from_=1, to=10, width=5)
        self.consumer_spin.grid(row=0, column=3, padx=4)
        self.consumer_spin.delete(0, tk.END)
        self.consumer_spin.insert(0, "2")

        tk.Label(self.control_frame, text="Buffer Size:", bg='#f0f0f0').grid(row=0, column=4, padx=4, sticky='e')
        self.buffer_spin = tk.Spinbox(self.control_frame, from_=1, to=20, width=5)
        self.buffer_spin.grid(row=0, column=5, padx=4)
        self.buffer_spin.delete(0, tk.END)
        self.buffer_spin.insert(0, "5")

        tk.Label(self.control_frame, text="Producer Speed:", bg='#f0f0f0').grid(row=0, column=6, padx=4, sticky='e')
        self.producer_scale = tk.Scale(self.control_frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=100, bg='#f0f0f0')
        self.producer_scale.grid(row=0, column=7, padx=4)
        self.producer_scale.set(0.7)

        tk.Label(self.control_frame, text="Consumer Speed:", bg='#f0f0f0').grid(row=0, column=8, padx=4, sticky='e')
        self.consumer_scale = tk.Scale(self.control_frame, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL, length=100, bg='#f0f0f0')
        self.consumer_scale.grid(row=0, column=9, padx=4)
        self.consumer_scale.set(1.0)

        # Controls Section
        controls_frame = tk.LabelFrame(main_frame, text="Controls", font=("Arial", 12, "bold"),
        bg='#f0f0f0', fg='#333', padx=10, pady=10)
        controls_frame.pack(fill=tk.X, pady=(0,10))

        button_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        button_frame.pack()
        self.start_button = tk.Button(button_frame, text="Start", width=12, command=self.on_start, bg='#4CAF50', fg='white', font=("Arial", 10, "bold"))
        self.start_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop", width=12, command=self.on_stop, state=tk.DISABLED, bg='#f44336', fg='white', font=("Arial", 10, "bold"))
        self.stop_button.grid(row=0, column=1, padx=10)

        self.reset_button = tk.Button(button_frame, text="Reset", width=12, command=self.on_reset, bg='#2196F3', fg='white', font=("Arial", 10, "bold"))
        self.reset_button.grid(row=0, column=2, padx=10)

        # Buffer Visualization Section
        buffer_section = tk.LabelFrame(main_frame, text="Buffer Visualization", font=("Arial", 12, "bold"),
                                       bg='#f0f0f0', fg='#333', padx=10, pady=10)
        buffer_section.pack(fill=tk.X, pady=(0,10))

        self.buffer_canvas = tk.Canvas(buffer_section, width=800, height=60, bg='white', relief=tk.SUNKEN, bd=2)
        self.buffer_canvas.pack(fill=tk.X)

        # Initialize with default buffer display
        self.create_buffer_display(5)

        # Statistics Section
        stats_frame = tk.LabelFrame(main_frame, text="Statistics", font=("Arial", 12, "bold"),
                                    bg='#f0f0f0', fg='#333', padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=(0,10))

        self.stats_frame = tk.Frame(stats_frame, bg='#f0f0f0')
        self.stats_frame.pack()

        self.produced_label = tk.Label(self.stats_frame, text="Total Produced: 0", bg='#f0f0f0', font=("Arial", 10))
        self.produced_label.grid(row=0, column=0, padx=10, pady=2, sticky='w')

        self.consumed_label = tk.Label(self.stats_frame, text="Total Consumed: 0", bg='#f0f0f0', font=("Arial", 10))
        self.consumed_label.grid(row=0, column=1, padx=10, pady=2, sticky='w')

        self.buffer_usage_label = tk.Label(self.stats_frame, text="Buffer Usage: 0/0", bg='#f0f0f0', font=("Arial", 10))
        self.buffer_usage_label.grid(row=0, column=2, padx=10, pady=2, sticky='w')

        # Logs Section
        logs_frame = tk.LabelFrame(main_frame, text="Logs", font=("Arial", 12, "bold"),
                                   bg='#f0f0f0', fg='#333', padx=10, pady=10)
        logs_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))

        self.log_area = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, state=tk.DISABLED,
                                                  bg='white', fg='#333', font=("Courier", 10))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Thread Status Section
        status_frame = tk.LabelFrame(main_frame, text="Thread Status", font=("Arial", 12, "bold"),
                                     bg='#f0f0f0', fg='#333', padx=10, pady=10)
        status_frame.pack(fill=tk.X)

        self.status_frame = tk.Frame(status_frame, bg='#f0f0f0')
        self.status_frame.pack(fill=tk.X)

        self.status_labels = {}
        self._last_logged = 0
        self.poll_logs()

    def on_start(self):
        self.log("Start button pressed")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        try:
            num_producers = int(self.producer_spin.get())
            num_consumers = int(self.consumer_spin.get())
            buffer_size = int(self.buffer_spin.get())
            producer_sleep = float(self.producer_scale.get())
            consumer_sleep = float(self.consumer_scale.get())

            if num_producers < 1 or num_consumers < 1 or buffer_size < 1 or producer_sleep <= 0 or consumer_sleep <= 0:
                raise ValueError("Values must be positive")

        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid values.\n{e}")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            return

        self.buffer = SharedBuffer(maxsize=buffer_size)
        self.create_buffer_display(self.buffer.maxsize)

        self.producers = [Producer(self.buffer, self, sleep_time=producer_sleep, producer_id=i + 1) for i in range(num_producers)]
        self.consumers = [Consumer(self.buffer, self, sleep_time=consumer_sleep, consumer_id=i + 1) for i in range(num_consumers)]

        for p in self.producers:
            p.start()

        for c in self.consumers:
            c.start()

        self.create_status_display()

        logger.log(f"Started {num_producers} producers, {num_consumers} consumers, buffer size {buffer_size}, producer sleep {producer_sleep:.1f}s, consumer sleep {consumer_sleep:.1f}s")

    def on_stop(self):
        self.log("Stop button pressed")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        for p in self.producers:
            p.stop()

        for c in self.consumers:
            c.stop()

        for p in self.producers:
            p.join(timeout=1)

        for c in self.consumers:
            c.join(timeout=1)

        logger.log("Stopped producers and consumers")

    def on_reset(self):
        self.log("Reset button pressed")

        # Stop any running threads
        for p in self.producers:
            if p.is_alive():
                p.stop()
        for c in self.consumers:
            if c.is_alive():
                c.stop()

        for p in self.producers:
            p.join(timeout=1)
        for c in self.consumers:
            c.join(timeout=1)

        # Clear logs
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

        # Reset buffer visualization
        self.buffer_canvas.delete("all")
        self.create_buffer_display(5)
        self.buffer = None

        # Reset thread status display
        for label in self.status_labels.values():
            label.config(text="", bg='lightgray')

        # Clear lists
        self.producers = []
        self.consumers = []
        self.status_labels = {}

        # Reset counters
        self.total_produced = 0
        self.total_consumed = 0
        self.update_statistics()

        # Reset buttons
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        logger.log("Simulation reset")

    def update_log(self, produced=None, consumed=None, action=None):
        if action == 'produce' and produced is not None:
            self.total_produced += 1
            self.log(f"Produced: {produced}")
        elif action == 'consume' and consumed is not None:
            self.total_consumed += 1
            self.log(f"Consumed: {consumed}")

    def create_buffer_display(self, maxsize):
        self.buffer_canvas.delete("all")
        self.slot_rects = []
        canvas_width = 800
        slot_width = canvas_width / maxsize
        for i in range(maxsize):
            x1 = i * slot_width
            x2 = (i + 1) * slot_width
            rect = self.buffer_canvas.create_rectangle(x1, 10, x2, 50, fill='lightgray', outline='black')
            text = self.buffer_canvas.create_text((x1 + x2)/2, 30, text="Empty", font=("Arial", 10))
            self.slot_rects.append((rect, text))

    def create_status_display(self):
        for widget in self.status_frame.winfo_children():
            widget.destroy()

        self.status_labels = {}

        row = 0
        for p in self.producers:
            label = tk.Label(self.status_frame, text=f"{p.name}: {p.state}", anchor='w', width=30, bg='lightgray', fg='black', font=("Arial", 10))
            label.grid(row=row, column=0, padx=4, pady=2, sticky='w')
            self.status_labels[p.name] = label
            row += 1

        for c in self.consumers:
            label = tk.Label(self.status_frame, text=f"{c.name}: {c.state}", anchor='w', width=30, bg='lightgray', fg='black', font=("Arial", 10))
            label.grid(row=row, column=0, padx=4, pady=2, sticky='w')
            self.status_labels[c.name] = label
            row += 1

    def update_buffer_display(self):
        if not hasattr(self, 'slot_rects') or not self.slot_rects:
            return

        if self.buffer:
            snapshot = self.buffer.get_buffer_snapshot()
        else:
            snapshot = []

        for i, (rect, text) in enumerate(self.slot_rects):
            if i < len(snapshot):
                self.buffer_canvas.itemconfig(rect, fill='#4CAF50')  # Green for occupied
                self.buffer_canvas.itemconfig(text, text=str(snapshot[i]))
            else:
                self.buffer_canvas.itemconfig(rect, fill='white')  # White for empty
                self.buffer_canvas.itemconfig(text, text="Empty")

    def update_thread_status_display(self):
        if not self.status_labels:
            return

        state_colors = {
            'RUNNING': '#4CAF50',  # Green
            'WAITING': '#FF9800',  # Orange
            'STOPPED': '#f44336'   # Red
        }

        for p in self.producers:
            label = self.status_labels.get(p.name)
            if label:
                color = state_colors.get(p.state, 'white')
                label.config(text=f"{p.name}: {p.state}", bg=color, fg='white')

        for c in self.consumers:
            label = self.status_labels.get(c.name)
            if label:
                color = state_colors.get(c.state, 'white')
                label.config(text=f"{c.name}: {c.state}", bg=color, fg='white')

    def update_statistics(self):
        self.produced_label.config(text=f"Total Produced: {self.total_produced}")
        self.consumed_label.config(text=f"Total Consumed: {self.total_consumed}")
        if self.buffer:
            usage = len(self.buffer.get_buffer_snapshot())
            max_size = self.buffer.maxsize
            self.buffer_usage_label.config(text=f"Buffer Usage: {usage}/{max_size}")
        else:
            self.buffer_usage_label.config(text="Buffer Usage: 0/0")

    def poll_logs(self):
        all_logs = logger.get_recent(100)
        if all_logs:
            new_logs = all_logs[self._last_logged:]
            for entry in new_logs:
                self.log(entry)
            self._last_logged = len(all_logs)

        self.update_buffer_display()
        self.update_thread_status_display()
        self.update_statistics()
        self.root.after(500, self.poll_logs)


def main():
    root = tk.Tk()
    app = ThreadSyncVisualizer(root)
    root.mainloop()


if __name__ == '__main__':
    main()
