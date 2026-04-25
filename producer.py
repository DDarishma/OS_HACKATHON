import random
import time
import threading

from logger_util import logger


class Producer(threading.Thread):
    RUNNING = 'RUNNING'
    WAITING = 'WAITING'
    STOPPED = 'STOPPED'

    def __init__(self, shared_buffer, ui=None, sleep_time=0.7, producer_id=1):
        super().__init__(name=f'Producer-{producer_id}', daemon=True)
        self.buffer = shared_buffer
        self.ui = ui
        self.sleep_time = sleep_time
        self.state = self.STOPPED
        self._running = threading.Event()

    def run(self):
        self.state = self.RUNNING
        self._running.set()

        while self._running.is_set():
            try:
                self.state = self.RUNNING
                value = random.randint(1, 100)

                self.buffer.add_item(value)

                # Log in console/logger
                logger.log(f"{self.name} produced: {value}")

                # Update UI only if UI exists
                if self.ui:
                    self.ui.update_log(produced=value, action='produce')

                sleep_time = random.uniform(self.sleep_time * 0.5, self.sleep_time * 1.5)
                self.state = self.WAITING
                time.sleep(sleep_time)

            except Exception as e:
                logger.log(f"{self.name} error: {e}")

        self.state = self.STOPPED

    def stop(self):
        self._running.clear()
        self.state = self.STOPPED