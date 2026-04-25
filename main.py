import time
from shared_buffer import SharedBuffer
from producer import Producer
from consumer import Consumer
from logger_util import logger


def main():
    buffer = SharedBuffer(maxsize=5)

    # Create producers and consumers with unique IDs
    producers = [
        Producer(buffer, ui=None, min_sleep=0.2, max_sleep=0.5, producer_id=i + 1)
        for i in range(2)
    ]

    consumers = [
        Consumer(buffer, ui=None, min_sleep=0.3, max_sleep=0.6, consumer_id=i + 1)
        for i in range(2)
    ]

    # Start all threads
    for p in producers:
        p.start()

    for c in consumers:
        c.start()

    run_time = 10
    start = time.time()

    try:
        while time.time() - start < run_time:
            time.sleep(1)
            snapshot = buffer.get_buffer_snapshot()
            print(f"\nBuffer ({len(snapshot)}/{buffer.maxsize}): {snapshot}")
            print("Recent log entries:")
            for entry in logger.get_recent(5):
                print("  ", entry)
            print("-----")

    except KeyboardInterrupt:
        print("\nStopping simulation...")

    finally:
        # Stop all threads
        for p in producers:
            p.stop()

        for c in consumers:
            c.stop()

        # Wait for threads to finish
        for p in producers:
            p.join(timeout=1)

        for c in consumers:
            c.join(timeout=1)

        print("\nFinal buffer:", buffer.get_buffer_snapshot())
        print("Simulation complete.")


if __name__ == '__main__':
    main()