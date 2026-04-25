import datetime
import threading


class LoggerUtil:
    def __init__(self, max_entries=1000, echo_console=True):
        self.max_entries = max_entries
        self.echo_console = echo_console
        self._logs = []
        self._lock = threading.Lock()

    def _format(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"[{timestamp}] {message}"

    def log(self, message):
        entry = self._format(message)
        with self._lock:
            self._logs.append(entry)
            if len(self._logs) > self.max_entries:
                self._logs.pop(0)

        if self.echo_console:
            print(entry)

    def get_recent(self, count=20):
        with self._lock:
            return self._logs[-count:]


logger = LoggerUtil()
