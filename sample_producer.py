import threading
import queue
import time
from runze_valve import RunzeValve


class SampleProducer:
    def __init__(self, sample_queue, stop_event, number=4, duration=100, delay=50):
        self.number = number
        self.duration = duration
        self.delay = delay
        self.sample_queue = sample_queue
        self.stop_event = stop_event
        self.valve = RunzeValve(com_port='COM8', address=0, num_port=10)
        self.producer_thread = threading.Thread(target=self.run, daemon=True)

    def start(self):
        self.producer_thread.start()

    def stop(self):
        self.stop_event.set()
        self.producer_thread.join()

    def run(self):
        for count in range(1, self.number + 1):
            if self.stop_event.is_set():
                break
            self.valve.set_current_port(count + 1)
            time.sleep(self.delay)  # time for sample to flow
            sample = f"{count}"
            print(f"Sample {sample} is ready to collect!")
            self.sample_queue.put(sample)
            time.sleep(self.duration)