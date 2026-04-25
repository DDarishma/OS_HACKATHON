import threading


class SharedBuffer:
    def __init__(self, maxsize=10):
        self.maxsize = maxsize
        self.buffer = []
        self.lock = threading.Lock()
        self.items = threading.Semaphore(0)
        self.spaces = threading.Semaphore(maxsize)

    def add_item(self, item, timeout=None):
        """Add item to buffer; wait if full."""
        # Wait for at least one free slot, or timeout
        acquired = self.spaces.acquire(timeout=timeout)
        if not acquired:
            raise BufferError("Buffer is full")

        with self.lock:
            self.buffer.append(item)

        self.items.release()

    def remove_item(self, timeout=None):
        """Remove item from buffer; wait if empty."""
        # Wait for at least one item, or timeout
        acquired = self.items.acquire(timeout=timeout)
        if not acquired:
            raise BufferError("Buffer is empty")

        with self.lock:
            item = self.buffer.pop(0)

        self.spaces.release()
        return item

    def get_buffer_snapshot(self):
        """Return a snapshot copy of current buffer content."""
        with self.lock:
            return list(self.buffer)

    def size(self):
        with self.lock:
            return len(self.buffer)
